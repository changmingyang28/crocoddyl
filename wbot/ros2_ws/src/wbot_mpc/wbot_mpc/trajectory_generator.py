#!/usr/bin/env python3
"""
参考轨迹生成器

为 MPC 生成平滑的参考轨迹，不依赖总步长
"""

import numpy as np
from typing import Optional


class TrajectoryGenerator:
    """参考轨迹生成器基类"""

    def __init__(self, target: float, dt: float):
        """
        参数:
            target: 目标值
            dt: 控制周期
        """
        self.target = target
        self.dt = dt
        self.current_value = 0.0
        self.time = 0.0

    def reset(self, initial_value: float):
        """重置轨迹生成器"""
        self.current_value = initial_value
        self.time = 0.0

    def update(self, current_value: float) -> float:
        """
        更新并获取下一个参考值

        参数:
            current_value: 当前实际值

        返回:
            参考值
        """
        raise NotImplementedError


class ExponentialTrajectory(TrajectoryGenerator):
    """
    指数平滑轨迹（推荐用于 MPC）

    公式: x_ref(t) = x_current + (x_target - x_current) * (1 - exp(-t/τ))

    特点:
    - 从当前状态平滑过渡到目标
    - 不依赖总步长
    - 时间常数 τ 控制收敛速度
    """

    def __init__(self, target: float, dt: float, time_constant: float = 1.0):
        """
        参数:
            target: 目标值
            dt: 控制周期
            time_constant: 时间常数 τ（秒），越小收敛越快
                          τ=1.0: 约1秒达到63%
                          τ=0.5: 约0.5秒达到63%
        """
        super().__init__(target, dt)
        self.time_constant = time_constant
        self.initial_value = 0.0

    def reset(self, initial_value: float):
        super().reset(initial_value)
        self.initial_value = initial_value

    def update(self, current_value: Optional[float] = None) -> float:
        """
        更新参考轨迹

        参数:
            current_value: 当前实际值（如果为None，使用内部状态）
        """
        if current_value is not None:
            self.current_value = current_value

        # 指数平滑公式
        error = self.target - self.initial_value
        progress = 1.0 - np.exp(-self.time / self.time_constant)
        ref_value = self.initial_value + error * progress

        self.time += self.dt
        return ref_value

    def get_info(self):
        """返回轨迹信息"""
        return {
            'type': 'Exponential',
            'target': self.target,
            'time_constant': self.time_constant,
            'current': self.current_value,
            'time': self.time
        }


class RateLimitedTrajectory(TrajectoryGenerator):
    """
    速度限制轨迹

    特点:
    - 以最大速度接近目标
    - 到达后保持
    - 适合需要限制运动速度的场景
    """

    def __init__(self, target: float, dt: float, max_velocity: float = 0.5):
        """
        参数:
            target: 目标值
            dt: 控制周期
            max_velocity: 最大速度（单位/秒）
        """
        super().__init__(target, dt)
        self.max_velocity = max_velocity

    def update(self, current_value: Optional[float] = None) -> float:
        if current_value is not None:
            self.current_value = current_value

        error = self.target - self.current_value

        # 计算本步的位移（速度限制）
        max_step = self.max_velocity * self.dt

        if abs(error) < max_step:
            # 已经很接近，直接到达
            ref_value = self.target
        else:
            # 以最大速度移动
            direction = np.sign(error)
            ref_value = self.current_value + direction * max_step

        self.current_value = ref_value
        self.time += self.dt
        return ref_value

    def get_info(self):
        return {
            'type': 'RateLimited',
            'target': self.target,
            'max_velocity': self.max_velocity,
            'current': self.current_value,
            'time': self.time
        }


class SmoothStepTrajectory(TrajectoryGenerator):
    """
    平滑阶跃轨迹（S曲线）

    使用五次多项式插值，保证位置、速度、加速度连续

    特点:
    - 极其平滑
    - 固定时间到达
    - 需要指定到达时间
    """

    def __init__(self, target: float, dt: float, duration: float = 2.0):
        """
        参数:
            target: 目标值
            dt: 控制周期
            duration: 到达时间（秒）
        """
        super().__init__(target, dt)
        self.duration = duration
        self.initial_value = 0.0

    def reset(self, initial_value: float):
        super().reset(initial_value)
        self.initial_value = initial_value

    def update(self, current_value: Optional[float] = None) -> float:
        if current_value is not None:
            self.current_value = current_value

        t = min(self.time, self.duration)
        s = t / self.duration  # 归一化时间 [0, 1]

        # 五次多项式插值: 6s^5 - 15s^4 + 10s^3
        blend = 6 * s**5 - 15 * s**4 + 10 * s**3

        error = self.target - self.initial_value
        ref_value = self.initial_value + error * blend

        self.time += self.dt
        return ref_value

    def get_info(self):
        return {
            'type': 'SmoothStep',
            'target': self.target,
            'duration': self.duration,
            'current': self.current_value,
            'time': self.time
        }


