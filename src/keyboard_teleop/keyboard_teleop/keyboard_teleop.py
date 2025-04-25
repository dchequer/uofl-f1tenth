import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
import threading
import socket
import sys

MAX_SPEED = 2.0  # m/s, forward
MAX_REVERSE_SPEED = -1.0  # m/s, reverse
ACCEL_STEP = 0.1  # m/s per tick
STEER_ANGLE = 0.4189  # ~24 degrees in radians (100% left/right)
PUBLISH_HZ = 20


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("keyboard_teleop")
        self.pub = self.create_publisher(AckermannDriveStamped, "/drive", 10)
        self.speed = 0.0
        self.steering_angle = 0.0
        self.accel_pressed = False
        self.decel_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.running = True

        # max speed
        self.max_speed = MAX_SPEED
        self.max_reverse_speed = -self.max_speed

        # Start keyboard thread
        self.kb_thread = threading.Thread(target=self.keyboard_loop, daemon=True)
        self.kb_thread.start()

        # Start publish timer
        self.timer = self.create_timer(1.0 / PUBLISH_HZ, self.publish_cmd)

    def keyboard_loop(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 5555))
        server.listen(5)
        print("Waiting for key listener to connect...")

        def print_status():
            up = "↑" if self.accel_pressed else " "
            down = "↓" if self.decel_pressed else " "
            left = "←" if self.left_pressed else " "
            right = "→" if self.right_pressed else " "
            sys.stdout.write(
                f"\r[{up}] [{down}] [{left}] [{right}]  max: {self.max_speed:.1f} m/s  (ESC to quit)   "
            )
            sys.stdout.flush()

        while self.running:
            try:
                conn, _ = server.accept()
                data = conn.recv(1024).decode()
                if not data:
                    continue

                if data.startswith("DOWN:"):
                    key = data[5:].lower()
                    if "up" in key:
                        self.accel_pressed = True
                    elif "down" in key:
                        self.decel_pressed = True
                    elif "left" in key:
                        self.left_pressed = True
                    elif "right" in key:
                        self.right_pressed = True
                    elif "esc" in key:
                        self.running = False

                    # max speed controls
                    elif "w" in key:
                        self.max_speed = min(self.max_speed + 0.1, 5.0)
                    elif "s" in key:
                        self.max_speed = max(self.max_speed - 0.1, 0.5)

                elif data.startswith("UP:"):
                    key = data[3:].lower()
                    if "up" in key:
                        self.accel_pressed = False
                    elif "down" in key:
                        self.decel_pressed = False
                    elif "left" in key:
                        self.left_pressed = False
                    elif "right" in key:
                        self.right_pressed = False

                print_status()
            except Exception as e:
                print(f"Socket error: {e}")

    def publish_cmd(self):
        # Update speed
        if self.accel_pressed:
            self.speed = min(self.speed + ACCEL_STEP, self.max_speed)
        elif self.decel_pressed:
            self.speed = max(self.speed - ACCEL_STEP, self.max_reverse_speed)
        else:
            # Natural deceleration (optional: set to 0 for instant stop)
            if self.speed > 0:
                self.speed = max(self.speed - ACCEL_STEP, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + ACCEL_STEP, 0)

        # Update steering
        if self.left_pressed and not self.right_pressed:
            self.steering_angle = STEER_ANGLE
        elif self.right_pressed and not self.left_pressed:
            self.steering_angle = -STEER_ANGLE
        else:
            self.steering_angle = 0.0

        # Publish
        msg = AckermannDriveStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.drive.speed = float(self.speed)
        msg.drive.steering_angle = float(self.steering_angle)
        self.pub.publish(msg)

    def destroy_node(self):
        self.running = False
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    try:
        while rclpy.ok() and node.running:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    print("Starting keyboard teleoperation node")
    main()
