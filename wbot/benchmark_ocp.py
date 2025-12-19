#!/usr/bin/env python3
"""
OCP 性能基准测试

对比不同配置和优化策略的求解速度
"""

import os
import sys
import time
import numpy as np
from ocp import WbotOCP, WbotOCPConfig
from ocp_fast import WbotOCPConfigFast, WbotOCPConfigUltraFast


def benchmark_single_ocp(ocp_solver, config_name, num_trials=10):
    """测试单个 OCP 的求解性能"""
    print(f"\n{'='*70}")
    print(f"测试配置: {config_name}".center(70))
    print(f"{'='*70}")

    target_angles = {
        'knee': -0.12,
        'waist_roll': 0.0,
        'waist_yaw': 0.0,
        'right_arm_pitch': 0.0,
        'left_arm_pitch': 0.0,
    }

    x0 = ocp_solver.get_initial_state()

    solve_times = []
    iterations = []
    costs = []

    print(f"\n运行 {num_trials} 次试验...")

    for trial in range(num_trials):
        # 冷启动
        result = ocp_solver.solve(
            x0=x0,
            target_joint_angles=target_angles,
            target_vx=1.0,
            target_omega_z=0.0,
            horizon_steps=50,
            max_iter=100,
            warm_start=None,
            verbose=False
        )

        solve_times.append(result['solve_time'])
        iterations.append(result['iter'])
        costs.append(result['cost'])

        if (trial + 1) % 5 == 0:
            print(f"  完成 {trial+1}/{num_trials} 次")

    # 统计
    solve_times = np.array(solve_times)
    iterations = np.array(iterations)
    costs = np.array(costs)

    print(f"\n📊 统计结果:")
    print(f"  求解时间:")
    print(f"    平均: {solve_times.mean()*1000:.1f} ms")
    print(f"    最小: {solve_times.min()*1000:.1f} ms")
    print(f"    最大: {solve_times.max()*1000:.1f} ms")
    print(f"    标准差: {solve_times.std()*1000:.1f} ms")

    print(f"\n  迭代次数:")
    print(f"    平均: {iterations.mean():.1f}")
    print(f"    最小: {iterations.min()}")
    print(f"    最大: {iterations.max()}")

    print(f"\n  代价函数:")
    print(f"    平均: {costs.mean():.2f}")
    print(f"    最小: {costs.min():.2f}")
    print(f"    最大: {costs.max():.2f}")

    # 实时性分析
    control_dt = 0.01  # 10ms 控制周期
    real_time_ratio = solve_times.mean() / control_dt

    print(f"\n  ⚡ 实时性:")
    print(f"    控制周期: {control_dt*1000:.1f} ms")
    print(f"    实时性比率: {real_time_ratio:.2%}")
    if real_time_ratio < 1.0:
        print(f"    ✓ 可以实时运行")
    else:
        print(f"    ✗ 无法实时运行 (需要加速 {1/real_time_ratio:.1f}x)")

    return {
        'solve_times': solve_times,
        'iterations': iterations,
        'costs': costs,
        'real_time_ratio': real_time_ratio
    }


def benchmark_warm_start(ocp_solver, config_name):
    """测试热启动的效果"""
    print(f"\n{'='*70}")
    print(f"测试热启动效果: {config_name}".center(70))
    print(f"{'='*70}")

    target_angles = {
        'knee': -0.12,
        'waist_roll': 0.0,
        'waist_yaw': 0.0,
        'right_arm_pitch': 0.0,
        'left_arm_pitch': 0.0,
    }

    x0 = ocp_solver.get_initial_state()

    # 冷启动
    print("\n1️⃣ 冷启动（无热启动）")
    result_cold = ocp_solver.solve(
        x0=x0,
        target_joint_angles=target_angles,
        horizon_steps=50,
        max_iter=100,
        warm_start=None,
        verbose=False
    )

    print(f"  求解时间: {result_cold['solve_time']*1000:.1f} ms")
    print(f"  迭代次数: {result_cold['iter']}")
    print(f"  代价: {result_cold['cost']:.2f}")

    # 热启动（使用上次的解）
    print("\n2️⃣ 热启动（使用上次的解）")

    # 轻微改变目标
    target_angles_2 = target_angles.copy()
    target_angles_2['knee'] = -0.24

    # 平移初始化
    xs_init = list(result_cold['xs'][1:]) + [result_cold['xs'][-1]]
    us_init = list(result_cold['us'][1:]) + [result_cold['us'][-1]]

    result_warm = ocp_solver.solve(
        x0=result_cold['xs'][1],  # 使用第二个状态
        target_joint_angles=target_angles_2,
        horizon_steps=50,
        max_iter=100,
        warm_start=(xs_init, us_init),
        verbose=False
    )

    print(f"  求解时间: {result_warm['solve_time']*1000:.1f} ms")
    print(f"  迭代次数: {result_warm['iter']}")
    print(f"  代价: {result_warm['cost']:.2f}")

    # 对比
    speedup = result_cold['solve_time'] / result_warm['solve_time']
    iter_reduction = (result_cold['iter'] - result_warm['iter']) / result_cold['iter'] * 100

    print(f"\n📈 热启动效果:")
    print(f"  加速比: {speedup:.2f}x")
    print(f"  迭代减少: {iter_reduction:.1f}%")