class AdaptiveTrajectory(TrajectoryGenerator):
    """
    自适应轨迹（基于当前误差调整速度）

    特点:
    - 误差大时快速接近
    - 误差小时缓慢接近
    - 避免震荡
    """

    def __init__(self, target: float, dt: float,
                 gain: float = 2.0, deadband: float = 0.01):
        """
        参数:
            target: 目标值
            dt: 控制周期
            gain: 增益系数（越大响应越快）
            deadband: 死区（误差小于此值时不动）
        """
        super().__init__(target, dt)
        self.gain = gain
        self.deadband = deadband

    def update(self, current_value: Optional[float] = None) -> float:
        if current_value is not None:
            self.current_value = current_value

        error = self.target - self.current_value

        # 死区
        if abs(error) < self.deadband:
            return self.current_value

        # 一阶低通滤波: x_ref += gain * error * dt
        step = self.gain * error * self.dt
        ref_value = self.current_value + step

        self.current_value = ref_value
        self.time += self.dt
        return ref_value

    def get_info(self):
        return {
            'type': 'Adaptive',
            'target': self.target,
            'gain': self.gain,
            'deadband': self.deadband,
            'current': self.current_value,
            'time': self.time
        }


def compare_trajectories():
    """对比不同轨迹生成器"""
    import matplotlib.pyplot as plt

    target = -1.2
    dt = 0.01
    steps = 500

    generators = {
        'Exponential (τ=1.0)': ExponentialTrajectory(target, dt, time_constant=1.0),
        'Exponential (τ=0.5)': ExponentialTrajectory(target, dt, time_constant=0.5),
        'RateLimited (0.5 rad/s)': RateLimitedTrajectory(target, dt, max_velocity=0.5),
        'SmoothStep (2s)': SmoothStepTrajectory(target, dt, duration=2.0),
        'Adaptive (gain=2)': AdaptiveTrajectory(target, dt, gain=2.0),
    }

    # 初始化
    initial_value = 0.0
    for gen in generators.values():
        gen.reset(initial_value)

    # 生成轨迹
    trajectories = {name: [] for name in generators.keys()}

    for step in range(steps):
        for name, gen in generators.items():
            ref = gen.update()
            trajectories[name].append(ref)

    # 绘图
    time = np.arange(steps) * dt

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # 位置轨迹
    ax = axes[0]
    for name, traj in trajectories.items():
        ax.plot(time, traj, linewidth=2, label=name)
    ax.axhline(y=target, color='r', linestyle='--', linewidth=2, label='Target')
    ax.axhline(y=initial_value, color='k', linestyle='--', alpha=0.3, label='Initial')
    ax.set_ylabel('Position (rad)', fontsize=12, fontweight='bold')
    ax.set_title('Reference Trajectory Comparison', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # 速度（数值微分）
    ax = axes[1]
    for name, traj in trajectories.items():
        velocity = np.diff(traj) / dt
        ax.plot(time[:-1], velocity, linewidth=2, label=name)
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Velocity (rad/s)', fontsize=12, fontweight='bold')
    ax.set_title('Reference Velocity', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('trajectory_comparison.png', dpi=150, bbox_inches='tight')
    print("\n✓ 轨迹对比图已保存: trajectory_comparison.png")
    plt.close()

    # 打印收敛时间（到达95%）
    print(f"\n{'='*70}")
    print("到达95%目标的时间:")
    print(f"{'='*70}")
    threshold = initial_value + 0.95 * (target - initial_value)

    for name, traj in trajectories.items():
        traj_arr = np.array(traj)
        idx = np.where(traj_arr <= threshold)[0]
        if len(idx) > 0:
            t_95 = idx[0] * dt
            print(f"  {name:<30}: {t_95:.2f}s")
        else:
            print(f"  {name:<30}: >5s")


if __name__ == "__main__":
    print("=" * 70)
    print("参考轨迹生成器对比".center(70))
    print("=" * 70)

    compare_trajectories()

    print("\n使用建议:")
    print("  1. ExponentialTrajectory: 推荐用于 MPC（平滑、简单）")
    print("  2. RateLimitedTrajectory: 需要严格限制速度时")
    print("  3. SmoothStepTrajectory: 需要固定时间到达时")
    print("  4. AdaptiveTrajectory: 需要自适应响应时")
    print()
