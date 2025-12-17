#!/usr/bin/env python3
"""
使用 MuJoCo 验证 Crocoddyl 优化的轨迹。

将 Crocoddyl 计算的关节角度作为目标，让 MuJoCo 的位置控制器跟踪，
验证轨迹在物理引擎下的稳定性。
"""

import argparse
import os
import sys
import time

import numpy as np
import pinocchio as pin


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MJCF_PATH = os.path.join(SCRIPT_DIR, "description/urdf/wbot_v2.xml")
TRAJ_FILE = os.path.join(SCRIPT_DIR, "wbot_trajectory.npz")


def load_trajectory(path: str):
    """加载优化得到的轨迹文件。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"未找到轨迹文件: {path}")

    data = np.load(path)
    xs = data["xs"]
    dt = float(data["dt"])

    print(f"轨迹信息:")
    print(f"  - 文件: {os.path.basename(path)}")
    print(f"  - 状态维度 (xs): {xs.shape}")
    print(f"  - 时间步长: {dt:.4f}s")
    print(f"  - 总时长: {(len(xs)-1)*dt:.3f}s")

    return xs, dt


def build_robot():
    """加载机器人模型。"""
    print(f"\n加载机器人模型:")
    print(f"  - MJCF: {os.path.basename(MJCF_PATH)}")

    try:
        model, collision_model, visual_model = pin.buildModelsFromMJCF(MJCF_PATH)
        robot = pin.RobotWrapper(model, collision_model, visual_model)

        print(f"  ✓ 模型加载成功")
        print(f"    - nq: {robot.model.nq}, nv: {robot.model.nv}")
        print(f"    - 质量: {pin.computeTotalMass(robot.model):.2f} kg")

        return robot

    except Exception as e:
        print(f"  ✗ 加载失败: {e}", file=sys.stderr)
        raise


def extract_configurations(xs: np.ndarray, robot: pin.RobotWrapper) -> np.ndarray:
    """从状态向量中提取配置 q 序列。"""
    nq = robot.model.nq
    if xs.shape[1] < nq:
        raise ValueError(f"状态维度 {xs.shape[1]} 小于 nq={nq}")

    qs = xs[:, :nq].copy()

    # 规范化四元数
    for i in range(len(qs)):
        qs[i] = pin.normalize(robot.model, qs[i])

    print(f"\n配置序列:")
    print(f"  - 帧数: {len(qs)}")
    print(f"  - 配置维度 (nq): {nq}")

    return qs


def playback_with_position_control(
    model_path: str,
    qs: np.ndarray,
    dt: float,
    rate: float = 1.0,
    repeat: bool = True,
):
    """使用位置控制在 MuJoCo 中播放轨迹。

    让 MuJoCo 的位置控制器跟踪 Crocoddyl 的关节角度轨迹。
    """
    try:
        import mujoco
        import mujoco.viewer
    except ImportError as exc:
        raise ImportError(
            "找不到 MuJoCo，可通过 `pip install mujoco` 安装"
        ) from exc

    print(f"\n初始化 MuJoCo 可视化:")

    # 加载 MuJoCo 模型
    model = mujoco.MjModel.from_xml_path(model_path)
    data = mujoco.MjData(model)

    print(f"  ✓ MuJoCo 模型加载成功")
    print(f"    - nq: {model.nq}, nv: {model.nv}")
    print(f"    - nu: {model.nu}")
    print(f"    - 时间步长: {model.opt.timestep:.4f}s")

    sleep_dt = max(dt / max(rate, 1e-6), 1e-4)

    print(f"\n开始轨迹播放:")
    print(f"  - 配置帧数: {len(qs)}")
    print(f"  - 时间步长: {dt:.4f}s")
    print(f"  - 播放速度: {rate:.2f}x")
    print(f"  - 循环播放: {'是' if repeat else '否'}")
    print(f"\n提示: 按 Ctrl+C 停止播放，或关闭 MuJoCo 窗口\n")

    # 状态变量
    frame_idx = [0]
    is_paused = [False]

    def reset_simulation():
        """重置到初始配置。"""
        data.qpos[:] = qs[0]
        data.qvel[:] = 0
        mujoco.mj_forward(model, data)
        frame_idx[0] = 0

    def update_control():
        """更新控制 - 设置目标关节角度给位置控制器。"""
        if is_paused[0]:
            return

        if frame_idx[0] < len(qs):
            # 从 Crocoddyl 的配置中提取关节角度作为控制目标
            # qs[i]: [base_pos(3), base_quat(4), joints(11)]
            # MuJoCo 的 7 个 actuators 对应关节:
            #   [9:16] = right, left, ankle, knee, hip, waist_roll, waist_yaw
            data.ctrl[:] = qs[frame_idx[0]][9:16]

            frame_idx[0] += 1
        else:
            if repeat:
                reset_simulation()
            else:
                is_paused[0] = True

    # 启动交互式查看器
    try:
        reset_simulation()

        with mujoco.viewer.launch_passive(model, data, key_callback=None) as viewer:
            viewer.sync()

            loop_count = 0
            while viewer.is_running():
                step_start = time.time()

                if not is_paused[0]:
                    # 更新控制目标
                    update_control()

                    # 执行物理步进 - MuJoCo 的位置控制器会跟踪 ctrl 的目标
                    mujoco.mj_step(model, data)

                    viewer.sync()

                    # 打印进度
                    if frame_idx[0] > 0 and frame_idx[0] % 10 == 0:
                        progress = frame_idx[0] / len(qs) * 100
                        print(f"\r  循环 #{loop_count+1} - 进度: {progress:.1f}% ({frame_idx[0]}/{len(qs)})", end="")

                    # 检查是否完成一轮
                    if frame_idx[0] == 0 and loop_count > 0:
                        print()  # 换行
                    elif frame_idx[0] >= len(qs):
                        if repeat:
                            loop_count += 1
                            print()
                        else:
                            print("\n  播放完成")
                            break

                # 控制播放速度
                elapsed = time.time() - step_start
                if elapsed < sleep_dt:
                    time.sleep(sleep_dt - elapsed)

    except KeyboardInterrupt:
        print("\n\n  播放已停止")


def main():
    parser = argparse.ArgumentParser(
        description="使用 MuJoCo 验证 Crocoddyl 优化的轨迹",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 默认播放（循环）
  %(prog)s --rate 0.5               # 慢速播放（0.5倍速）
  %(prog)s --once                   # 播放一遍后退出

说明:
  此脚本直接设置 Crocoddyl 计算的关节角度到 MuJoCo，
  用于可视化验证轨迹的合理性。
        """,
    )
    parser.add_argument(
        "--trajectory",
        type=str,
        default=TRAJ_FILE,
        help="轨迹文件 (.npz)，默认使用 wbot_trajectory.npz",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="播放速度倍率（>1 加速，<1 减速）",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只播放一遍，不循环",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Wbot MuJoCo 轨迹验证".center(60))
    print("=" * 60)

    try:
        # 1. 加载轨迹
        xs, dt = load_trajectory(args.trajectory)

        # 2. 加载机器人模型
        robot = build_robot()

        # 3. 提取配置序列
        qs = extract_configurations(xs, robot)

        # 4. 使用 MuJoCo 播放
        playback_with_position_control(
            MJCF_PATH,
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
