#!/bin/bash
# 使用conda环境启动Wbot MPC系统

cd /home/guanyu/crocoddyl/wbot/ros2_ws

# 激活conda环境
eval "$(conda shell.bash hook)"
conda activate croc

# 使用conda的C++库（解决CXXABI版本问题）
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Source ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

# 添加ROS2 Python包到PYTHONPATH（让conda Python能找到rclpy）
# 注意：conda的site-packages要在最前面，避免使用~/.local的包
export PYTHONPATH=$CONDA_PREFIX/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages:/opt/ros/humble/lib/python3.10/site-packages:$PYTHONPATH

echo "========================================================================"
echo "  Wbot MPC System (Conda环境)"
echo "========================================================================"
echo ""
echo "环境: croc (conda)"
echo "Python: $(which python)"
echo ""
echo "启动节点:"
echo "  - MuJoCo仿真器 @ 100Hz"
echo "  - MPC求解器"
echo ""
echo "要控制机器人，在另一个终端运行:"
echo "  conda activate croc"
echo "  cd $(pwd)"
echo "  source /opt/ros/humble/setup.bash"
echo "  source install/setup.bash"
echo "  export PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:\$PYTHONPATH"
echo "  ros2 run wbot_command velocity_command"
echo ""
echo "========================================================================"
echo ""

ros2 launch wbot_bringup wbot_mpc_sim_only.launch.py
