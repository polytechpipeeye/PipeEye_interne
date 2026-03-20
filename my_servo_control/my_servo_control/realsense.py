import rclpy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageSubscriber:
    def __init__(self):
        self.node = rclpy.create_node('image_subscriber')
        self.bridge = CvBridge()
        self.subscription = self.node.create_subscription(
            Image,
            '/camera/color/image_raw',  # Change this topic to your camera topic
            self.image_callback,
            10
        )
        self.subscription  # Prevent unused variable warning
        self.node.get_logger().info('Image subscriber node initialized')

    def image_callback(self, msg):
        print(1)
        try:
            print(2)
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            print(cv_image,type(cv_image))
            cv2.imshow("RGB Image", cv_image)
            cv2.waitKey(1)  # Adjust the delay as needed (1 millisecond in this case)
        except Exception as e:
            self.node.get_logger().error(f"Error converting image: {e}")

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    rclpy.spin(image_subscriber.node)
    image_subscriber.node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
