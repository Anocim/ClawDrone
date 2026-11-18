"""Bridge the Gazebo downward camera to ROS 2 and optionally start a viewer."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_setup(context):
    """Build the Gazebo topic name from the arguments and create the nodes."""
    world = LaunchConfiguration('world').perform(context)
    model = LaunchConfiguration('model').perform(context)
    link = LaunchConfiguration('link').perform(context)
    sensor = LaunchConfiguration('sensor').perform(context)
    show_window = LaunchConfiguration('show_window').perform(context) == 'true'
    # Gazebo topics: either given explicitly or built from the model/link/sensor names.
    image = LaunchConfiguration('gz_image_topic').perform(context)
    if not image:
        image = f'/world/{world}/model/{model}/link/{link}/sensor/{sensor}/image'
    info = LaunchConfiguration('gz_info_topic').perform(context)
    if not info:
        info = image.rsplit('/', 1)[0] + '/camera_info'
    actions = [
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='camera_down_bridge',
            arguments=[
                f'{image}@sensor_msgs/msg/Image[gz.msgs.Image',
                f'{info}@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            ],
            remappings=[
                (image, '/camera_down/image_raw'),
                (info, '/camera_down/camera_info'),
            ],
            output='screen',
        ),
    ]
    if LaunchConfiguration('viewer').perform(context) == 'true':
        actions.append(Node(
            package='f550_vision',
            executable='camera_viewer',
            parameters=[{'show_window': show_window}],
            output='screen',
        ))
    return actions


def generate_launch_description():
    """Declare the launch arguments and defer the node creation."""
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='tenis',
                              description='Gazebo world name'),
        DeclareLaunchArgument('model', default_value='f550_detailed_mono_cam_down_0',
                              description='Spawned model name, including the _N suffix'),
        DeclareLaunchArgument('link', default_value='camera_link',
                              description='Link that holds the camera sensor'),
        DeclareLaunchArgument('sensor', default_value='camera',
                              description='Name of the camera sensor'),
        DeclareLaunchArgument('gz_image_topic', default_value='',
                              description='Full Gazebo image topic; overrides the names above'),
        DeclareLaunchArgument('gz_info_topic', default_value='',
                              description='Gazebo camera_info topic; empty = beside the image'),
        DeclareLaunchArgument('viewer', default_value='true',
                              description='Start the camera_viewer node'),
        DeclareLaunchArgument('show_window', default_value='true',
                              description='Open an OpenCV preview window'),
        OpaqueFunction(function=_launch_setup),
    ])
