import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

class FollowWall(Node):

    def __init__(self, desired_distance, desired_speed=0.5):
        super().__init__('follow_wall')
        self.desired_distance = desired_distance
        self.desired_speed = desired_speed
        
        # PID State Variables
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        # Physical Limits
        self.max_angular_vel = 1.0  # Maximum allowed turning speed (rad/s)
        
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Float32, '/closest_point', self.cb_calc_angular_vel, 10)

    def cb_calc_angular_vel(self, msg):
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0.0:
            return  # Prevent division by zero on first callback
            
        error = self.desired_distance - msg.data
        self.get_logger().info(f'-------------------------------------------------------------- ')
        self.get_logger().info(f'Error: {error:.2f}, Distance: {msg.data:.2f}')
        
        # 1. Gain Scheduling (Asymmetric reactions)
        if error > 0:
            # TOO CLOSE: Aggressive gains to avoid crashing
            Kp = 1.65
            Ki = -0.0
            Kd = 1.5
        else:
            # TOO FAR: Smoother, relaxed gains to slowly return to the wall
            Kp = 0.9
            Ki = -0.0
            Kd = 1.5

        # 2. Standard PID Math (using true time 'dt')
        proportional = Kp * error
        derivative = Kd * ((error - self.prev_error) / dt)
        
        # Calculate tentative output for anti-windup check
        raw_angular = proportional + (Ki * (self.integral + error * dt)) + derivative
        
        # Anti-Windup: Only accumulate integral if we aren't already at max turning speed
        if -self.max_angular_vel <= raw_angular <= self.max_angular_vel:
            self.integral += error * dt
            
        integral_term = Ki * self.integral

        # Final PID Output
        final_angular = proportional + integral_term + derivative

        # 3. Hard Clamping the Output
        # This guarantees the robot never exceeds your set maximum turning speed
        safe_angular = max(-self.max_angular_vel, min(self.max_angular_vel, final_angular))

        self.prev_error = error
        self.last_time = current_time

        self.go(safe_angular)

    def go(self, angular_vel):
        vel_msg = Twist()
        
        # 4. Dynamic Linear Velocity Scaling
        # If turning sharply, slow down the forward speed. 
        # If driving straight (angular_vel ~ 0), drive at desired_speed.
        speed_penalty = abs(angular_vel) * 1.8
        if angular_vel > 0:
            speed_penalty *= 1.2
        safe_linear_speed = max(0.1, self.desired_speed - speed_penalty)
        
        vel_msg.linear.x = safe_linear_speed
        vel_msg.angular.z = angular_vel

        self.twist_pub.publish(vel_msg)
        self.get_logger().info(f'Lin: {safe_linear_speed:.2f}, Ang: {angular_vel:.2f}')

def main(args=None):
    rclpy.init(args=args)
    fw = FollowWall(desired_distance=0.8, desired_speed=1.0)
    rclpy.spin(fw)
    fw.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()