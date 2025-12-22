# Wbot MPC ROS2 - 快速启动指南

## 依赖问题说明

由于ROS2的pinocchio需要numpy 1.x，而pip安装的crocoddyl需要numpy 2.x，存在版本冲突。

**推荐方案：使用conda环境**，因为那里所有依赖都是兼容的。

## 🚀 快速启动（推荐）

### 终端1 - 启动仿真器和MPC

```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
./run_with_conda.sh
```

### 终端2 - 启动键盘控制（可选）

```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
conda activate croc
source /opt/ros/humble/setup.bash
source install/setup.bash
export PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:$PYTHONPATH
ros2 run wbot_command velocity_command
```

键盘控制：
- `w`: 加速
- `s`: 减速
- `a`: 左转
- `d`: 右转
- `x`: 停止
- `q`: 退出

## 📋 系统检查

```bash
cd /home/guanyu/crocoddyl/wbot/ros2_ws
conda activate croc
source /opt/ros/humble/setup.bash
export PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:$PYTHONPATH

python3 << 'EOF'
import mujoco
import crocoddyl
import pinocchio
import rclpy
print("✓ All dependencies OK!")
EOF
```

## 🔍 监控话题

```bash
# 查看MPC性能
ros2 topic echo /wbot/mpc_performance

# 查看机器人状态频率
ros2 topic hz /wbot/state

# 节点图
rqt_graph
```

## ⚙️ 参数调整

编辑 `run_with_conda.sh`，在最后一行添加参数：

```bash
ros2 launch wbot_bringup wbot_mpc_sim_only.launch.py \
    horizon_steps:=15 \
    dt:=0.05 \
    sim_frequency:=100.0
```

## 🐛 故障排除

### 问题1: MuJoCo viewer不显示

```bash
export DISPLAY=:0
```

### 问题2: import错误

确保正确设置PYTHONPATH：
```bash
export PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:$PYTHONPATH
```

### 问题3: 性能慢

降低horizon或增加ddp_max_iters。

## 📝 架构说明

- **MuJoCo Node**: 主循环 @ 100Hz，发布/wbot/state
- **MPC Node**: 异步求解，订阅/wbot/state，发布/wbot/control
- **Command Node**: 键盘输入，发布/wbot/cmd_vel

参考 `ARCHITECTURE.md` 了解详细设计。
