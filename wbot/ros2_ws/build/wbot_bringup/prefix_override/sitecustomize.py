import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/guanyu/crocoddyl/wbot/ros2_ws/install/wbot_bringup'
