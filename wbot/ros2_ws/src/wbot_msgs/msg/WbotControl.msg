# Wbot control input message
# Contains control vector computed by MPC

std_msgs/Header header

# Time for which this control is valid
float64 time

# Control vector [wheel_left_vel, wheel_right_vel, arm_joint_torques...]
float64[] control

# Flag indicating if this is a valid control (solver converged)
bool valid
