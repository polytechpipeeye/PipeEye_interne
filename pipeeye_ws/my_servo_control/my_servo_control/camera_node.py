import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        
        # 1. Publisher : Envoie l'image sur le réseau ROS
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)
        
        # 2. Timer : Capture une image 20 fois par seconde (20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)
        
        # 3. Initialisation Caméra
        # L'index 0 est généralement la première caméra USB branchée
        self.cap = cv2.VideoCapture(0)
        
        # Outil de conversion OpenCV <-> ROS
        self.br = CvBridge()
        
        if not self.cap.isOpened():
            self.get_logger().error("ERREUR : Impossible d'ouvrir la caméra !")
        else:
            self.get_logger().info("Caméra activée et publication sur /video_frames")

    def timer_callback(self):
        # Lecture d'une frame
        ret, frame = self.cap.read()
        
        if ret:
            # A. Affichage local (Ouvre une fenêtre sur le Pi)
            # Note : Nécessite un écran branché au Pi ou du X11 Forwarding
            cv2.imshow("Vue Robot", frame)
            cv2.waitKey(1) # Nécessaire pour rafraîchir l'image OpenCV
            
            # B. Publication ROS
            # On convertit l'image OpenCV (BGR) en message ROS
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame, "bgr8"))
        else:
            self.get_logger().warning("Erreur lecture frame")

    def destroy_node(self):
        # Libération propre de la caméra
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    camera_node = CameraNode()
    try:
        rclpy.spin(camera_node)
    except KeyboardInterrupt:
        pass
    finally:
        camera_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
