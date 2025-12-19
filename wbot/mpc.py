#!/usr/bin/env python3
"""
Wbot MPC 控制器

实现真正的模型预测控制（MPC）：
- 每个时间步求解一个 OCP
- 只执行第一个控制输入
- 基于新状态重新规划
"""

import argparse
import numpy as np
import pinocchio as pin
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Callable
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ocp import WbotOCP, WbotOCPConfig
from trajectory_generator import ExponentialTrajectory, RateLimitedTrajectory, AdaptiveTrajectory


class WbotMPCConfig:
    """MPC 配置参数"""

    def __init__(self):
        # === MPC 参数 ===
        self.horizon_steps = 20      # MPC 时域步数（预测未来多少步）
        self.total_steps = 500       # 总仿真步数
        self.control_dt = 0.01       # 控制周期 (s)

        # === 目标参数 ===
        self.target_vx = 1.0           # 目标前进速度 (m/s)
        self.target_omega_z = 0.0      # 目标转向角速度 (rad/s)

        # === 关节目标 ===
        self.knee_target = -1.2        # knee 最终目标角度

        # === 参考轨迹生成器配置 ===
        self.trajectory_type = 'exponential'  # 'exponential', 'rate_limited', 'adaptive', 'constant'

        # Exponential 参数
        self.time_constant = 1.0       # 时间常数（秒），越小收敛越快

        # RateLimited 参数
        self.max_velocity = 0.5        # 最大速度（rad/s）

        # Adaptive 参数
        self.adaptive_gain = 2.0       # 增益系数
        self.adaptive_deadband = 0.01  # 死区

        # === 基础关节目标 ===
        self.base_target_angles = {
            'waist_roll': 0.0,
            'waist_yaw': 0.0,
            'right_arm_pitch': 0.0,
            'left_arm_pitch': 0.0,
        }

        # === 求解参数 ===
        self.max_iter = 20           # 每次 OCP 的最大迭代次数
        self.use_warm_start = True    # 是否使用热启动
        self.shift_initialization = True  # 是否使用轨迹平移初始化


