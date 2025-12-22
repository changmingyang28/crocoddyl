#!/usr/bin/env python3
"""
Wbot MPC System Launch File

This launch file starts the complete Wbot MPC system:
1. MuJoCo Simulator Node - Main simulation loop (100Hz)
2. MPC Solver Node - Optimal control solver (asynchronous)
3. Velocity Command Node - User interface (keyboard)

Architecture follows OCS2 design pattern:
- Simulator runs the main loop
- MPC responds to state updates
- Command node allows interactive control
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# Note: No need for conda paths when using system Python
# All dependencies (mujoco, crocoddyl, pinocchio) are installed system-wide


def generate_launch_description():
    """Generate launch description for Wbot MPC system."""

    # No special environment setup needed for system Python installation

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
            'mujoco_xml': '/home/guanyu/crocoddyl/wbot/description/scene.xml',
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

    # Velocity Command Node (interactive keyboard interface)
    # Note: Removed xterm prefix - run in same terminal for now
    # To run in separate terminal, manually start: ros2 run wbot_command velocity_command
    command_node = Node(
        package='wbot_command',
        executable='velocity_command',
        name='wbot_velocity_command',
        output='screen',
        emulate_tty=True,
    )

    # Info message
    launch_info = LogInfo(
        msg=[
            '\n',
            '='*70, '\n',
            'Wbot MPC System Launched\n',
            '='*70, '\n',
            'Nodes:\n',
            '  - wbot_mujoco: MuJoCo simulator (main loop @ ',
            LaunchConfiguration('sim_frequency'), ' Hz)\n',
            '  - wbot_mpc: MPC solver (config file)\n',
            '  - wbot_velocity_command: Keyboard interface\n',
            '\n',
            'Topics:\n',
            '  - /wbot/state: Robot state (published by simulator)\n',
            '  - /wbot/control: Control commands (published by MPC)\n',
            '  - /wbot/cmd_vel: Velocity commands (published by command node)\n',
            '  - /wbot/mpc_performance: MPC performance metrics\n',
            '\n',
            'Usage:\n',
            '  - Use the command terminal to control the robot (w/a/s/d/x/q)\n',
            '  - Watch the MuJoCo viewer for visualization\n',
            '  - Monitor terminal output for performance metrics\n',
            '='*70, '\n',
        ]
    )

    return LaunchDescription([
        # Arguments
        sim_freq_arg,
        enable_viewer_arg,

        # Info
        launch_info,

        # Nodes
        mujoco_node,
        mpc_node,
        command_node,
    ])
