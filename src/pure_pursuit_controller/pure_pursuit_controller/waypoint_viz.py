import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA, Int32
import csv
import os


class WaypointVisualizer(Node):
    def __init__(self):
        super().__init__("waypoint_visualizer")

        self.publisher = self.create_publisher(MarkerArray, "/wp_marker_array", 1)

        self.declare_parameter("waypoint_file", os.path.expanduser("~/waypoints.csv"))
        path = self.get_parameter("waypoint_file").get_parameter_value().string_value

        self.waypoints = self.load_waypoints(path)
        self.timer = self.create_timer(1.0, self.publish_markers)
        self.next_index = 0
        self.create_subscription(Int32, "/next_waypoint_index", self.index_callback, 10)

        self.get_logger().info(
            f"Publishing {len(self.waypoints)} waypoints to RViz from: {path}"
        )

    def index_callback(self, msg):
        self.next_index = msg.data

    def load_waypoints(self, path):
        points = []
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row["x"])
                y = float(row["y"])
                points.append((x, y))
        return points

    def publish_markers(self):
        marker_array = MarkerArray()
        total = len(self.waypoints)

        for i, (x, y) in enumerate(self.waypoints):
            m = Marker()
            m.header.frame_id = "map"
            m.header.stamp = self.get_clock().now().to_msg()
            m.ns = "waypoints"
            m.id = i
            m.type = Marker.SPHERE
            m.action = Marker.ADD
            m.pose.position.x = x
            m.pose.position.y = y
            m.pose.position.z = 0.1
            m.pose.orientation.w = 1.0
            m.scale.x = 0.3
            m.scale.y = 0.3
            m.scale.z = 0.3

            # Color gradient: green to red
            color = ColorRGBA()
            color.r = i / total
            color.g = 1.0 - (i / total)
            color.b = 0.0
            color.a = 1.0
            m.color = color

            marker_array.markers.append(m)

        # Highlight the current next waypoint
        if self.next_index < len(self.waypoints):
            next_marker = Marker()
            next_marker.header.frame_id = "map"
            next_marker.header.stamp = self.get_clock().now().to_msg()
            next_marker.ns = "next_waypoint"
            next_marker.id = 9999
            next_marker.type = Marker.SPHERE
            next_marker.action = Marker.ADD
            next_marker.pose.position.x = self.waypoints[self.next_index][0]
            next_marker.pose.position.y = self.waypoints[self.next_index][1]
            next_marker.pose.position.z = 0.3
            next_marker.pose.orientation.w = 1.0
            next_marker.scale.x = 0.5
            next_marker.scale.y = 0.5
            next_marker.scale.z = 0.5
            next_marker.color.r = 1.0
            next_marker.color.g = 0.0
            next_marker.color.b = 1.0
            next_marker.color.a = 1.0
            marker_array.markers.append(next_marker)

        self.publisher.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
