# Pure Pursuit Controller

This package implements a Pure Pursuit path tracking algorithm for autonomous vehicles, specifically designed for F1Tenth/Roboracer platforms. It includes tools for waypoint recording, visualization, and path tracking.

## Features

- **Waypoint Recorder**: Record waypoints using RViz's 2D Goal Pose tool.
- **Waypoint Visualizer**: Visualize waypoints in RViz with color gradients and highlight the next waypoint.
- **Pure Pursuit Node**: Perform path tracking using the Pure Pursuit algorithm.

## Installation

1. Clone the repository into your ROS 2 workspace.
2. Build the workspace using `colcon build --packages-select pure_pursuit_controller`.

## Usage

**Reminder**: Always run the following commands before using this package:

```bash
source /opt/ros/galactic/setup.bash
cd autoware && . install/setup.bash
```

- Launch the nodes using the provided launch file:
  ```bash
  ros2 launch pure_pursuit_controller pure_pursuit.launch.py
  ```
- Record waypoints by clicking 2D Goal Pose in RViz. (TODO: currently you need to manually run "waypoint_recorder")
- Visualize waypoints and track the path in real-time.
- Send commands to car to drive.

## Dependencies

- ROS 2
- `rclpy`, `geometry_msgs`, `nav_msgs`, `ackermann_msgs`, `visualization_msgs`

## License

This project is licensed under the MIT License.
