# High-level velocity command for wbot
# User specifies desired base velocities

std_msgs/Header header

# Desired forward velocity (m/s)
float64 vx

# Desired yaw angular velocity (rad/s)
float64 omega_z

# Target arm joint angles (optional, empty means use current)
float64[] target_joint_angles
