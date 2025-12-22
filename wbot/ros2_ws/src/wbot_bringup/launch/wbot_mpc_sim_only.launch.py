#!/usr/bin/env python3
"""
Wbot MPC Simulation Launch File (Simulator + MPC only)

This launch file starts only the simulator and MPC nodes.
Run the command node separately in another terminal for keyboard control.

Terminal 1: ros2 launch wbot_bringup wbot_mpc_sim_only.launch.py
Terminal 2: ros2 run wbot_command velocity_command
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for Wbot MPC system."""

    # Declare launch arguments
    sim_freq_arg = DeclareLaunchArgument(
        'sim_frequency',
        default_value='100.0',
        description='Simulation frequency in Hz'
    )

    enable_viewer_arg = DeclareLaunchArgument(
        'enable_viewer',
        default_value='true',
        description='Enable MuJoCo viewer'
    )

    # MuJoCo Simulator Node
    mujoco_node = Node(
        package='wbot_simulator',
        executable='mujoco_node',
        name='wbot_mujoco',
        output='screen',
        parameters=[{
            'sim_frequency': LaunchConfiguration('sim_frequency'),
            'enable_viewer': LaunchConfiguration('enable_viewer'),
            'mujoco_xml': '/home/guanyu/crocoddyl/wbot/description/urdf/wbot_v2.xml',
            'publish_frequency': LaunchConfiguration('sim_frequency'),
        }],
        emulate_tty=True,
    )

    # MPC Solver Node
    mpc_config_path = os.path.join(
        get_package_share_directory('wbot_mpc'),
        'config',
        'mpc_params.yaml'
    )
    mpc_node = Node(
        package='wbot_mpc',
        executable='mpc_node',
        name='wbot_mpc',
        output='screen',
        parameters=[mpc_config_path],
        emulate_tty=True,
    )

    # Info message
    launch_info = LogInfo(
        msg=[
            '\n',
            '='*70, '\n',
            'Wbot MPC System Launched (Simulator + MPC only)\n',
            '='*70, '\n',
            'Running:\n',
            '  - wbot_mujoco: MuJoCo simulator @ ',
            LaunchConfiguration('sim_frequency'), ' Hz\n',
            '  - wbot_mpc: MPC solver (config file)\n',
            '\n',
            'To control the robot, open another terminal:\n',
            '  $ source /opt/ros/humble/setup.bash\n',
            '  $ source install/setup.bash\n',
            '  $ ros2 run wbot_command velocity_command\n',
            '\n',
            'Keyboard: w/s (vx), a/d (omega_z), x (stop), q (quit)\n',
            '='*70, '\n',
        ]
    )

    return LaunchDescription([
        # Arguments
        sim_freq_arg,
        enable_viewer_arg,

        # Info
        launch_info,

        # Nodes (no command node)
        mujoco_node,
        mpc_node,
    ])
