import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_name = 'my_bot'  # <--- CHANGE ME si besoin

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )
   # Path vers le fichier world vide
    world_path = os.path.join(
        get_package_share_directory("my_bot"),
        'worlds',
        'empty.world' 
    )

    # Gazebo (via ros_gz_sim)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r ', world_path], 
            'on_exit_shutdown': 'true'}.items()
    )

    # Spawner: insère le robot après un petit délai
    spawn_entity = TimerAction(
        period=5.0,
        actions=[ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_sim', 'create',
                '-topic', '/robot_description',
                '-name', 'my_bot',
                '-x', '0', '-y', '0', '-z', '0.1'
            ],
            output='screen'
        )]
    )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    return LaunchDescription([
        gazebo,
        rsp,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner
    ])