class WbotMPC:
    """Wbot 机器人 MPC 控制器"""

    def __init__(self, mjcf_path: str,
                 mpc_config: Optional[WbotMPCConfig] = None,
                 ocp_config: Optional[WbotOCPConfig] = None):
        """
        初始化 MPC 控制器

        参数:
            mjcf_path: MuJoCo XML 模型文件路径
            mpc_config: MPC 配置，如果为 None 则使用默认配置
            ocp_config: OCP 配置，如果为 None 则使用默认配置
        """
        self.mjcf_path = mjcf_path
        self.mpc_config = mpc_config if mpc_config is not None else WbotMPCConfig()
        self.ocp_config = ocp_config if ocp_config is not None else WbotOCPConfig()

        # 创建 OCP 求解器
        self.ocp_solver = WbotOCP(mjcf_path, self.ocp_config)

        # 历史记录
        self.state_history = []       # 状态历史
        self.control_history = []     # 控制历史
        self.solve_times = []         # 每次求解时间
        self.iterations = []          # 每次迭代次数
        self.costs = []               # 每次代价

        # 热启动缓存
        self.xs_prev = None
        self.us_prev = None

        # 创建参考轨迹生成器
        self.trajectory_generator = self._create_trajectory_generator()

        print(f"\n✓ WbotMPC 初始化完成")
        print(f"  MPC时域: {self.mpc_config.horizon_steps}步")
        print(f"  总步数: {self.mpc_config.total_steps}步")
        print(f"  控制周期: {self.mpc_config.control_dt}s")
        print(f"  总时长: {self.mpc_config.total_steps * self.mpc_config.control_dt:.1f}s")
        print(f"\n  目标:")
        print(f"    knee: {self.mpc_config.knee_target:.4f} rad ({np.degrees(self.mpc_config.knee_target):.1f}°)")
        print(f"\n  参考轨迹:")
        print(f"    类型: {self.mpc_config.trajectory_type}")
        if self.mpc_config.trajectory_type == 'exponential':
            print(f"    时间常数: {self.mpc_config.time_constant}s")
        elif self.mpc_config.trajectory_type == 'rate_limited':
            print(f"    最大速度: {self.mpc_config.max_velocity} rad/s")
        elif self.mpc_config.trajectory_type == 'adaptive':
            print(f"    增益: {self.mpc_config.adaptive_gain}")

    def _create_trajectory_generator(self):
        """创建轨迹生成器"""
        if self.mpc_config.trajectory_type == 'exponential':
            return ExponentialTrajectory(
                target=self.mpc_config.knee_target,
                dt=self.mpc_config.control_dt,
                time_constant=self.mpc_config.time_constant
            )
        elif self.mpc_config.trajectory_type == 'rate_limited':
            return RateLimitedTrajectory(
                target=self.mpc_config.knee_target,
                dt=self.mpc_config.control_dt,
                max_velocity=self.mpc_config.max_velocity
            )
        elif self.mpc_config.trajectory_type == 'adaptive':
            return AdaptiveTrajectory(
                target=self.mpc_config.knee_target,
                dt=self.mpc_config.control_dt,
                gain=self.mpc_config.adaptive_gain,
                deadband=self.mpc_config.adaptive_deadband
            )
        else:  # 'constant'
            return None

    def get_target_joint_angles(self, step: int, current_state: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        获取当前时间步的目标关节角度

        参数:
            step: 当前时间步
            current_state: 当前状态（用于轨迹生成器）

        返回:
            目标关节角度字典
        """
        target_angles = self.mpc_config.base_target_angles.copy()

        if self.trajectory_generator is None:
            # 固定目标
            knee_ref = self.mpc_config.knee_target
        else:
            # 使用轨迹生成器
            if step == 0 and current_state is not None:
                # 第一步：初始化轨迹生成器
                knee_q_idx = self.ocp_solver.joint_indices['knee'][0]
                if knee_q_idx is not None:
                    current_knee = current_state[knee_q_idx]
                    self.trajectory_generator.reset(current_knee)

            knee_ref = self.trajectory_generator.update()

        target_angles['knee'] = knee_ref
        return target_angles

    def shift_trajectory(self, trajectory: np.ndarray, fill_last: bool = True) -> List:
        """
        平移轨迹（用于热启动）

        参数:
            trajectory: 原始轨迹 (N, dim)
            fill_last: 是否用最后一个值填充

        返回:
            平移后的轨迹列表
        """
        shifted = list(trajectory[1:])  # 去掉第一个
        if fill_last:
            shifted.append(trajectory[-1])  # 用最后一个填充
        return shifted

    def run_open_loop(self, verbose: bool = False) -> Dict:
        """
        运行开环 MPC（使用 OCP 预测的状态，不考虑模型误差）

        这个版本用于测试 MPC 框架，假设状态完美跟踪预测。
        后续可以扩展为闭环版本，接入真实仿真器。

        参数:
            verbose: 是否显示详细信息

        返回:
            统计信息字典
        """
        print(f"\n{'='*70}")
        print("开始 MPC 开环仿真")
        print(f"{'='*70}\n")

        total_start_time = time.time()

        # 初始状态
        x_current = self.ocp_solver.get_initial_state()

        # MPC 主循环
        for step in range(self.mpc_config.total_steps):
            step_start_time = time.time()

            # 获取当前目标（传入当前状态用于轨迹生成）
            target_angles = self.get_target_joint_angles(step, x_current)

            # 准备热启动
            warm_start = None
            if self.mpc_config.use_warm_start and self.xs_prev is not None:
                if self.mpc_config.shift_initialization:
                    # 使用平移的轨迹
                    warm_start = (
                        self.shift_trajectory(self.xs_prev),
                        self.shift_trajectory(self.us_prev)
                    )
                else:
                    # 直接使用上次的解
                    warm_start = (list(self.xs_prev), list(self.us_prev))

            # 求解 OCP（从当前状态规划未来 horizon_steps 步）
            result = self.ocp_solver.solve(
                x0=x_current,
                target_joint_angles=target_angles,
                target_vx=self.mpc_config.target_vx,
                target_omega_z=self.mpc_config.target_omega_z,
                horizon_steps=self.mpc_config.horizon_steps,
                max_iter=self.mpc_config.max_iter,
                warm_start=warm_start,
                verbose=verbose
            )

            # *** MPC 核心：只取第一个控制输入 ***
            u_apply = result['us'][0]

            # 开环仿真：使用 OCP 预测的下一个状态
            # （假设模型完美，实际应该是物理仿真器返回的状态）
            x_next = result['xs'][1]

            # 保存历史
            self.state_history.append(x_current.copy())
            self.control_history.append(u_apply.copy())
            self.solve_times.append(result['solve_time'])
            self.iterations.append(result['iter'])
            self.costs.append(result['cost'])

            # 更新状态
            x_current = x_next

            # 保存用于下次热启动
            self.xs_prev = result['xs']
            self.us_prev = result['us']

            # 打印进度
            if (step + 1) % 50 == 0 or step == 0:
                elapsed = time.time() - total_start_time
                progress = (step + 1) / self.mpc_config.total_steps * 100
                avg_solve_time = np.mean(self.solve_times[-50:]) if len(self.solve_times) >= 50 else np.mean(self.solve_times)
                eta = avg_solve_time * (self.mpc_config.total_steps - step - 1)

                print(f"[步骤 {step+1:4d}/{self.mpc_config.total_steps}] "
                      f"进度: {progress:5.1f}% | "
                      f"求解: {result['solve_time']*1000:5.1f}ms | "
                      f"迭代: {result['iter']:3d} | "
                      f"代价: {result['cost']:8.2f} | "
                      f"预计剩余: {eta:.1f}s")

        total_time = time.time() - total_start_time

        # 打印统计
        stats = self._print_statistics(total_time)

        return stats

    def run_closed_loop(self, simulator_step_fn: Callable, verbose: bool = False) -> Dict:
        """
        运行闭环 MPC（使用真实仿真器）

        参数:
            simulator_step_fn: 仿真器步进函数 fn(x, u) -> x_next
            verbose: 是否显示详细信息

        返回:
            统计信息字典
        """
        print(f"\n{'='*70}")
        print("开始 MPC 闭环仿真")
        print(f"{'='*70}\n")

        total_start_time = time.time()

        # 初始状态
        x_current = self.ocp_solver.get_initial_state()

        # MPC 主循环
        for step in range(self.mpc_config.total_steps):
            step_start_time = time.time()

            # 获取当前目标（传入当前状态用于轨迹生成）
            target_angles = self.get_target_joint_angles(step, x_current)

            # 准备热启动
            warm_start = None
            if self.mpc_config.use_warm_start and self.xs_prev is not None:
                if self.mpc_config.shift_initialization:
                    warm_start = (
                        self.shift_trajectory(self.xs_prev),
                        self.shift_trajectory(self.us_prev)
                    )
                else:
                    warm_start = (list(self.xs_prev), list(self.us_prev))

            # 求解 OCP
            result = self.ocp_solver.solve(
                x0=x_current,
                target_joint_angles=target_angles,
                target_vx=self.mpc_config.target_vx,
                target_omega_z=self.mpc_config.target_omega_z,
                horizon_steps=self.mpc_config.horizon_steps,
                max_iter=self.mpc_config.max_iter,
                warm_start=warm_start,
                verbose=verbose
            )

            # 只取第一个控制输入
            u_apply = result['us'][0]

            # *** 闭环核心：使用仿真器返回真实状态（可能有扰动、模型误差）***
            x_next = simulator_step_fn(x_current, u_apply)

            # 保存历史
            self.state_history.append(x_current.copy())
            self.control_history.append(u_apply.copy())
            self.solve_times.append(result['solve_time'])
            self.iterations.append(result['iter'])
            self.costs.append(result['cost'])

            # 更新状态
            x_current = x_next

            # 保存用于下次热启动
            self.xs_prev = result['xs']
            self.us_prev = result['us']

            # 打印进度
            if (step + 1) % 50 == 0 or step == 0:
                elapsed = time.time() - total_start_time
                progress = (step + 1) / self.mpc_config.total_steps * 100
                avg_solve_time = np.mean(self.solve_times[-50:]) if len(self.solve_times) >= 50 else np.mean(self.solve_times)
                eta = avg_solve_time * (self.mpc_config.total_steps - step - 1)

                print(f"[步骤 {step+1:4d}/{self.mpc_config.total_steps}] "
                      f"进度: {progress:5.1f}% | "
                      f"求解: {result['solve_time']*1000:5.1f}ms | "
                      f"迭代: {result['iter']:3d} | "
                      f"代价: {result['cost']:8.2f} | "
                      f"预计剩余: {eta:.1f}s")

        total_time = time.time() - total_start_time

        # 打印统计
        stats = self._print_statistics(total_time)

        return stats

    def _print_statistics(self, total_time: float) -> Dict:
        """打印统计信息"""
        print(f"\n{'='*70}")
        print(f"MPC 仿真完成!")
        print(f"{'='*70}")

        solve_times_arr = np.array(self.solve_times)
        iterations_arr = np.array(self.iterations)
        costs_arr = np.array(self.costs)

        print(f"\n⏱️  时间统计:")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.1f}分钟)")
        print(f"  平均每步: {total_time/self.mpc_config.total_steps*1000:.1f}ms")
        print(f"  平均求解: {solve_times_arr.mean()*1000:.1f}ms")
        print(f"  最快求解: {solve_times_arr.min()*1000:.1f}ms")
        print(f"  最慢求解: {solve_times_arr.max()*1000:.1f}ms")
        print(f"  求解标准差: {solve_times_arr.std()*1000:.1f}ms")

        print(f"\n🔄 迭代统计:")
        print(f"  总迭代: {sum(self.iterations)}")
        print(f"  平均每步: {iterations_arr.mean():.1f}次")
        print(f"  最少迭代: {iterations_arr.min()}次")
        print(f"  最多迭代: {iterations_arr.max()}次")

        print(f"\n💰 代价统计:")
        print(f"  最终代价: {costs_arr[-1]:.2f}")
        print(f"  平均代价: {costs_arr.mean():.2f}")
        print(f"  最小代价: {costs_arr.min():.2f}")
        print(f"  最大代价: {costs_arr.max():.2f}")

        # 实时性分析
        real_time_ratio = solve_times_arr.mean() / self.mpc_config.control_dt
        print(f"\n⚡ 实时性分析:")
        print(f"  控制周期: {self.mpc_config.control_dt*1000:.1f}ms")
        print(f"  平均求解时间: {solve_times_arr.mean()*1000:.1f}ms")
        print(f"  实时性比率: {real_time_ratio:.2%}")
        if real_time_ratio < 1.0:
            print(f"  ✓ 可以实时运行（求解时间 < 控制周期）")
        else:
            print(f"  ✗ 无法实时运行（求解时间 > 控制周期）")

        print(f"\n{'='*70}\n")

        return {
            'total_time': total_time,
            'solve_times': solve_times_arr,
            'iterations': iterations_arr,
            'costs': costs_arr,
            'real_time_ratio': real_time_ratio
        }

    def get_trajectory(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取完整轨迹

        返回:
            (xs, us): 状态和控制轨迹
        """
        xs = np.array(self.state_history)
        us = np.array(self.control_history)
        return xs, us

    def save_trajectory(self, save_path: str):
        """保存轨迹"""
        xs, us = self.get_trajectory()

        # 提取关节数据
        joint_names = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']
        joint_data = {}

        for joint_name in joint_names:
            if self.ocp_solver.model.existJointName(joint_name):
                joint_id = self.ocp_solver.model.getJointId(joint_name)
                joint_q_idx = self.ocp_solver.model.joints[joint_id].idx_q
                joint_v_idx = self.ocp_solver.model.joints[joint_id].idx_v
                joint_positions = xs[:, joint_q_idx]
                joint_velocities = xs[:, self.ocp_solver.state.nq + joint_v_idx]
                joint_data[f'{joint_name}_position'] = joint_positions
                joint_data[f'{joint_name}_velocity'] = joint_velocities

        # 保存
        np.savez(save_path,
                 xs=xs,
                 us=us,
                 dt=self.mpc_config.control_dt,
                 solve_times=np.array(self.solve_times),
                 iterations=np.array(self.iterations),
                 costs=np.array(self.costs),
                 **joint_data)

        print(f"\n✓ MPC 轨迹已保存: {save_path}")

    def plot_mpc_analysis(self, save_path: str):
        """绘制 MPC 性能分析图表"""
        if len(self.solve_times) == 0:
            print("⚠️  没有数据可绘制")
            return

        print(f"\n{'='*70}")
        print("生成 MPC 性能分析图表".center(70))
        print(f"{'='*70}")

        time_steps = np.arange(len(self.solve_times)) * self.mpc_config.control_dt

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('MPC Performance Analysis', fontsize=16, fontweight='bold')

        # 求解时间
        ax = axes[0, 0]
        ax.plot(time_steps, np.array(self.solve_times) * 1000, 'b-', linewidth=1.5)
        ax.axhline(y=self.mpc_config.control_dt * 1000, color='r', linestyle='--',
                   linewidth=2, label=f'Control Period ({self.mpc_config.control_dt*1000:.1f}ms)')
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Solve Time (ms)', fontsize=11, fontweight='bold')
        ax.set_title('OCP Solve Time per Step', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # 迭代次数
        ax = axes[0, 1]
        ax.plot(time_steps, self.iterations, 'g-', linewidth=1.5)
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Iterations', fontsize=11, fontweight='bold')
        ax.set_title('Solver Iterations per Step', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 代价函数
        ax = axes[1, 0]
        ax.plot(time_steps, self.costs, 'm-', linewidth=1.5)
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Cost', fontsize=11, fontweight='bold')
        ax.set_title('Cost Function Value', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 实时性分析（滚动窗口）
        ax = axes[1, 1]
        window_size = 50
        real_time_ratios = []
        for i in range(len(self.solve_times)):
            start = max(0, i - window_size + 1)
            window_mean = np.mean(self.solve_times[start:i+1])
            real_time_ratios.append(window_mean / self.mpc_config.control_dt)

        ax.plot(time_steps, real_time_ratios, 'r-', linewidth=1.5)
        ax.axhline(y=1.0, color='k', linestyle='--', linewidth=2, label='Real-time Threshold')
        ax.set_xlabel('Time (s)', fontsize=11)
        ax.set_ylabel('Real-time Ratio', fontsize=11, fontweight='bold')
        ax.set_title(f'Real-time Performance (Window={window_size})', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\n✓ MPC 性能分析图表已保存: {save_path}")
        plt.close()

    def playback(self, rate: float = 1.0, repeat: bool = True):
        """使用 MuJoCo 播放 MPC 轨迹"""
        xs, us = self.get_trajectory()

        if len(xs) == 0:
            print("⚠️  没有可播放的轨迹")
            return

        try:
            import mujoco
            import mujoco.viewer
        except ImportError:
            print("\n⚠️  未安装 MuJoCo，跳过可视化")
            return

        print(f"\n{'='*70}")
        print("MuJoCo 可视化播放".center(70))
        print(f"{'='*70}")

        # 提取配置序列
        nq = self.ocp_solver.model.nq
        qs = xs[:, :nq].copy()

        # 规范化四元数
        for i in range(len(qs)):
            qs[i] = pin.normalize(self.ocp_solver.model, qs[i])

        # 加载 MuJoCo 模型
        model = mujoco.MjModel.from_xml_path(self.mjcf_path)
        data = mujoco.MjData(model)

        print(f"\n✓ MuJoCo 模型加载成功")
        print(f"  - 帧数: {len(qs)}")

        sleep_dt = max(self.mpc_config.control_dt / max(rate, 1e-6), 1e-4)

        frame_idx = [0]
        is_paused = [False]

        def reset_simulation():
            data.qpos[:] = qs[0]
            data.qvel[:] = 0
            data.ctrl[:] = 0
            data.act[:] = 0
            mujoco.mj_forward(model, data)
            frame_idx[0] = 0

        def update_control():
            if is_paused[0]:
                return
            if frame_idx[0] < len(qs):
                data.ctrl[:] = qs[frame_idx[0]][9:16]
                frame_idx[0] += 1
            else:
                if repeat:
                    reset_simulation()
                else:
                    is_paused[0] = True

        try:
            reset_simulation()
            with mujoco.viewer.launch_passive(model, data, key_callback=None) as viewer:
                viewer.sync()
                loop_count = 0
                while viewer.is_running():
                    step_start = time.time()
                    if not is_paused[0]:
                        update_control()
                        mujoco.mj_step(model, data)
                        viewer.sync()

                        if frame_idx[0] > 0 and frame_idx[0] % 50 == 0:
                            progress = frame_idx[0] / len(qs) * 100
                            print(f"\r  循环 #{loop_count+1} - 进度: {progress:.1f}%", end="")

                        if frame_idx[0] >= len(qs):
                            if repeat:
                                loop_count += 1
                                print()
                            else:
                                print("\n  播放完成")
                                break

                    elapsed = time.time() - step_start
                    if elapsed < sleep_dt:
                        time.sleep(sleep_dt - elapsed)

        except KeyboardInterrupt:
            print("\n\n  播放已停止")


def main():
    parser = argparse.ArgumentParser(
        description="Wbot MPC 控制器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                     # 默认：500步，horizon=50
  %(prog)s --steps 1000        # 运行1000步
  %(prog)s --horizon 30        # 使用30步时域
  %(prog)s --no-warm-start     # 不使用热启动
        """,
    )
    parser.add_argument("--steps", type=int, default=500, help="总仿真步数")
    parser.add_argument("--horizon", type=int, default=20, help="MPC时域步数")
    parser.add_argument("--knee-target", type=float, default=-1.2, help="knee目标角度(rad)")
    parser.add_argument("--no-warm-start", action="store_true", help="不使用热启动")
    parser.add_argument("--no-shift", action="store_true", help="热启动不使用轨迹平移")
    parser.add_argument("--no-playback", action="store_true", help="不启动播放")
    parser.add_argument("--rate", type=float, default=1.0, help="播放速度")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    mjcf_path = os.path.join(script_dir, "description/urdf/wbot_v2.xml")

    try:
        # 配置
        mpc_config = WbotMPCConfig()
        mpc_config.total_steps = args.steps
        mpc_config.horizon_steps = args.horizon
        mpc_config.knee_target = args.knee_target
        mpc_config.use_warm_start = not args.no_warm_start
        mpc_config.shift_initialization = not args.no_shift

        # 创建 MPC 控制器
        mpc = WbotMPC(mjcf_path, mpc_config)

        # 运行开环仿真
        stats = mpc.run_open_loop(verbose=False)

        # 保存轨迹
        save_path = os.path.join(script_dir, 'wbot_trajectory_mpc.npz')
        mpc.save_trajectory(save_path)

        # 绘制性能分析
        plot_path = os.path.join(script_dir, 'mpc_performance.png')
        mpc.plot_mpc_analysis(plot_path)

        # 播放
        if not args.no_playback:
            mpc.playback(rate=args.rate, repeat=False)
        else:
            print("\n✓ 跳过播放（--no-playback）")

    except KeyboardInterrupt:
        print("\n\n程序已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
