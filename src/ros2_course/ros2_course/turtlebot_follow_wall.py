import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Float32
from collections import deque


class FollowWall(Node):

    def __init__(self, desired_distance, desired_speed=0.5):
        super().__init__('follow_wall')
        self.desired_distance = desired_distance
        self.desired_speed = desired_speed
        self.angular_velocity = 0.0
        self.prev_error = 0.0
        self.integral = deque([0.0] * 100, maxlen=100)
        # self.max_abs_error = 0.0
        self.twist_pub = self.create_publisher(
            Twist, '/cmd_vel', 10)

        self.pose = None
        self.subscription = self.create_subscription(
                                       Float32,
                                       '/closest_point',
                                       self.cb_calc_angular_vel,
                                       10)

    # Calculating angular velocity based on the closest point
    def cb_calc_angular_vel(self, msg):
        self.get_logger().info(f'Closest point: {msg.data}')
        d = self.desired_distance - msg.data
        self.get_logger().info(f'Error: {d}')
        # if(abs(d) > self.max_abs_error):
        #     self.max_abs_error = abs(d)
        # d = d / self.max_abs_error
        Kp = 10.0 # Proportional gain
        Ki = 0.1 # Integral gain
        Kd = 40.0 # Derivative gain

        self.integral.append(d)
        derivative = d - self.prev_error
        self.prev_error = d

        if(d < 0):
            self.angular_velocity = (Kp * d + Ki * sum(self.integral) + Kd * derivative)/(Kp + Ki + Kd)*0.5/2
        else:
            self.angular_velocity = (Kp * d + Ki * sum(self.integral) + Kd * derivative)/(Kp + Ki + Kd)*0.5/0.7

        self.get_logger().info(f'Angular velocity: {self.angular_velocity}')
        self.go(self.desired_speed)

    def go(self, speed):
        # Create and publish msg
        vel_msg = Twist()
        vel_msg.linear.x = speed
        vel_msg.linear.y = 0.0
        vel_msg.linear.z = 0.0
        vel_msg.angular.x = 0.0
        vel_msg.angular.y = 0.0
        vel_msg.angular.z = self.angular_velocity

        self.twist_pub.publish(vel_msg)
        self.get_logger().info(f'Published velocity: {vel_msg}')



def main(args=None):
    rclpy.init(args=args)
    fw = FollowWall(desired_distance=1.0, desired_speed=0.5)
    rclpy.spin(fw)
    fw.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()