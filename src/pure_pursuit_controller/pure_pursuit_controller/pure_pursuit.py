import rclpy
from rclpy.node import Node
import math
import csv
import os
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from ackermann_msgs.msg import AckermannDriveStamped
from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import Int32


class WaypointLoader:
    def __init__(self, csv_file_path):
        self.waypoints = self.load_csv(csv_file_path)

    def load_csv(self, path):
        waypoints = []
        with open(path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                x, y = float(row[0]), float(row[1])
                waypoints.append((x, y))
        return waypoints


class PurePursuitNode(Node):
    def __init__(self):
        super().__init__("pure_pursuit_node")

        self.declare_parameter("lookahead_distance", 10.0)
        self.lookahead_distance = (
            self.get_parameter("lookahead_distance").get_parameter_value().double_value
        )

        # Load waypoints
        pkg_path = get_package_share_directory("pure_pursuit_controller")
        user_path = os.path.expanduser("~/waypoints.csv")
        if os.path.exists(user_path):
            wp_path = user_path
            self.get_logger().info(f"Using user-generated waypoints from {user_path}")
        else:
            wp_path = os.path.join(pkg_path, "waypoints", "waypoints.csv")
            self.get_logger().info(f"Using default waypoints from {wp_path}")

        self.waypoints = WaypointLoader(wp_path).waypoints
        print(f"Loaded {len(self.waypoints)} waypoints from {wp_path}")
        self.wp_index_pub = self.create_publisher(Int32, "/next_waypoint_index", 10)

        self.current_pose = None
        self.current_waypoint_index = 0
        self.arrival_threshold = 2.0
        self.speed = 2.5  # Target speed
        self.actual_speed = 0.0

        self.create_subscription(Odometry, "/ego_racecar/odom", self.odom_callback, 10)
        self.cmd_pub = self.create_publisher(AckermannDriveStamped, "/drive", 10)

        self.timer = self.create_timer(0.05, self.timer_callback)

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose
        vx = msg.twist.twist.linear.x
        vy = msg.twist.twist.linear.y
        self.actual_speed = math.hypot(vx, vy)

    def timer_callback(self):
        if self.current_pose is None:
            return

        # No more waypoints
        if self.current_waypoint_index >= len(self.waypoints):
            self.stop_drive()  # stop the car
            self.get_logger().info("All waypoints reached. Stopping.")
            return

        # Current target waypoint
        target_wp = self.waypoints[self.current_waypoint_index]
        cx = self.current_pose.position.x
        cy = self.current_pose.position.y
        distance = math.hypot(target_wp[0] - cx, target_wp[1] - cy)

        # Check if we have reached the waypoint
        if distance < self.arrival_threshold:
            self.current_waypoint_index += 1
            self.get_logger().info(
                f"Reached waypoint {self.current_waypoint_index - 1}, moving to {self.current_waypoint_index}"
            )
            # Publish the updated waypoint index
            index_msg = Int32()
            index_msg.data = self.current_waypoint_index
            self.wp_index_pub.publish(index_msg)
            return  # wait until next cycle

        steering_angle = self.compute_steering_angle(target_wp)
        self.publish_drive(steering_angle)

    def find_lookahead_point(self):
        cx = self.current_pose.position.x
        cy = self.current_pose.position.y

        for i, (wx, wy) in enumerate(self.waypoints):
            dx = wx - cx
            dy = wy - cy
            distance = math.hypot(dx, dy)
            if distance >= self.lookahead_distance:
                return (wx, wy), i
        return None, None

    def compute_steering_angle(self, lookahead_point):
        lx, ly = lookahead_point
        px = self.current_pose.position.x
        py = self.current_pose.position.y

        # Orientation as yaw
        q = self.current_pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        # Transform point to vehicle coordinates
        dx = lx - px
        dy = ly - py

        x_r = math.cos(-yaw) * dx - math.sin(-yaw) * dy
        y_r = math.sin(-yaw) * dx + math.cos(-yaw) * dy

        if x_r == 0:
            return 0.0

        curvature = (2 * y_r) / (self.lookahead_distance ** 2)
        return curvature

    def publish_drive(self, steering_angle):
        max_steering_angle = 0.4189  # radians (24 degrees)
        angle_ratio = abs(steering_angle) / max_steering_angle
        speed = self.speed * (1.0 - 0.5 * angle_ratio)

        drive_msg = AckermannDriveStamped()
        drive_msg.header.frame_id = "base_link"
        drive_msg.header.stamp = self.get_clock().now().to_msg()
        drive_msg.drive.steering_angle = max(
            min(steering_angle, self.max_steering_angle), -self.max_steering_angle
        )
        drive_msg.drive.speed = speed
        self.cmd_pub.publish(drive_msg)

    def stop_drive(self):
        drive_msg = AckermannDriveStamped()
        drive_msg.header.frame_id = "base_link"
        drive_msg.header.stamp = self.get_clock().now().to_msg()
        drive_msg.drive.steering_angle = 0.0
        drive_msg.drive.speed = 0.0
        self.cmd_pub.publish(drive_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PurePursuitNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
