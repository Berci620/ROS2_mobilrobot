import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class TurtlebotClosestPoint(Node):
    def __init__(self):
        super().__init__('turtlebot_closest_point')

        closest_point = None

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.pub = self.create_publisher(
            Float32,
            '/closest_point',
            10
        )

    def scan_callback(self, msg):
        # Process the laser scan data
        self.closest_point = min(msg.ranges)
        if self.closest_point is not None:
            self.pub.publish(Float32(data=self.closest_point))
        


def main(args=None):
    rclpy.init(args=args)
    turtlebot_closest_point = TurtlebotClosestPoint()
    rclpy.spin(turtlebot_closest_point)
    turtlebot_closest_point.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()