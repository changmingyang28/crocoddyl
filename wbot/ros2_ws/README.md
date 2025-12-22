# Wbot MPC ROS2 System

基于ROS2的Wbot差速驱动机器人模型预测控制系统。

## 系统架构

本系统采用OCS2风格的分布式节点架构：

```
┌─────────────────────┐
│ Velocity Command    │  用户通过键盘输入期望速度
│ Node                │  发布: /wbot/cmd_vel
└──────────┬──────────┘
           │
           ↓ VelocityCommand
┌──────────────────────────────────────────────────────┐
│                  MPC Node                            │
│  - 订阅: /wbot/state, /wbot/cmd_vel                  │
│  - 求解OCP (DDP算法)                                  │
│  - 发布: /wbot/control, /wbot/mpc_performance       │
└──────────────┬───────────────────────────────────────┘
               │ WbotControl
               ↓
┌──────────────────────────────────────────────────────┐
│            MuJoCo Simulator Node                     │
│  (主循环 @ 100Hz)                                     │
│  - 运行MuJoCo仿真                                     │
│  - 应用MPC控制                                        │
│  - 发布: /wbot/state                                 │
│  - 实时可视化                                         │
└──────────────────────────────────────────────────────┘
```

### 关键设计特点

1. **异步架构**: 仿真器驱动主循环（100Hz），MPC异步求解（约20-50Hz）
2. **实时可视化**: MuJoCo边仿真边显示（不是先算完再播放）
3. **命令切换**: 随时可以通过键盘更改目标速度
4. **性能监控**: 发布MPC求解时间、迭代次数等指标

## 包说明

### wbot_msgs
ROS2消息定义包：
- `WbotState.msg`: 机器人状态 [q, v]
- `WbotControl.msg`: 控制输入 [wheel_vels, joint_torques]
- `VelocityCommand.msg`: 高层速度命令 (vx, omega_z)
- `MpcPerformance.msg`: MPC性能指标

### wbot_mpc
MPC求解器节点：
- 订阅机器人状态和速度命令
- 求解OCP（使用Crocoddyl DDP）
- 发布第一个控制输入（receding horizon）
- 使用warm-start加速求解

### wbot_simulator
MuJoCo仿真器节点：
- **主循环**: 以固定频率运行仿真
- 应用MPC控制
- 发布状态（触发MPC求解）
- 提供实时可视化

### wbot_command
速度命令接口：
- 键盘交互
- 发布期望的vx和omega_z

### wbot_bringup
Launch文件集合

## 编译

```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

## 运行

### 方式1: 使用Launch文件（推荐）

```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
source install/setup.bash
ros2 launch wbot_bringup wbot_mpc.launch.py
```

可选参数：
```bash
ros2 launch wbot_bringup wbot_mpc.launch.py \
    sim_frequency:=100.0 \
    horizon_steps:=20 \
    dt:=0.05 \
    enable_viewer:=true
```

### 方式2: 手动启动各节点

终端1 - MuJoCo仿真器（主循环）:
```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
source install/setup.bash
ros2 run wbot_simulator mujoco_node
```

终端2 - MPC求解器:
```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
source install/setup.bash
ros2 run wbot_mpc mpc_node
```

终端3 - 速度命令:
```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
source install/setup.bash
ros2 run wbot_command velocity_command
```

## 使用说明

### 键盘控制
在命令终端中：
- `w`: 增加前向速度
- `s`: 减少前向速度
- `a`: 增加左转角速度
- `d`: 增加右转角速度
- `x`: 停止（所有速度归零）
- `q`: 退出

### 监控话题

查看MPC性能：
```bash
ros2 topic echo /wbot/mpc_performance
```

查看当前状态：
```bash
ros2 topic echo /wbot/state
```

查看控制输出：
```bash
ros2 topic echo /wbot/control
```

### 可视化节点图

```bash
rqt_graph
```

### 录制数据（用于后续分析）

```bash
ros2 bag record -a
```

## 参数调整

### MPC参数
编辑 `launch/wbot_mpc.launch.py` 或通过命令行：
- `horizon_steps`: MPC预测步数（默认20）
- `dt`: 时间步长（默认0.05s）
- `ddp_max_iters`: DDP最大迭代次数（默认50）

### 仿真参数
- `sim_frequency`: 仿真频率（默认100Hz）
- `enable_viewer`: 是否启用MuJoCo可视化（默认true）

## 故障排除

### 问题1: MuJoCo viewer无法打开
确保DISPLAY环境变量设置正确：
```bash
echo $DISPLAY
# 如果为空，设置：
export DISPLAY=:0
```

### 问题2: MPC求解超时
检查日志中的求解时间。如果过长（>100ms），尝试：
- 减少 `horizon_steps`
- 减少 `ddp_max_iters`
- 检查是否有其他进程占用CPU

### 问题3: 控制不平滑
- 确保MPC频率足够高（>20Hz）
- 检查 `/wbot/mpc_performance` 中的converged标志
- 增加 `horizon_steps` 以获得更长的预测

### 问题4: 仿真运行慢
检查仿真频率：
```bash
ros2 topic hz /wbot/state
```
如果低于目标频率，尝试关闭viewer或降低仿真频率。

## 与原始实现对比

| 特性 | 原始实现 (mpc.py) | ROS2实现 |
|------|------------------|----------|
| 架构 | 单脚本monolithic | 分布式节点 |
| 可视化 | 先计算后回放 | 实时边算边显示 |
| 命令切换 | ❌ | ✅ |
| 监控 | 终端日志 | ROS topics + rqt |
| 扩展性 | 低 | 高（易于添加新节点） |
| 调试 | 困难 | 简单（独立测试各节点） |

## 后续扩展

可以轻松添加的新功能：

1. **性能监控节点**:
   - 订阅 `/wbot/mpc_performance`
   - 发布到 `/diagnostics`
   - 可视化求解时间趋势

2. **轨迹记录节点**:
   - 订阅 `/wbot/state` 和 `/wbot/control`
   - 保存到文件用于离线分析

3. **安全监控节点**:
   - 监控速度/加速度限制
   - 发布紧急停止信号

4. **路径规划节点**:
   - 生成参考路径
   - 发布高层目标点
   - MPC跟踪参考轨迹

5. **RViz插件**:
   - 显示MPC预测轨迹
   - 显示接触力
   - 显示参考路径

## 性能基准

在典型配置下（horizon=20, dt=0.05, 100Hz仿真）：
- MPC平均求解时间: 5-25ms
- MPC频率: 20-50Hz（异步）
- 仿真频率: 100Hz
- 总CPU占用: <80%（单核）

## 许可证

MIT License

## 参考

本实现参考了以下开源项目的架构设计：
- [OCS2](https://github.com/leggedrobotics/ocs2) - 用于MRT_ROS_Dummy_Loop模式
- [Crocoddyl](https://github.com/loco-3d/crocoddyl) - 用于DDP求解器
