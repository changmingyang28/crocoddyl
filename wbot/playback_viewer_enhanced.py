#!/usr/bin/env python3
"""
将 wbot_trajectory.npz 中的最优轨迹在 3D 视图中播放。

增强版：添加了更多诊断信息和错误处理
"""

import argparse
import os
import sys
import time
from typing import Iterable

import numpy as np
import pinocchio as pin
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MJCF_PATH = os.path.join(SCRIPT_DIR, "description/urdf/wbot_v2.xml")
MESH_DIR = os.path.join(SCRIPT_DIR, "description/dae")
TRAJ_FILE = os.path.join(SCRIPT_DIR, "wbot_trajectory.npz")


def load_trajectory(path: str):
    """加载优化得到的轨迹文件。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到轨迹文件: {path}")

    data = np.load(path)
    xs = data["xs"]
    dt = float(data["dt"])

    # 打印轨迹信息
    print(f"轨迹信息:")
    print(f"  - 文件: {os.path.basename(path)}")
    print(f"  - 状态维度: {xs.shape}")
    print(f"  - 时间步长: {dt:.4f}s")
    print(f"  - 总时长: {(len(xs)-1)*dt:.3f}s")

    return xs, dt


def build_robot_with_visuals():
    """加载包含视觉模型的机器人。"""
    package_dirs = [
        MESH_DIR,  # 视觉网格
        os.path.join(SCRIPT_DIR, "description"),  # 相对路径回退
        SCRIPT_DIR,
    ]

    # v2 URDF 使用 STL 文件，不需要检查 DAE
    # 检查 STL mesh 是否存在
    base_mesh_stl = os.path.join(SCRIPT_DIR, "description/meshes/base_link_1211_evt2.STL")
    if not os.path.exists(base_mesh_stl):
        print(f"  ⚠️  警告: STL mesh 文件未找到，将只加载几何模型")
        print(f"     预期路径: {base_mesh_stl}")

    print(f"\n加载机器人模型:")
    print(f"  - MJCF: {os.path.basename(MJCF_PATH)}")

    try:
        # 使用 MuJoCo XML 加载（包含 visual 和 collision models）
        # MJCF 不需要 package_dirs，mesh 路径在 XML 中已指定
        model, collision_model, visual_model = pin.buildModelsFromMJCF(MJCF_PATH)

        # 创建 RobotWrapper
        robot = pin.RobotWrapper(model, collision_model, visual_model)

        # 打印模型信息
        print(f"  ✓ 模型加载成功")
        print(f"    - nq: {robot.model.nq}, nv: {robot.model.nv}")
        print(f"    - 质量: {pin.computeTotalMass(robot.model):.2f} kg")

        if robot.visual_model:
            print(f"    - 视觉几何体: {len(robot.visual_model.geometryObjects)}")
        if robot.collision_model:
            print(f"    - 碰撞几何体: {len(robot.collision_model.geometryObjects)}")

        return robot

    except Exception as e:
        print(f"  ✗ 加载失败: {e}", file=sys.stderr)
        raise


def create_visualizer(robot: pin.RobotWrapper, viewer: str, open_browser: bool):
    """初始化可视化后端。"""
    print(f"\n初始化可视化器: {viewer}")

    if viewer == "meshcat":
        try:
            from pinocchio.visualize import MeshcatVisualizer
        except ImportError as exc:
            raise ImportError(
                "找不到 Meshcat，可通过 `pip install meshcat` 安装"
            ) from exc

        viz = MeshcatVisualizer(
            robot.model, robot.collision_model, robot.visual_model
        )
        viz.initViewer(open=open_browser)
        viz.loadViewerModel(rootNodeName="wbot")

        try:
            url = viz.viewer.url()
            print(f"  ✓ Meshcat已启动")
            print(f"    URL: {url}")
            if open_browser:
                print(f"    提示: 浏览器应该会自动打开")
        except Exception:
            print(f"  ✓ Meshcat已启动（无法获取URL）")

        return viz

    if viewer == "gepetto":
        try:
            from pinocchio.visualize import GepettoVisualizer
        except ImportError as exc:
            raise ImportError(
                "找不到 Gepetto 可视化绑定，请确认已安装 gepetto-viewer-corba"
            ) from exc

        try:
            viz = GepettoVisualizer(
                robot.model, robot.collision_model, robot.visual_model
            )
            viz.initViewer(loadModel=False)
            viz.loadViewerModel(rootNodeName="wbot")
            print(f"  ✓ Gepetto已连接")
            return viz
        except Exception as e:
            raise RuntimeError(
                f"无法连接到Gepetto服务器: {e}\n"
                f"请先运行 'gepetto-gui' 启动Gepetto Viewer"
            ) from e

    raise ValueError(f"不支持的 viewer: {viewer}")


def add_ground_plane(viz, viewer: str, size=(4.0, 4.0), thickness=0.02):
    """在可视化里添加一块地面。"""
    if viewer == "meshcat":
        try:
            import meshcat.geometry as g
            import meshcat.transformations as tf
        except Exception:
            return

        name = "ground"
        viz.viewer[name].set_object(
            g.Box([size[0], size[1], thickness]),
            g.MeshLambertMaterial(color=0x888888, reflectivity=0.6),
        )
        viz.viewer[name].set_transform(
            tf.translation_matrix([0.0, 0.0, -thickness * 0.5])
        )
        print(f"  ✓ 添加地面平面 ({size[0]}m × {size[1]}m)")
        return

    if viewer == "gepetto":
        try:
            gui = viz.viewer.gui
            name = viz.viewerName + "/ground"
            if not gui.nodeExists(name):
                gui.addBox(name, size[0], size[1], thickness, [0.5, 0.5, 0.5, 1.0])
                gui.applyConfiguration(name, [0, 0, -thickness * 0.5, 0, 0, 0, 1])
                gui.addToGroup(name, viz.viewerName)
                gui.refresh()
                print(f"  ✓ 添加地面平面 ({size[0]}m × {size[1]}m)")
        except Exception as e:
            print(f"  ! 无法添加地面: {e}")


def extract_configurations(xs: np.ndarray, robot: pin.RobotWrapper) -> np.ndarray:
    """从状态向量中取出配置 q 序列。"""
    nq = robot.model.nq
    if xs.shape[1] < nq:
        raise ValueError(f"状态维度 {xs.shape[1]} 小于 nq={nq}")

    qs = xs[:, :nq].copy()

    # 规范化四元数，避免数值误差导致姿态跳变
    for i in range(len(qs)):
        qs[i] = pin.normalize(robot.model, qs[i])

    print(f"\n配置序列:")
    print(f"  - 帧数: {len(qs)}")
    print(f"  - 配置维度 (nq): {nq}")

    return qs


def plot_joint_data(log_file: str, output_file: str = None):
    """Read joint log and plot data.

    Args:
        log_file: Path to joint_log.csv file
        output_file: Output image path, defaults to joint_plots.png
    """
    if not os.path.exists(log_file):
        print(f"Warning: Joint log file not found: {log_file}")
        return

    if output_file is None:
        output_file = os.path.join(os.path.dirname(log_file), 'joint_plots.png')

    # 读取CSV数据
    data = np.genfromtxt(log_file, delimiter=',', names=True, encoding='utf-8')

    # 只分析 ankle 关节
    joint = 'ankle'

    # Create 1x4 subplot grid (1 joint × 4 data types)
    fig, axes = plt.subplots(1, 4, figsize=(20, 4))
    fig.suptitle('Ankle Joint Motion Data Analysis', fontsize=16, fontweight='bold')

    data_types = [
        ('pos(deg)', 'Angle (deg)', 'b-'),
        ('vel(rad/s)', 'Velocity (rad/s)', 'g-'),
        ('acc(rad/s²)', 'Acceleration (rad/s²)', 'r-'),
        ('torque(Nm)', 'Torque (Nm)', 'm-')
    ]

    time = data['times']

    for j, (suffix, ylabel, color) in enumerate(data_types):
        ax = axes[j]

        # Construct column name (numpy.genfromtxt removes special chars)
        # 'pos(deg)' -> 'posdeg', 'vel(rad/s)' -> 'velrads', etc.
        suffix_clean = suffix.replace('(', '').replace(')', '').replace('/', '')
        col_name = f'{joint}_{suffix_clean}'

        try:
            values = data[col_name]
            ax.plot(time, values, color, linewidth=2.0, label=joint)
            ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
            ax.set_xlabel('Time (s)', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=0.8)

            # Add title
            title_map = {
                'pos(deg)': 'Position',
                'vel(rad/s)': 'Velocity',
                'acc(rad/s²)': 'Acceleration',
                'torque(Nm)': 'Torque'
            }
            ax.set_title(f'Ankle {title_map[suffix]}', fontsize=13, fontweight='bold')

        except (KeyError, ValueError) as e:
            ax.text(0.5, 0.5, f'Data unavailable\n{col_name}',
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_ylabel(ylabel, fontsize=12)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Joint data plot saved: {output_file}")
    plt.close()


def playback(
    viz,
    qs: Iterable[np.ndarray],
    dt: float,
    rate: float = 1.0,
    repeat: bool = True,
):
    """按时间播放轨迹。"""
    sleep_dt = max(dt / max(rate, 1e-6), 1e-4)
    segment = list(qs)

    print(f"\n开始播放:")
    print(f"  - 帧数: {len(segment)}")
    print(f"  - 时间步长: {dt:.4f}s")
    print(f"  - 播放速度: {rate:.2f}x")
    print(f"  - 睡眠间隔: {sleep_dt:.4f}s")
    print(f"  - 循环播放: {'是' if repeat else '否'}")
    print(f"\n提示: 按 Ctrl+C 停止播放\n")

    def _loop():
        for i, q in enumerate(segment):
            viz.display(q)
            if i % 10 == 0:  # 每10帧打印一次进度
                progress = (i + 1) / len(segment) * 100
                print(f"\r  进度: {progress:.1f}% ({i+1}/{len(segment)})", end="")
            time.sleep(sleep_dt)
        print()  # 换行

    try:
        if repeat:
            loop_count = 0
            while True:
                loop_count += 1
                print(f"  循环 #{loop_count}")
                _loop()
        else:
            _loop()
            print("  播放完成")
    except KeyboardInterrupt:
        print("\n\n  播放已停止")


def main():
    parser = argparse.ArgumentParser(
        description="在 3D 视图中回放 wbot 最优轨迹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 默认播放（Meshcat）
  %(prog)s --viewer gepetto         # 使用Gepetto
  %(prog)s --rate 0.5               # 慢速播放（0.5倍速）
  %(prog)s --start 10 --end 30      # 只播放第10-30帧
  %(prog)s --once                   # 播放一遍后退出
        """,
    )
    parser.add_argument(
        "--trajectory",
        type=str,
        default=TRAJ_FILE,
        help="轨迹文件 (.npz)，默认使用 wbot_trajectory.npz",
    )
    parser.add_argument(
        "--viewer",
        choices=["meshcat", "gepetto"],
        default="meshcat",
        help="可视化后端（默认 meshcat）",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="播放速度倍率（>1 加速，<1 减速）",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="从第几步开始播放（包含）",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="播放到第几步（不包含）",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只播放一遍，不循环",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Meshcat 时不自动打开浏览器",
    )
    parser.add_argument(
        "--no-ground",
        action="store_true",
        help="不在可视化里添加地面",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate joint data plots (reads joint_log.csv)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Wbot 轨迹 3D 可视化".center(60))
    print("=" * 60)

    try:
        # 1. 加载轨迹
        xs, dt = load_trajectory(args.trajectory)

        # 1.5 生成关节数据图表（如果指定）
        if args.plot:
            log_file = os.path.join(SCRIPT_DIR, 'joint_log.csv')
            plot_joint_data(log_file)

        # 2. 加载机器人
        robot = build_robot_with_visuals()

        # 3. 创建可视化器
        viz = create_visualizer(robot, args.viewer, open_browser=not args.no_browser)

        # 4. 添加地面
        if not args.no_ground:
            add_ground_plane(viz, args.viewer)

        # 5. 提取配置
        qs = extract_configurations(xs, robot)

        # 6. 播放区间
        start = max(args.start, 0)
        end = args.end if args.end is not None else len(qs)
        end = min(end, len(qs))

        if start >= end:
            raise ValueError(f"播放区间无效: start={start}, end={end}")

        if start > 0 or end < len(qs):
            print(f"  播放片段: [{start}, {end}) / {len(qs)}")
            qs = qs[start:end]

        # 7. 开始播放
        playback(
            viz,
            qs,
            dt,
            rate=args.rate,
            repeat=not args.once,
        )

    except KeyboardInterrupt:
        print("\n程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
