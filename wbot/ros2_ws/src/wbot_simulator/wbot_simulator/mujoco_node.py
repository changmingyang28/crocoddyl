#!/usr/bin/env python3
"""
Wbot MuJoCo Simulator Node - ROS2 Implementation

This node implements the real-time MuJoCo simulation loop for the wbot robot.
It runs the simulation at a fixed frequency, applies controls from the MPC,
and provides real-time visualization.

Architecture (following OCS2 MRT_ROS_Dummy_Loop pattern):
- Main loop runs at sim_frequency (e.g., 100Hz)
- Publishes state to /wbot/state
- Subscribes to control from /wbot/control
- Handles MuJoCo simulation and visualization
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
import numpy as np
import time
import mujoco
import mujoco.viewer
from typing import Optional
import pinocchio as pin

from wbot_msgs.msg import WbotState, WbotControl


class WbotMujocoNode(Node):
    """
    MuJoCo simulator node for wbot robot.

    This node runs the main simulation loop, following the OCS2 design pattern
    where the simulator (not MPC) drives the main loop.
    """

    def __init__(self):
        super().__init__('wbot_mujoco_node')

        # Declare parameters
        self.declare_parameter('sim_frequency', 100.0)  # Hz
        self.declare_parameter('mujoco_xml', '/home/guanyu/crocoddyl/wbot/description/scene.xml')
        self.declare_parameter('enable_viewer', True)
        self.declare_parameter('publish_frequency', 100.0)  # Can be different from sim

        # Get parameters
        self.sim_freq = self.get_parameter('sim_frequency').value
        self.dt_sim = 1.0 / self.sim_freq
        self.mujoco_xml = self.get_parameter('mujoco_xml').value
        self.enable_viewer = self.get_parameter('enable_viewer').value
        self.publish_freq = self.get_parameter('publish_frequency').value

        # Initialize MuJoCo
        self.get_logger().info(f'Loading MuJoCo model from {self.mujoco_xml}')
        self.model = mujoco.MjModel.from_xml_path(self.mujoco_xml)
        self.data = mujoco.MjData(self.model)

        # Set simulation timestep
        self.model.opt.timestep = self.dt_sim

        # Control state
        self.latest_control: Optional[WbotControl] = None
        self.last_control_time = 0.0

        # Pinocchio model for state extraction (optional, for consistency)
        # Use MJCF instead of URDF to match the MuJoCo model
        self.pin_model = pin.buildModelFromMJCF(self.mujoco_xml)
        self.pin_data = self.pin_model.createData()

        # Get joint mapping (MuJoCo joint names to indices)
        self.joint_names = []
        for i in range(self.model.njnt):
            joint_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if joint_name:
                self.joint_names.append(joint_name)

        # Get actuator mapping
        self.actuator_names = []
        for i in range(self.model.nu):
            actuator_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
            if actuator_name:
                self.actuator_names.append(actuator_name)

        self.get_logger().info(f'MuJoCo model loaded: {len(self.joint_names)} joints, {len(self.actuator_names)} actuators')
        self.get_logger().info(f'Actuators: {self.actuator_names}')

        # Subscriber (using callback group for thread safety)
        control_callback_group = MutuallyExclusiveCallbackGroup()
        self.control_sub = self.create_subscription(
            WbotControl,
            '/wbot/control',
            self.control_callback,
            10,
            callback_group=control_callback_group
        )

        # Publisher
        self.state_pub = self.create_publisher(
            WbotState,
            '/wbot/state',
            10
        )

        # Initialize robot to a stable configuration
        self.initialize_robot_state()

        # Viewer (will be created in run loop if needed)
        self.viewer = None

        # Simulation statistics
        self.sim_step_count = 0
        self.start_time = time.time()
        self.last_log_time = time.time()

        self.get_logger().info('✓ Wbot MuJoCo Node initialized')
        self.get_logger().info(f'  Simulation frequency: {self.sim_freq} Hz')
        self.get_logger().info(f'  Timestep: {self.dt_sim*1000:.2f} ms')
        self.get_logger().info(f'  Viewer enabled: {self.enable_viewer}')

    def initialize_robot_state(self):
        """
        Initialize robot to a stable standing configuration.
        """
        # Set initial joint positions (matching OCP initial state)
        # The model uses a free floating base in 3D:
        # qpos[0:3] = base position (x, y, z)
        # qpos[3:7] = base orientation (quaternion: qw, qx, qy, qz)
        # qpos[7:] = other joints

        # Base position
        self.data.qpos[0] = 0.0      # base_x
        self.data.qpos[1] = 0.0      # base_y
        self.data.qpos[2] = 0.0935   # base_z (height from ground)

        # Base orientation (quaternion: no rotation)
        self.data.qpos[3] = 1.0      # qw
        self.data.qpos[4] = 0.0      # qx
        self.data.qpos[5] = 0.0      # qy
        self.data.qpos[6] = 0.0      # qz

        # Other joints (default configuration)
        # Set all to zero or small values to avoid collisions
        if self.model.nq > 7:
            for i in range(7, min(self.model.nq, 18)):
                self.data.qpos[i] = 0.0

        # Set velocities to zero
        self.data.qvel[:] = 0.0

        # Set controls to zero
        self.data.ctrl[:] = 0.0

        # Forward kinematics
        mujoco.mj_forward(self.model, self.data)

        self.get_logger().info(f'Robot initialized: nq={self.model.nq}, nv={self.model.nv}')

    def control_callback(self, msg: WbotControl):
        """
        Handle control updates from MPC.

        Args:
            msg: Control message from MPC
        """
        if not msg.valid:
            self.get_logger().warn('Received invalid control, ignoring')
            return

        self.latest_control = msg
        self.last_control_time = time.time()

    def get_state_vector(self) -> np.ndarray:
        """
        Extract full state vector from MuJoCo simulation.

        Returns:
            State vector [q, v] compatible with Pinocchio/Crocoddyl
        """
        nq = self.model.nq
        nv = self.model.nv

        # Extract positions and velocities
        q = self.data.qpos.copy()
        v = self.data.qvel.copy()

        # Concatenate to form state vector
        x = np.concatenate([q, v])

        return x

    def apply_control(self):
        """
        Apply the latest control from MPC to the simulation.
        """
        if self.latest_control is None:
            # No control received yet, apply zero control
            self.data.ctrl[:] = 0.0
            return

        # Check if control is stale (timeout after 0.5 seconds)
        if time.time() - self.last_control_time > 0.5:
            self.get_logger().warn('Control timeout, applying zero control')
            self.data.ctrl[:] = 0.0
            return

        # Apply control
        control = np.array(self.latest_control.control)
        if len(control) == self.model.nu:
            self.data.ctrl[:] = control
        else:
            self.get_logger().error(
                f'Control dimension mismatch: expected {self.model.nu}, got {len(control)}'
            )

    def publish_state(self):
        """
        Publish current robot state to ROS.
        """
        state_msg = WbotState()
        state_msg.header.stamp = self.get_clock().now().to_msg()
        state_msg.header.frame_id = 'world'

        # Get state vector
        x = self.get_state_vector()
        state_msg.state = x.tolist()
        state_msg.time = self.data.time
        state_msg.mode = 0  # Single mode for now

        self.state_pub.publish(state_msg)

    def simulation_step(self):
        """
        Execute one simulation step.

        This is the core of the main loop.
        """
        # Apply control from MPC
        self.apply_control()

        # Step simulation
        mujoco.mj_step(self.model, self.data)

        # Publish state (this triggers MPC to solve)
        self.publish_state()

        # Update counter
        self.sim_step_count += 1

    def run(self):
        """
        Main simulation loop.

        This follows the OCS2 MRT_ROS_Dummy_Loop pattern:
        - Runs at fixed frequency (sim_frequency)
        - Steps simulation
        - Publishes state (which triggers MPC)
        - Handles visualization

        This is the PRIMARY LOOP in the system (not MPC).
        """
        self.get_logger().info('='*70)
        self.get_logger().info('Starting MuJoCo simulation loop')
        self.get_logger().info('='*70)

        # Create viewer if enabled
        if self.enable_viewer:
            self.get_logger().info('Opening MuJoCo viewer...')
            # Note: mujoco.viewer.launch_passive creates a non-blocking viewer
            self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
            self.viewer.cam.distance = 3.0
            self.viewer.cam.elevation = -20
            self.viewer.cam.azimuth = 135
            time.sleep(0.5)  # Give viewer time to initialize

        # Main loop timing
        loop_start_time = time.time()
        target_period = self.dt_sim

        try:
            while rclpy.ok():
                step_start = time.time()

                # Execute simulation step
                self.simulation_step()

                # Update viewer
                if self.viewer is not None:
                    self.viewer.sync()

                # Spin ROS callbacks (non-blocking)
                rclpy.spin_once(self, timeout_sec=0.0)

                # Log statistics periodically
                current_time = time.time()
                if current_time - self.last_log_time > 5.0:
                    elapsed = current_time - self.start_time
                    avg_freq = self.sim_step_count / elapsed
                    self.get_logger().info(
                        f'Simulation: {self.sim_step_count} steps, '
                        f'{avg_freq:.1f} Hz, '
                        f'time={self.data.time:.2f}s'
                    )
                    self.last_log_time = current_time

                # Sleep to maintain fixed frequency
                step_duration = time.time() - step_start
                sleep_time = target_period - step_duration

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # Running slower than target frequency
                    if self.sim_step_count % 100 == 0:
                        self.get_logger().warn(
                            f'Simulation running slow: {step_duration*1000:.1f}ms > {target_period*1000:.1f}ms'
                        )

        except KeyboardInterrupt:
            self.get_logger().info('Keyboard interrupt received')

        finally:
            # Cleanup
            if self.viewer is not None:
                self.get_logger().info('Closing viewer...')
                self.viewer.close()
                time.sleep(0.2)

            self.get_logger().info('Simulation stopped')


def main(args=None):
    """Main entry point for the MuJoCo simulator node."""
    rclpy.init(args=args)

    try:
        node = WbotMujocoNode()

        # Run the simulation loop (this blocks)
        # Note: We don't use executor.spin() because we need manual control
        # of the loop timing for real-time simulation
        node.run()

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
