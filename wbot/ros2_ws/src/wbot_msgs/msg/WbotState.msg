# Wbot robot state message
# Contains full state vector for MPC

std_msgs/Header header

# Current simulation time
float64 time

# Full state vector [q0, q1, q2, ..., v0, v1, v2, ...]
# For wbot: [base_x, base_y, base_theta, joint_angles..., base_vx, base_vy, base_omega, joint_velocities...]
float64[] state

# Current contact mode (for future extension)
int8 mode
