from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="pure_pursuit_controller",
                executable="pure_pursuit",
                name="pure_pursuit_node",
                output="screen",
            ),
            Node(
                package="pure_pursuit_controller",
                executable="waypoint_viz",
                name="waypoint_visualizer_node",
                output="screen",
            ),
        ]
    )
