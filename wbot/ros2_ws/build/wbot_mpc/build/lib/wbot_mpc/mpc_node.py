#!/usr/bin/env python3
"""
Wbot MPC Node - ROS2 Implementation

This node implements the Model Predictive Control solver for the wbot robot.
It subscribes to robot state and velocity commands, solves the optimal control
problem, and publishes the control output.

Architecture:
- Subscribes to: /wbot/state, /wbot/cmd_vel
- Publishes to: /wbot/control, /wbot/mpc_performance
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
import numpy as np
import time
from typing import Optional, Dict
from collections import deque

from wbot_msgs.msg import WbotState, WbotControl, VelocityCommand, MpcPerformance

from .ocp import WbotOCP
from .trajectory_generator import ExponentialTrajectory


class WbotMpcNode(Node):
    """
    MPC solver node for wbot robot.

    This node runs the MPC optimization in response to state updates.
    It maintains a warm-start solution and updates the reference trajectory
    based on velocity commands.
    """

    def __init__(self):
        super().__init__('wbot_mpc_node')

        # Declare parameters
        self.declare_parameter('horizon_steps', 20)
        self.declare_parameter('dt', 0.05)
        self.declare_parameter('ddp_max_iters', 50)
        self.declare_parameter('publish_performance', True)

        # Get parameters
        self.horizon_steps = self.get_parameter('horizon_steps').value
        self.dt = self.get_parameter('dt').value
        self.ddp_max_iters = self.get_parameter('ddp_max_iters').value
        self.publish_performance = self.get_parameter('publish_performance').value

        # Initialize OCP solver
        self.get_logger().info('Initializing OCP solver...')
        self.ocp_solver = WbotOCP(
            mjcf_path='/home/guanyu/crocoddyl/wbot/description/urdf/wbot_v2.xml'
        )

        # MPC state
        self.latest_state: Optional[WbotState] = None
        self.current_vx = 0.0
        self.current_omega_z = 0.0
        self.current_joint_targets = {}
        self.xs_prev = None
        self.us_prev = None

        # Trajectory generators
        self.vx_generator = ExponentialTrajectory(
            target=0.0,
            dt=self.dt,
            time_constant=1.0
        )
        self.omega_z_generator = ExponentialTrajectory(
            target=0.0,
            dt=self.dt,
            time_constant=0.5
        )

        # Performance tracking
        self.solve_times = deque(maxlen=50)
        self.last_solve_time = time.time()

        # Create callback groups for concurrent execution
        state_callback_group = MutuallyExclusiveCallbackGroup()
        cmd_callback_group = MutuallyExclusiveCallbackGroup()

        # Subscribers
        self.state_sub = self.create_subscription(
            WbotState,
            '/wbot/state',
            self.state_callback,
            10,
            callback_group=state_callback_group
        )

        self.cmd_sub = self.create_subscription(
            VelocityCommand,
            '/wbot/cmd_vel',
            self.cmd_callback,
            10,
            callback_group=cmd_callback_group
        )

        # Publishers
        self.control_pub = self.create_publisher(
            WbotControl,
            '/wbot/control',
            10
        )

        self.performance_pub = self.create_publisher(
            MpcPerformance,
            '/wbot/mpc_performance',
            10
        )

        self.get_logger().info('✓ Wbot MPC Node initialized')
        self.get_logger().info(f'  Horizon: {self.horizon_steps} steps ({self.horizon_steps * self.dt:.2f}s)')
        self.get_logger().info(f'  dt: {self.dt}s')
        self.get_logger().info(f'  Max DDP iterations: {self.ddp_max_iters}')

    def cmd_callback(self, msg: VelocityCommand):
        """
        Handle velocity command updates.

        Updates the target velocities for the trajectory generators.
        """
        self.get_logger().debug(f'Received command: vx={msg.vx:.2f}, omega_z={msg.omega_z:.2f}')

        # Update target velocities
        self.vx_generator.set_target(msg.vx)
        self.omega_z_generator.set_target(msg.omega_z)

        # Update target joint angles if provided
        if len(msg.target_joint_angles) > 0:
            # Assume order matches joint names in OCP
            for i, (joint_name, _) in enumerate(self.ocp_solver.actuated_joints.items()):
                if i < len(msg.target_joint_angles):
                    self.current_joint_targets[joint_name] = msg.target_joint_angles[i]

        self.get_logger().info(f'Command updated: vx={msg.vx:.2f} m/s, ω_z={msg.omega_z:.2f} rad/s')

    def state_callback(self, msg: WbotState):
        """
        Handle state updates and trigger MPC solve.

        This is the main callback that drives the MPC loop.
        """
        self.latest_state = msg

        # Solve MPC
        self.solve_mpc(msg)

    def solve_mpc(self, state_msg: WbotState):
        """
        Solve the MPC optimization problem.

        Args:
            state_msg: Current robot state
        """
        solve_start = time.time()

        # Extract state vector
        x_current = np.array(state_msg.state)

        # Update trajectory references
        vx_ref = self.vx_generator.update()
        omega_z_ref = self.omega_z_generator.update()

        # If no joint targets specified, use current joint positions
        if not self.current_joint_targets:
            nq = self.ocp_solver.state.nq
            q_current = x_current[:nq]

            # Extract current joint angles from joint_indices
            for joint_name, (idx_q, idx_v) in self.ocp_solver.joint_indices.items():
                if idx_q is not None and joint_name not in ['left', 'right', 'caster_yaw', 'caster_rotate']:
                    # Skip wheel joints, only track arm/body joints
                    self.current_joint_targets[joint_name] = q_current[idx_q]

        # Solve OCP
        try:
            # Prepare warm start (xs, us) tuple
            warm_start = None
            if self.xs_prev is not None and self.us_prev is not None:
                warm_start = (self.xs_prev, self.us_prev)

            result = self.ocp_solver.solve(
                x0=x_current,
                target_joint_angles=self.current_joint_targets,
                target_vx=vx_ref,
                target_omega_z=omega_z_ref,
                horizon_steps=self.horizon_steps,
                max_iter=self.ddp_max_iters,
                warm_start=warm_start,
                verbose=False
            )

            # Update warm-start for next iteration
            # Always update warm start (shift solution by one timestep)
            xs = result['xs'].tolist() if isinstance(result['xs'], np.ndarray) else result['xs']
            us = result['us'].tolist() if isinstance(result['us'], np.ndarray) else result['us']
            self.xs_prev = xs[1:] + [xs[-1]]
            self.us_prev = us[1:] + [us[-1]]

            # Publish control
            self.publish_control(result, state_msg.header.stamp)

            # Track performance
            solve_time = time.time() - solve_start
            self.solve_times.append(solve_time)

            # Publish performance metrics
            if self.publish_performance:
                self.publish_performance_metrics(result, solve_time)

            # Log periodically
            current_time = time.time()
            if current_time - self.last_solve_time > 2.0:
                avg_solve_time = np.mean(self.solve_times) * 1000
                mpc_freq = 1.0 / np.mean(self.solve_times) if len(self.solve_times) > 0 else 0.0
                self.get_logger().info(
                    f'MPC: {avg_solve_time:.1f}ms avg, '
                    f'{mpc_freq:.1f}Hz, '
                    f'cost={result["cost"]:.0f}, '
                    f'iters={result["iter"]}'
                )
                self.last_solve_time = current_time

        except Exception as e:
            self.get_logger().error(f'MPC solve failed: {e}')
            # Publish zero control on failure
            self.publish_zero_control(state_msg.header.stamp)

    def publish_control(self, result: Dict, timestamp):
        """
        Publish the MPC control output.

        Args:
            result: OCP solution dictionary
            timestamp: ROS timestamp
        """
        control_msg = WbotControl()
        control_msg.header.stamp = timestamp
        control_msg.header.frame_id = 'wbot_base'

        # Extract first control from trajectory
        u_apply = result['us'][0]
        control_msg.control = u_apply.tolist() if isinstance(u_apply, np.ndarray) else u_apply
        control_msg.valid = True  # If solve succeeded, control is valid

        # Time for which this control is valid (next timestep)
        control_msg.time = self.dt

        self.control_pub.publish(control_msg)

    def publish_zero_control(self, timestamp):
        """
        Publish zero control (safety fallback).

        Args:
            timestamp: ROS timestamp
        """
        control_msg = WbotControl()
        control_msg.header.stamp = timestamp
        control_msg.header.frame_id = 'wbot_base'
        control_msg.control = [0.0] * self.ocp_solver.nu
        control_msg.valid = False
        control_msg.time = 0.0

        self.control_pub.publish(control_msg)

    def publish_performance_metrics(self, result: Dict, solve_time: float):
        """
        Publish MPC performance metrics.

        Args:
            result: OCP solution dictionary
            solve_time: Solve time in seconds
        """
        perf_msg = MpcPerformance()
        perf_msg.header.stamp = self.get_clock().now().to_msg()
        perf_msg.solve_time = solve_time
        perf_msg.iterations = result['iter']
        perf_msg.converged = (result['iter'] < self.ddp_max_iters)  # Converged if didn't hit max iters
        perf_msg.cost = result['cost']

        if len(self.solve_times) > 1:
            perf_msg.mpc_frequency = 1.0 / np.mean(self.solve_times)
        else:
            perf_msg.mpc_frequency = 0.0

        self.performance_pub.publish(perf_msg)


def main(args=None):
    """Main entry point for the MPC node."""
    rclpy.init(args=args)

    try:
        node = WbotMpcNode()

        # Use multi-threaded executor for concurrent callbacks
        executor = MultiThreadedExecutor(num_threads=4)
        executor.add_node(node)

        try:
            executor.spin()
        except KeyboardInterrupt:
            pass
        finally:
            node.get_logger().info('Shutting down MPC node')
            node.destroy_node()

    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
