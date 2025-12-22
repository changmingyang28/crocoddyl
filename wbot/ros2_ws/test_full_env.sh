#!/bin/bash
# Test complete environment setup

cd /home/guanyu/crocoddyl/wbot/ros2_ws

# Activate conda
eval "$(conda shell.bash hook)"
conda activate croc

# Source ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

# Set PYTHONPATH
export PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages:$PYTHONPATH
export PYTHONPATH=/opt/ros/humble/local/lib/python3.10/dist-packages:$PYTHONPATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

echo "===== Environment Check ====="
echo "CONDA_PREFIX: $CONDA_PREFIX"
echo "Python: $(which python)"
echo ""

echo "===== Package Check ====="
python -c "import mujoco; print('✓ mujoco')" 2>/dev/null || echo "✗ mujoco"
python -c "import crocoddyl; print('✓ crocoddyl')" 2>/dev/null || echo "✗ crocoddyl"
python -c "import pinocchio; print('✓ pinocchio')" 2>/dev/null || echo "✗ pinocchio"
python -c "import rclpy; print('✓ rclpy')" 2>/dev/null || echo "✗ rclpy"
python -c "import numpy; print('✓ numpy')" 2>/dev/null || echo "✗ numpy"

echo ""
echo "If all packages show ✓, you're ready to run!"
echo "Run: ./run_wbot_mpc.sh"
