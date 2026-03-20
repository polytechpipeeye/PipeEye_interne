import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class XboxControllerNode(Node):

    def __init__(self):
        super().__init__('xbox_controller_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(Joy, 'joy', self.joy_callback, 10)
        self.joy_msg = Joy()
        self.joy_axes = []
        self.joy_buttons = []
        self.linear_scale = 0.5  # Scale for linear velocity
        self.angular_scale = 0.5  # Scale for angular velocity

    def joy_callback(self, msg):
        self.joy_msg = msg
        self.joy_axes = msg.axes
        self.joy_buttons = msg.buttons
        self.publish_twist()

    def publish_twist(self):
        twist_msg = Twist()
        if len(self.joy_axes) >= 4:
            # Assuming axes 0 and 1 are for left stick x and y, axes 3 and 4 for right stick x and y
            twist_msg.linear.x = self.linear_scale * self.joy_axes[1]  # Left stick y-axis
            twist_msg.angular.z = self.angular_scale * self.joy_axes[3]  # Right stick x-axis

        self.publisher_.publish(twist_msg)
        self.get_logger().info('Publishing Twist command: Linear=%.2f, Angular=%.2f' %
                               (twist_msg.linear.x, twist_msg.angular.z))

def main(args=None):
    rclpy.init(args=args)
    xbox_controller_node = XboxControllerNode()
    rclpy.spin(xbox_controller_node)
    xbox_controller_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
