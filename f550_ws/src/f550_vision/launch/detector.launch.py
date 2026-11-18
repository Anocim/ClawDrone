"""Start the camera bridge and the YOLO ball detector."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Include the camera bridge (without viewer) and add the detector node."""
    camera_launch = os.path.join(
        get_package_share_directory('f550_vision'), 'launch', 'camera.launch.py')
    return LaunchDescription([
        DeclareLaunchArgument('model_path',
                              description='Absolute path to the YOLO .pt file'),
        DeclareLaunchArgument('world', default_value='tenis'),
        DeclareLaunchArgument('model', default_value='f550_detailed_mono_cam_down_0'),
        DeclareLaunchArgument('link', default_value='camera_link'),
        DeclareLaunchArgument('sensor', default_value='camera'),
        DeclareLaunchArgument('gz_image_topic', default_value=''),
        DeclareLaunchArgument('gz_info_topic', default_value=''),
        DeclareLaunchArgument('conf_threshold', default_value='0.4'),
        DeclareLaunchArgument('target_labels', default_value='',
                              description='Comma-separated class names; empty keeps all'),
        DeclareLaunchArgument('max_rate_hz', default_value='5.0'),
        DeclareLaunchArgument('device', default_value='',
                              description="Empty = automatic; 'cpu' or '0' to force"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(camera_launch),
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'model': LaunchConfiguration('model'),
                'link': LaunchConfiguration('link'),
                'sensor': LaunchConfiguration('sensor'),
                'gz_image_topic': LaunchConfiguration('gz_image_topic'),
                'gz_info_topic': LaunchConfiguration('gz_info_topic'),
                'viewer': 'false',
            }.items(),
        ),
        Node(
            package='f550_vision',
            executable='ball_detector',
            parameters=[{
                'model_path': ParameterValue(LaunchConfiguration('model_path'), value_type=str),
                'conf_threshold': ParameterValue(
                    LaunchConfiguration('conf_threshold'), value_type=float),
                'target_labels': ParameterValue(
                    LaunchConfiguration('target_labels'), value_type=str),
                'max_rate_hz': ParameterValue(
                    LaunchConfiguration('max_rate_hz'), value_type=float),
                'device': ParameterValue(LaunchConfiguration('device'), value_type=str),
            }],
            output='screen',
        ),
    ])
