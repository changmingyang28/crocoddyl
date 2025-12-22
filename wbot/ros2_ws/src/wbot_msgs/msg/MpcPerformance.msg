# MPC performance metrics message
# Published by MPC node for monitoring

std_msgs/Header header

# OCP solve time (seconds)
float64 solve_time

# Number of DDP iterations
int32 iterations

# Whether solver converged
bool converged

# Final cost value
float64 cost

# MPC computation frequency (Hz)
float64 mpc_frequency
