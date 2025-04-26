import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import csv
import os


class WaypointRecorder(Node):
    def __init__(self):
        super().__init__("waypoint_recorder")

        self.output_file = os.path.join(os.path.expanduser("~"), "waypoints.csv")
        self.waypoints = []

        self.subscription = self.create_subscription(
            PoseStamped, "/goal_pose", self.goal_pose_callback, 10
        )

        self.get_logger().info(
            f"Waypoint Recorder Ready! Click 2D Goal Pose in RViz to record points to {self.output_file}"
        )

    def goal_pose_callback(self, msg):
        x = msg.pose.position.x
        y = msg.pose.position.y
        self.waypoints.append((x, y))
        self.get_logger().info(f"Saved waypoint: x={x:.2f}, y={y:.2f}")
        self.save_to_csv()

    def save_to_csv(self):
        with open(self.output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y"])
            for wp in self.waypoints:
                writer.writerow([wp[0], wp[1]])


def main(args=None):
    rclpy.init(args=args)
    node = WaypointRecorder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
