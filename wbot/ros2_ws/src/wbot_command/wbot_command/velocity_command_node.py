#!/usr/bin/env python3
"""
Wbot Velocity Command Node - ROS2 Implementation

This node provides a keyboard interface for sending velocity commands to the wbot.
Users can interactively specify desired forward velocity and yaw rate.

Architecture:
- Publishes to: /wbot/cmd_vel
- Interactive keyboard input
"""

import rclpy
from rclpy.node import Node
import sys
import select
import tty
import termios
from typing import Optional

from wbot_msgs.msg import VelocityCommand


class VelocityCommandNode(Node):
    """
    Velocity command node for wbot robot.

    Provides keyboard interface for sending velocity commands.
    """

    def __init__(self):
        super().__init__('velocity_command_node')

        # Publisher
        self.cmd_pub = self.create_publisher(
            VelocityCommand,
            '/wbot/cmd_vel',
            10
        )

        # Command state
        self.current_vx = 0.0
        self.current_omega_z = 0.0

        # Velocity increments
        self.vx_increment = 0.1  # m/s
        self.omega_increment = 0.1  # rad/s

        # Limits
        self.vx_max = 2.0  # m/s
        self.omega_max = 1.5  # rad/s

        self.get_logger().info('✓ Velocity Command Node initialized')
        self.print_instructions()

    def print_instructions(self):
        """Print keyboard control instructions."""
        print('\n' + '='*70)
        print('Wbot Velocity Command Interface')
        print('='*70)
        print('\nKeyboard Controls:')
        print('  w/s : Increase/Decrease forward velocity (vx)')
        print('  a/d : Increase/Decrease yaw rate (omega_z)')
        print('  x   : Stop (set all velocities to zero)')
        print('  q   : Quit')
        print('\nCurrent limits:')
        print(f'  vx: ±{self.vx_max} m/s')
        print(f'  omega_z: ±{self.omega_max} rad/s')
        print('='*70)
        print(f'\nCurrent command: vx={self.current_vx:.2f} m/s, omega_z={self.current_omega_z:.2f} rad/s')
        print('\nPress keys to control (no need to press Enter)...\n')

    def get_key(self) -> Optional[str]:
        """
        Get a single keypress without waiting for Enter.

        Returns:
            Key character or None if no key pressed
        """
        # Save terminal settings
        settings = termios.tcgetattr(sys.stdin)

        try:
            tty.setraw(sys.stdin.fileno())

            # Check if input is available (non-blocking)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1)
                return key
            else:
                return None

        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def update_command(self, key: str):
        """
        Update velocity command based on key press.

        Args:
            key: Key character
        """
        if key == 'w':
            self.current_vx = min(self.current_vx + self.vx_increment, self.vx_max)
        elif key == 's':
            self.current_vx = max(self.current_vx - self.vx_increment, -self.vx_max)
        elif key == 'a':
            self.current_omega_z = min(self.current_omega_z + self.omega_increment, self.omega_max)
        elif key == 'd':
            self.current_omega_z = max(self.current_omega_z - self.omega_increment, -self.omega_max)
        elif key == 'x':
            self.current_vx = 0.0
            self.current_omega_z = 0.0
        elif key == 'q':
            self.get_logger().info('Quit requested')
            return False
        else:
            # Unknown key, don't update
            return True

        # Publish updated command
        self.publish_command()

        # Print current state
        print(f'\rCommand: vx={self.current_vx:+.2f} m/s, omega_z={self.current_omega_z:+.2f} rad/s   ', end='', flush=True)

        return True

    def publish_command(self):
        """Publish current velocity command."""
        msg = VelocityCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'wbot_base'
        msg.vx = self.current_vx
        msg.omega_z = self.current_omega_z
        msg.target_joint_angles = []  # Empty means use current

        self.cmd_pub.publish(msg)

    def run(self):
        """
        Main command loop.

        Reads keyboard input and publishes velocity commands.
        """
        try:
            # Publish initial zero command
            self.publish_command()

            while rclpy.ok():
                # Get keyboard input (non-blocking)
                key = self.get_key()

                if key is not None:
                    if not self.update_command(key):
                        # Quit requested
                        break

                # Spin ROS callbacks
                rclpy.spin_once(self, timeout_sec=0.0)

        except KeyboardInterrupt:
            self.get_logger().info('\nKeyboard interrupt received')

        finally:
            # Send stop command before exiting
            self.current_vx = 0.0
            self.current_omega_z = 0.0
            self.publish_command()
            print('\n\nStopped. Exiting...\n')


def main(args=None):
    """Main entry point for the velocity command node."""
    rclpy.init(args=args)

    try:
        node = VelocityCommandNode()
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
