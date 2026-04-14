import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int8
from cv_bridge import CvBridge
import cv2
import os
from datetime import datetime

class ScreenshotNode(Node):
	def __init__(self):
		super().__init__('screenshot_node')
		self.save_path=os.path.expanduser('~/Pictures/RobotScreenshots')
		if not os.path.exists(self.save_path):
			os.makedirs(self.save_path)
			self.get_logger().info(f"Dossier créé : {self.save_path}")
		self.bridge=CvBridge()
		self.latest_frame=None
		self.image_sub=self.create_subscription(Image, '/camera/image_hud',self.image_callback,10)
		self.trigger_sub=self.create_subscription(Int8, '/camera/screenshot',self.trigger_callback,10)
		self.get_logger().info(f"noeud capture pret")
	
	def image_callback(self,msg):
		try:
			self.latest_frame=self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
		except Exception as e:
			self.get_logger().error(f"Erreur conversion image : {e}")
	
	def trigger_callback(self,msg):
		if msg.data==1:
			if self.latest_frame is not None:
				now=datetime.now()
				filename=now.strftime("capture_%d%m%Y_%H%M%S.png")
				full_path=os.path.join(self.save_path, filename)
				cv2.imwrite(full_path,self.latest_frame)
				self.get_logger().info(f"Photo sauvegardée : {full_path}")
			else:
				self.get_logger().warn("impossible de prendre la photo aucun flux camera recu")

def main(args=None):
    rclpy.init(args=args)
    node=ScreenshotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