def benchmark_horizon_length(ocp_solver, config_name):
    """测试不同时域长度的影响"""
    print(f"\n{'='*70}")
    print(f"测试时域长度影响: {config_name}".center(70))
    print(f"{'='*70}")

    horizons = [20, 30, 50, 70, 100]
    target_angles = {
        'knee': -0.12,
        'waist_roll': 0.0,
        'waist_yaw': 0.0,
        'right_arm_pitch': 0.0,
        'left_arm_pitch': 0.0,
    }

    x0 = ocp_solver.get_initial_state()

    print(f"\n{'Horizon':<10} {'时间(ms)':<12} {'迭代':<8} {'代价':<12} {'实时性':<10}")
    print("-" * 60)

    for horizon in horizons:
        result = ocp_solver.solve(
            x0=x0,
            target_joint_angles=target_angles,
            horizon_steps=horizon,
            max_iter=100,
            warm_start=None,
            verbose=False
        )

        control_dt = 0.01
        real_time_ratio = result['solve_time'] / control_dt
        status = "✓" if real_time_ratio < 1.0 else "✗"

        print(f"{horizon:<10} "
              f"{result['solve_time']*1000:<12.1f} "
              f"{result['iter']:<8} "
              f"{result['cost']:<12.2f} "
              f"{status} {real_time_ratio:.2%}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mjcf_path = os.path.join(script_dir, "description/urdf/wbot_v2.xml")

    print("=" * 70)
    print("OCP 性能基准测试".center(70))
    print("=" * 70)

    # 配置列表
    configs = [
        ('Standard', WbotOCPConfig()),
        ('Fast', WbotOCPConfigFast()),
        ('UltraFast', WbotOCPConfigUltraFast()),
    ]

    results = {}

    # 测试1: 单次求解性能
    print("\n" + "🔬 测试 1: 单次求解性能".center(70))
    for name, config in configs:
        ocp_solver = WbotOCP(mjcf_path, config)
        results[name] = benchmark_single_ocp(ocp_solver, name, num_trials=10)

    # 对比总结
    print(f"\n{'='*70}")
    print("性能对比总结".center(70))
    print(f"{'='*70}")

    print(f"\n{'配置':<12} {'平均时间(ms)':<15} {'平均迭代':<12} {'实时性':<12}")
    print("-" * 70)

    for name in ['Standard', 'Fast', 'UltraFast']:
        res = results[name]
        avg_time = res['solve_times'].mean() * 1000
        avg_iter = res['iterations'].mean()
        status = "✓" if res['real_time_ratio'] < 1.0 else "✗"

        print(f"{name:<12} "
              f"{avg_time:<15.1f} "
              f"{avg_iter:<12.1f} "
              f"{status} {res['real_time_ratio']:.2%}")

    # 加速比
    baseline_time = results['Standard']['solve_times'].mean()
    print(f"\n加速比 (相对于 Standard):")
    for name in ['Fast', 'UltraFast']:
        speedup = baseline_time / results[name]['solve_times'].mean()
        print(f"  {name}: {speedup:.2f}x")

    # 测试2: 热启动效果
    print("\n" + "🔬 测试 2: 热启动效果".center(70))
    ocp_solver = WbotOCP(mjcf_path, WbotOCPConfigFast())
    benchmark_warm_start(ocp_solver, 'Fast')

    # 测试3: 时域长度影响
    print("\n" + "🔬 测试 3: 时域长度影响".center(70))
    ocp_solver = WbotOCP(mjcf_path, WbotOCPConfigFast())
    benchmark_horizon_length(ocp_solver, 'Fast')

    print(f"\n{'='*70}")
    print("测试完成！".center(70))
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
