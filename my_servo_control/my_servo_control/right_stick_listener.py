#!/usr/bin/env python3

import rclpy
import sys
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from my_robot_interface.msg import LedControl

class RobotListener(Node):
    def __init__(self):
        super().__init__('robot_listener')

        # --- ÉTATS INTERNES (Mémorisation) ---
        self.x = 0.0
        self.y = 0.0
        self.vitesse = 1
        self.intensity = 1
        self.q = [False, False, False, False] # q1, q2, q3, q4

        # --- ABONNEMENTS ---
        # 1. Topic Moteurs / Joystick
        self.sub_joy = self.create_subscription(Vector3, 'right_stick', self.joy_callback, 10)
        
        # 2. Topic LED
        self.sub_led = self.create_subscription(LedControl, 'LEDinput', self.led_callback, 10)

        self.get_logger().info("Listener Ready - En attente de données...")

    def joy_callback(self, msg: Vector3):
        # Mise à jour des valeurs joystick
        self.x = msg.x
        self.y = msg.y
        self.vitesse = int(msg.z)
        self.afficher_ligne_complete()

    def led_callback(self, msg: LedControl):
        # Mise à jour des valeurs LED
        self.intensity = msg.intensity
        self.q = [msg.q1, msg.q2, msg.q3, msg.q4]
        self.afficher_ligne_complete()

    def afficher_ligne_complete(self):
        # Préparation du visuel des quartiers
        s = [" [X] " if val else " [ ] " for val in self.q]
        visuel_led = "".join(s)

        # Construction de la ligne unique
        # :6.1f permet de bloquer la largeur des nombres pour que la ligne ne saute pas
        log_msg = (
            f"STICK: x={self.x:6.1f} y={self.y:6.1f} | "
            f"VIT: {self.vitesse} | "
            f"LUM: {self.intensity} | "
            f"LED: {visuel_led}"
        )
        
        self.get_logger().info(log_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RobotListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
