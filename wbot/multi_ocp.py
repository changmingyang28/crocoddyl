#!/usr/bin/env python3
"""
多段OCP求解器（重构版）

使用 WbotOCP 类进行多段连续的 OCP 求解，为实现完整 MPC 做准备
"""

import argparse
import numpy as np
import pinocchio as pin
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ocp import WbotOCP, WbotOCPConfig


class MultiOCPConfig:
    """多段 OCP 配置参数"""

    def __init__(self):
        # === 分段参数 ===
        self.n_segments = 20        # 总段数
        self.horizon_steps = 20     # 每段的时域步数

        # === 目标参数 ===
        self.knee_final_target = -1.2  # knee 最终目标角度 (rad)
        self.target_vx = 1.0           # 目标前进速度 (m/s)
        self.target_omega_z = 0.0      # 目标转向角速度 (rad/s)

        # === 基础关节目标 ===
        self.base_target_angles = {
            'waist_roll': 0.0,
            'waist_yaw': 0.0,
            'right_arm_pitch': 0.0,
            'left_arm_pitch': 0.0,
        }

        # === 求解参数 ===
        self.max_iter = 100  # 每段的最大迭代次数


class MultiOCP:
    """多段 OCP 求解器"""

    def __init__(self, mjcf_path: str,
                 multi_config: Optional[MultiOCPConfig] = None,
                 ocp_config: Optional[WbotOCPConfig] = None):
        """
        初始化多段 OCP 求解器

        参数:
            mjcf_path: MuJoCo XML 模型文件路径
            multi_config: 多段 OCP 配置，如果为 None 则使用默认配置
            ocp_config: 单段 OCP 配置，如果为 None 则使用默认配置
        """
        self.mjcf_path = mjcf_path
        self.multi_config = multi_config if multi_config is not None else MultiOCPConfig()
        self.ocp_config = ocp_config if ocp_config is not None else WbotOCPConfig()

        # 创建 OCP 求解器
        self.ocp_solver = WbotOCP(mjcf_path, self.ocp_config)

        # 存储求解结果
        self.all_xs = []
        self.all_us = []
        self.all_costs = []
        self.all_iters = []
        self.segment_times = []

        # 合并后的轨迹
        self.xs_combined = None
        self.us_combined = None

        print(f"\n✓ MultiOCP 初始化完成")
        print(f"  总段数: {self.multi_config.n_segments}")
        print(f"  每段时域: {self.multi_config.horizon_steps}步")
        print(f"  总时长: {self.multi_config.n_segments * self.multi_config.horizon_steps * self.ocp_config.dt:.1f}s")

    def solve_all_segments(self, verbose: bool = False) -> Dict:
        """
        求解所有段的 OCP

        参数:
            verbose: 是否显示详细求解信息

        返回:
            包含求解统计信息的字典
        """
        print(f"\n{'='*70}")
        print("开始多段OCP求解")
        print(f"{'='*70}\n")

        total_start_time = time.time()

        # 初始状态
        x_current = self.ocp_solver.get_initial_state()

        # 循环求解每一段
        for seg in range(self.multi_config.n_segments):
            seg_start_time = time.time()

            # 当前阶段的 knee 目标
            knee_target_current = (self.multi_config.knee_final_target *
                                 (seg + 1) / self.multi_config.n_segments)

            # 合并目标角度
            target_joint_angles = self.multi_config.base_target_angles.copy()
            target_joint_angles['knee'] = knee_target_current

            # 显示进度信息
            self._print_segment_header(seg, knee_target_current, x_current)

            # 准备热启动
            warm_start = None
            if seg > 0:
                # 使用上一段的最终控制作为初始猜测
                warm_start = (
                    [x_current] * (self.multi_config.horizon_steps + 1),
                    [self.all_us[-1][-1]] * self.multi_config.horizon_steps
                )

            # 求解 OCP
            result = self.ocp_solver.solve(
                x0=x_current,
                target_joint_angles=target_joint_angles,
                target_vx=self.multi_config.target_vx,
                target_omega_z=self.multi_config.target_omega_z,
                horizon_steps=self.multi_config.horizon_steps,
                max_iter=self.multi_config.max_iter,
                warm_start=warm_start,
                verbose=verbose
            )

            seg_time = time.time() - seg_start_time

            # 保存结果
            self.all_xs.append(result['xs'])
            self.all_us.append(result['us'])
            self.all_costs.append(result['cost'])
            self.all_iters.append(result['iter'])
            self.segment_times.append(seg_time)

            # 更新当前状态
            x_current = result['xs'][-1].copy()

            # 显示求解结果
            self._print_segment_result(seg, result, seg_time, x_current)

        total_time = time.time() - total_start_time

        # 合并轨迹
        self._combine_trajectories()

        # 打印统计信息
        stats = self._print_statistics(total_time)

        return stats

    def _print_segment_header(self, seg: int, knee_target: float, x_current: np.ndarray):
        """打印段的开始信息"""
        # 估计剩余时间
        eta_str = ""
        if seg > 0:
            avg_time = sum(self.segment_times) / len(self.segment_times)
            remaining_segs = self.multi_config.n_segments - seg
            eta_seconds = avg_time * remaining_segs
            eta_str = f" | 预计剩余: {eta_seconds:.1f}s"

        progress = (seg + 1) / self.multi_config.n_segments * 100
        print(f"【第 {seg+1}/{self.multi_config.n_segments} 段】 ({progress:.1f}%{eta_str})")
        print(f"  knee目标: {knee_target:.4f} rad ({np.degrees(knee_target):.1f}°)")

        # 显示当前 knee 角度
        if self.ocp_solver.model.existJointName('knee'):
            knee_q_idx = self.ocp_solver.model.joints[
                self.ocp_solver.model.getJointId('knee')
            ].idx_q
            print(f"  当前knee: {x_current[knee_q_idx]:.4f} rad ({np.degrees(x_current[knee_q_idx]):.1f}°)")

    def _print_segment_result(self, seg: int, result: Dict, seg_time: float, x_current: np.ndarray):
        """打印段的求解结果"""
        iter_per_sec = result['iter'] / seg_time if seg_time > 0 else 0
        ms_per_iter = seg_time * 1000 / result['iter'] if result['iter'] > 0 else 0

        print(f"  ✓ 完成: 迭代={result['iter']}, 代价={result['cost']:.2f}")
        print(f"    耗时: {seg_time:.2f}s ({ms_per_iter:.1f}ms/iter, {iter_per_sec:.1f}iter/s)")

        # 显示最终 knee 角度
        if self.ocp_solver.model.existJointName('knee'):
            knee_q_idx = self.ocp_solver.model.joints[
                self.ocp_solver.model.getJointId('knee')
            ].idx_q
            print(f"    最终knee: {x_current[knee_q_idx]:.4f} rad ({np.degrees(x_current[knee_q_idx]):.1f}°)")
        print()

    def _combine_trajectories(self):
        """合并所有段的轨迹"""
        self.xs_combined = self.all_xs[0]
        self.us_combined = self.all_us[0]

        for seg in range(1, self.multi_config.n_segments):
            # 跳过第一个点（与上一段的最后一个点重复）
            self.xs_combined = np.vstack([self.xs_combined, self.all_xs[seg][1:]])
            self.us_combined = np.vstack([self.us_combined, self.all_us[seg]])

    def _print_statistics(self, total_time: float) -> Dict:
        """打印统计信息并返回统计字典"""
        print(f"{'='*70}")
        print(f"所有OCP求解完成!")
        print(f"{'='*70}")

        # 时间统计
        segment_times_arr = np.array(self.segment_times)
        print(f"\n⏱️  时间统计:")
        print(f"  总耗时: {total_time:.2f}s ({total_time/60:.1f}分钟)")
        print(f"  平均每段: {total_time/self.multi_config.n_segments:.2f}s")
        print(f"  最快一段: {segment_times_arr.min():.2f}s (第{segment_times_arr.argmin()+1}段)")
        print(f"  最慢一段: {segment_times_arr.max():.2f}s (第{segment_times_arr.argmax()+1}段)")
        print(f"  标准差: {segment_times_arr.std():.2f}s")

        # 迭代统计
        all_iters_arr = np.array(self.all_iters)
        print(f"\n🔄 迭代统计:")
        print(f"  总迭代: {sum(self.all_iters)}")
        print(f"  平均每段: {all_iters_arr.mean():.1f}次")
        print(f"  最少迭代: {all_iters_arr.min()}次 (第{all_iters_arr.argmin()+1}段)")
        print(f"  最多迭代: {all_iters_arr.max()}次 (第{all_iters_arr.argmax()+1}段)")

        # 代价统计
        all_costs_arr = np.array(self.all_costs)
        print(f"\n💰 代价统计:")
        print(f"  最终代价: {all_costs_arr[-1]:.2f}")
        print(f"  平均代价: {all_costs_arr.mean():.2f}")
        print(f"  最小代价: {all_costs_arr.min():.2f} (第{all_costs_arr.argmin()+1}段)")
        print(f"  最大代价: {all_costs_arr.max():.2f} (第{all_costs_arr.argmax()+1}段)")

        print(f"\n{'='*70}\n")

        # 轨迹信息
        print(f"合并轨迹:")
        print(f"  总状态数: {len(self.xs_combined)}")
        print(f"  总控制数: {len(self.us_combined)}")
        print(f"  总时长: {len(self.us_combined) * self.ocp_config.dt:.2f}s")

        return {
            'total_time': total_time,
            'segment_times': segment_times_arr,
            'all_iters': all_iters_arr,
            'all_costs': all_costs_arr,
        }

    def save_trajectory(self, save_path: str):
        """保存轨迹到文件"""
        if self.xs_combined is None:
            print("⚠️  没有可保存的轨迹，请先调用 solve_all_segments()")
            return

        # 提取关节数据
        joint_names = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']
        joint_data = {}

        for joint_name in joint_names:
            if self.ocp_solver.model.existJointName(joint_name):
                joint_id = self.ocp_solver.model.getJointId(joint_name)
                joint_q_idx = self.ocp_solver.model.joints[joint_id].idx_q
                joint_v_idx = self.ocp_solver.model.joints[joint_id].idx_v
                joint_positions = self.xs_combined[:, joint_q_idx]
                joint_velocities = self.xs_combined[:, self.ocp_solver.state.nq + joint_v_idx]
                joint_data[f'{joint_name}_position'] = joint_positions
                joint_data[f'{joint_name}_velocity'] = joint_velocities

        # 保存
        np.savez(save_path,
                 xs=self.xs_combined,
                 us=self.us_combined,
                 dt=self.ocp_config.dt,
                 n_segments=self.multi_config.n_segments,
                 segment_costs=np.array(self.all_costs),
                 segment_iters=np.array(self.all_iters),
                 **joint_data)

        print(f"\n✓ 轨迹已保存: {save_path}")
        print(f"  包含关节数据: {', '.join(joint_names)}")

    def save_joint_log(self, log_path: str):
        """保存详细的关节日志 CSV"""
        if self.xs_combined is None:
            print("⚠️  没有可保存的日志，请先调用 solve_all_segments()")
            return

        joint_names = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']

        # 获取轮速和 base 速度
        left_wheel_v_idx = self.ocp_solver.joint_indices['left'][1]
        right_wheel_v_idx = self.ocp_solver.joint_indices['right'][1]
        left_wheel_vels = self.xs_combined[:, self.ocp_solver.state.nq + left_wheel_v_idx] if left_wheel_v_idx else None
        right_wheel_vels = self.xs_combined[:, self.ocp_solver.state.nq + right_wheel_v_idx] if right_wheel_v_idx else None
        vx_velocities = self.xs_combined[:, self.ocp_solver.state.nq + 0]
        omega_z_velocities = self.xs_combined[:, self.ocp_solver.state.nq + 5]

        with open(log_path, 'w') as f:
            # 写入表头
            header = ['time(s)', 'segment']
            header.extend([
                'left_wheel_vel(rad/s)', 'right_wheel_vel(rad/s)',
                'base_vx(m/s)', 'base_omega_z(rad/s)'
            ])
            for jname in joint_names:
                header.extend([
                    f'{jname}_pos(rad)', f'{jname}_pos(deg)',
                    f'{jname}_vel(rad/s)', f'{jname}_acc(rad/s²)',
                    f'{jname}_torque(Nm)'
                ])
            f.write(','.join(header) + '\n')

            # 提取关节数据
            joint_info = {}
            for jname in joint_names:
                if self.ocp_solver.model.existJointName(jname):
                    joint_id = self.ocp_solver.model.getJointId(jname)
                    q_idx = self.ocp_solver.model.joints[joint_id].idx_q
                    v_idx = self.ocp_solver.model.joints[joint_id].idx_v
                    u_idx = v_idx - 6 if v_idx >= 6 else None

                    positions = self.xs_combined[:, q_idx]
                    velocities = self.xs_combined[:, self.ocp_solver.state.nq + v_idx]

                    # 计算加速度
                    accelerations = np.zeros(len(velocities))
                    accelerations[:-1] = (velocities[1:] - velocities[:-1]) / self.ocp_config.dt
                    accelerations[-1] = accelerations[-2]

                    # 提取力矩
                    torques = np.zeros(len(positions))
                    if u_idx is not None and u_idx >= 0 and u_idx < self.ocp_solver.nu:
                        torques[:-1] = self.us_combined[:, u_idx]
                        torques[-1] = 0.0

                    joint_info[jname] = {
                        'pos': positions,
                        'vel': velocities,
                        'acc': accelerations,
                        'torque': torques
                    }

            # 写入数据
            for t in range(len(self.xs_combined)):
                time = t * self.ocp_config.dt
                segment = min(t // self.multi_config.horizon_steps, self.multi_config.n_segments - 1)
                row = [f'{time:.4f}', f'{segment}']

                row.extend([
                    f'{left_wheel_vels[t]:.6f}' if left_wheel_vels is not None else '0.0',
                    f'{right_wheel_vels[t]:.6f}' if right_wheel_vels is not None else '0.0',
                    f'{vx_velocities[t]:.6f}',
                    f'{omega_z_velocities[t]:.6f}'
                ])

                for jname in joint_names:
                    if jname in joint_info:
                        info = joint_info[jname]
                        row.extend([
                            f'{info["pos"][t]:.6f}',
                            f'{np.rad2deg(info["pos"][t]):.3f}',
                            f'{info["vel"][t]:.6f}',
                            f'{info["acc"][t]:.6f}',
                            f'{info["torque"][t]:.6f}'
                        ])
                    else:
                        row.extend(['0.0'] * 5)

                f.write(','.join(row) + '\n')

        print(f"✓ 关节日志已保存: {log_path}")

    def plot_results(self, log_file: str, output_file: Optional[str] = None):
        """绘制关节数据图表"""
        if not os.path.exists(log_file):
            print(f"\n⚠️  未找到日志文件: {log_file}")
            return

        if output_file is None:
            output_file = os.path.join(os.path.dirname(log_file), 'joint_plots_multi.png')

        print(f"\n{'='*70}")
        print("生成关节数据图表".center(70))
        print(f"{'='*70}")

        # 读取CSV数据
        data = np.genfromtxt(log_file, delimiter=',', names=True, encoding='utf-8')

        joints = ['ankle', 'knee', 'hip', 'waist_roll', 'waist_yaw']

        # 创建子图：5行 × 4列
        fig, axes = plt.subplots(5, 4, figsize=(20, 18))
        fig.suptitle('Multi-OCP Joint Motion Data Analysis', fontsize=18, fontweight='bold')

        data_types = [
            ('pos(deg)', 'Angle (deg)', 'b-'),
            ('vel(rad/s)', 'Velocity (rad/s)', 'g-'),
            ('acc(rad/s²)', 'Acceleration (rad/s²)', 'r-'),
            ('torque(Nm)', 'Torque (Nm)', 'm-')
        ]

        time = data['times']

        for i, joint in enumerate(joints):
            for j, (suffix, ylabel, color) in enumerate(data_types):
                ax = axes[i, j]

                suffix_clean = suffix.replace('(', '').replace(')', '').replace('/', '')
                col_name = f'{joint}_{suffix_clean}'

                try:
                    values = data[col_name]
                    ax.plot(time, values, color, linewidth=1.5, label=joint)
                    ax.set_ylabel(ylabel, fontsize=10, fontweight='bold')
                    ax.set_xlabel('Time (s)', fontsize=9)
                    ax.grid(True, alpha=0.3)
                    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=0.8)

                    if i == 0:
                        title_map = {
                            'pos(deg)': 'Position',
                            'vel(rad/s)': 'Velocity',
                            'acc(rad/s²)': 'Acceleration',
                            'torque(Nm)': 'Torque'
                        }
                        ax.set_title(title_map[suffix], fontsize=12, fontweight='bold')

                    if j == 0:
                        ax.text(-0.15, 0.5, joint.replace('_', ' ').title(),
                               transform=ax.transAxes, fontsize=11, fontweight='bold',
                               rotation=90, va='center', ha='right')

                except (KeyError, ValueError) as e:
                    ax.text(0.5, 0.5, f'Data unavailable\n{col_name}',
                           ha='center', va='center', transform=ax.transAxes, fontsize=8)
                    ax.set_ylabel(ylabel, fontsize=10)
                    if j == 0:
                        ax.text(-0.15, 0.5, joint.replace('_', ' ').title(),
                               transform=ax.transAxes, fontsize=11, fontweight='bold',
                               rotation=90, va='center', ha='right')

        plt.tight_layout(rect=[0.03, 0, 1, 0.97])
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n✓ 关节数据图表已保存: {output_file}")
        plt.close()

        # 额外绘制轮速和 base 速度
        fig2, axes2 = plt.subplots(2, 2, figsize=(16, 10))
        fig2.suptitle('Wheel Velocities and Base Motion', fontsize=16, fontweight='bold')

        try:
            ax = axes2[0, 0]
            ax.plot(time, data['left_wheel_velrads'], 'b-', linewidth=2, label='Left Wheel')
            ax.plot(time, data['right_wheel_velrads'], 'r-', linewidth=2, label='Right Wheel')
            ax.set_xlabel('Time (s)', fontsize=11)
            ax.set_ylabel('Wheel Velocity (rad/s)', fontsize=11, fontweight='bold')
            ax.set_title('Wheel Angular Velocities', fontsize=12, fontweight='bold')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

            ax = axes2[0, 1]
            ax.plot(time, data['base_vxms'], 'g-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=11)
            ax.set_ylabel('Base Velocity (m/s)', fontsize=11, fontweight='bold')
            ax.set_title('Base Forward Velocity (vx)', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

            ax = axes2[1, 0]
            ax.plot(time, data['base_omega_zrads'], 'm-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=11)
            ax.set_ylabel('Angular Velocity (rad/s)', fontsize=11, fontweight='bold')
            ax.set_title('Base Yaw Rate (ωz)', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

            ax = axes2[1, 1]
            segment_ids = data['segment'].astype(int)
            ax.plot(time, segment_ids, 'k-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=11)
            ax.set_ylabel('Segment ID', fontsize=11, fontweight='bold')
            ax.set_title('OCP Segment Timeline', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_yticks(range(int(segment_ids.max()) + 1))

        except (KeyError, ValueError) as e:
            print(f"  ⚠️  轮速/base数据不完整: {e}")

        plt.tight_layout()
        wheel_plot_path = output_file.replace('.png', '_wheels.png')
        plt.savefig(wheel_plot_path, dpi=150, bbox_inches='tight')
        print(f"✓ 轮速和base运动图表已保存: {wheel_plot_path}")
        plt.close()

    def playback(self, rate: float = 1.0, repeat: bool = True):
        """使用 MuJoCo 播放轨迹"""
        if self.xs_combined is None:
            print("⚠️  没有可播放的轨迹，请先调用 solve_all_segments()")
            return

        try:
            import mujoco
            import mujoco.viewer
        except ImportError:
            print("\n⚠️  未安装 MuJoCo，跳过可视化")
            print("   安装方法: pip install mujoco")
            return

        print(f"\n{'='*70}")
        print("MuJoCo 可视化播放".center(70))
        print(f"{'='*70}")

        # 提取配置序列
        nq = self.ocp_solver.model.nq
        qs = self.xs_combined[:, :nq].copy()

        # 规范化四元数
        for i in range(len(qs)):
            qs[i] = pin.normalize(self.ocp_solver.model, qs[i])

        # 加载 MuJoCo 模型
        model = mujoco.MjModel.from_xml_path(self.mjcf_path)
        data = mujoco.MjData(model)

        print(f"\n✓ MuJoCo 模型加载成功")
        print(f"  - nq: {model.nq}, nv: {model.nv}, nu: {model.nu}")

        sleep_dt = max(self.ocp_config.dt / max(rate, 1e-6), 1e-4)

        print(f"\n开始轨迹播放:")
        print(f"  - 配置帧数: {len(qs)}")
        print(f"  - 时间步长: {self.ocp_config.dt:.4f}s")
        print(f"  - 播放速度: {rate:.2f}x")
        print(f"  - 循环播放: {'是' if repeat else '否'}")
        print(f"\n提示: 按 Ctrl+C 停止播放，或关闭 MuJoCo 窗口\n")

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
                            print(f"\r  循环 #{loop_count+1} - 进度: {progress:.1f}% ({frame_idx[0]}/{len(qs)})", end="")

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
        description="多段OCP连续控制（重构版）+ MuJoCo可视化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              # 默认：10段×50步
  %(prog)s --segments 50 --horizon 10   # 50段×10步
  %(prog)s --no-playback                # 只求解+绘图
  %(prog)s --no-plot                    # 只求解+播放
        """,
    )
    parser.add_argument("--segments", type=int, default=10, help="OCP段数")
    parser.add_argument("--horizon", type=int, default=50, help="每段时域步数")
    parser.add_argument("--no-playback", action="store_true", help="不启动播放")
    parser.add_argument("--no-plot", action="store_true", help="不生成图表")
    parser.add_argument("--rate", type=float, default=1.0, help="播放速度")
    parser.add_argument("--once", action="store_true", help="只播放一遍")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    mjcf_path = os.path.join(script_dir, "description/urdf/wbot_v2.xml")

    try:
        # 配置
        multi_config = MultiOCPConfig()
        multi_config.n_segments = args.segments
        multi_config.horizon_steps = args.horizon

        # 创建求解器
        multi_ocp = MultiOCP(mjcf_path, multi_config)

        # 求解所有段
        multi_ocp.solve_all_segments(verbose=False)

        # 保存轨迹
        save_path = os.path.join(script_dir, 'wbot_trajectory_multi.npz')
        multi_ocp.save_trajectory(save_path)

        # 保存日志
        log_path = os.path.join(script_dir, 'joint_log_multi.csv')
        multi_ocp.save_joint_log(log_path)

        # 绘图
        if not args.no_plot:
            multi_ocp.plot_results(log_path)
        else:
            print("\n✓ 跳过绘图（--no-plot）")

        # 播放
        if not args.no_playback:
            multi_ocp.playback(rate=args.rate, repeat=not args.once)
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
