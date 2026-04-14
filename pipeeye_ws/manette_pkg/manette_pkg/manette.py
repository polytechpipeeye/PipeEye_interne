import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from std_msgs.msg import Int8

# Import du message personnalisé LEDControl
from my_robot_interface.msg import LedControl 

class MasterTeleopNode(Node):

    def __init__(self):
        super().__init__('master_teleop_node')
        
        # --- PUBLISHERS ---
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 1)
        self.tourelle_pub = self.create_publisher(Vector3, '/right_stick', 1) 
        self.led_pub = self.create_publisher(LedControl, '/LEDinput', 1)      
        self.publisher_zoom=self.create_publisher(Int8, 'camera/zoom_cmd', 1)
        self.screenshot_pub=self.create_publisher(Int8, '/camera/screenshot', 1)
        
        # subscription au noeud Joy qui envoie les informations analogiques de la dualshock
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        
        # --- VARIABLES D'ÉTAT TOURELLE---
        self.indiceVitesse = 1 # indice vitesse des moteurs tourelle
        self.indiceLED = 1 # indice intensity LED tourelle
        
        self.q1 = False # Croix
        self.q2 = False # Rond
        self.q3 = False # Triangle
        self.q4 = False # Carré
        
        # memoire
        self.last_buttons = []
        self.last_axes = []
        
        # --- LOGIQUE DU SWITCH (L2 indice 6) ---
        self.mode_tourelle = False      # Faux = Moteurs, Vrai = Tourelle
        self.button_switch = 7          # Index du bouton L2
        self.switch_press_time = None   # Mémorise l'heure du début de l'appui
        self.switch_hold_duration = 1.0 # Duree en secondes a maintenir pour basculer
        self.has_toggled = False        # Sécurité pour ne basculer qu'une seule fois par appui
        
        # Paramètres de conduite
        self.linear_scale = 0.5
        self.angular_scale = 0.5
        
        self.get_logger().info("Publisher at Work")
        self.last_pub_time=0.0
        self.last_led_time=0.0
        self.last_speed_time=0.0
        self.last_screenshot_time=0.0
        


    def joy_callback(self, msg):
        current_time = self.get_clock().now().nanoseconds / 1e9 # Temps actuel en secondes

        # GESTION DU SWITCH BLOQUANT (Appui long L2)
        # Vérifie si le bouton L2 (index 6) est enfoncé
        is_l2_pressed = (msg.buttons[self.button_switch] == 1)

        if is_l2_pressed:
            if self.switch_press_time is None:
                # Début de l'appui
                self.switch_press_time = current_time
                self.has_toggled = False
            else:
                # On maintient enfoncé, on vérifie si la durée est atteinte
                elapsed = current_time - self.switch_press_time
                if elapsed >= self.switch_hold_duration and not self.has_toggled:
                    # BASCULEMENT !
                    self.mode_tourelle = not self.mode_tourelle
                    self.has_toggled = True # Verrouillage pour éviter que ça clignote
                    
                    # Arrêt de sécurité immédiat des roues si on passe en mode tourelle
                    if self.mode_tourelle:
                        self.cmd_vel_pub.publish(Twist()) 
                        
                    self.get_logger().info(f"\n >>> CHANGEMENT DE MODE : {'TOURELLE ' if self.mode_tourelle else 'CONDUITE '} <<<\n")
        else:
            # On a relâché L2, on réinitialise le chronomètre
            self.switch_press_time = None
            self.has_toggled = False


        # GESTION DES BOUTONS
        if msg.buttons[0] == 1 and self.last_buttons[0] == 0: self.q1 = not self.q1 # Croix
        if msg.buttons[1] == 1 and self.last_buttons[1] == 0: self.q2 = not self.q2 # Rond
        if msg.buttons[2] == 1 and self.last_buttons[2] == 0: self.q3 = not self.q3 # Triangle
        if msg.buttons[3] == 1 and self.last_buttons[3] == 0: self.q4 = not self.q4 # Carré

        # Indice LED avec R1 (indice 5) : de 1 à 4
        if msg.buttons[5] == 1 and self.last_buttons[5] == 0:
        	if (current_time - self.last_led_time) >= 0.05:
        		self.indiceLED = self.indiceLED + 1 if self.indiceLED < 4 else 1
        		self.last_led_time=current_time
        # Indice Vitesse avec Flèche HAUT (indice 7) : de 1 à 3
        if len(msg.axes) >7 and len(self.last_axes) >7:
            if msg.axes[7] > 0.5 and self.last_axes[7] == 0.0:
            	if (current_time - self.last_speed_time) >= 0.05:
            		self.indiceVitesse = self.indiceVitesse + 1 if self.indiceVitesse < 3 else 1
            		self.last_speed_time=current_time
            elif msg.axes[7] < -0.5 and self.last_axes[7] == 0.0: #screenshot
            	if (current_time - self.last_screenshot_time) >= 0.05:
            		self.get_logger().info("capture d'écran")
            		msg_photo=Int8()
            		msg_photo.data=1
            		self.screenshot_pub.publish(msg_photo)
            		self.last_screenshot_time=current_time

        # Préparation de l'affichage visuel des LEDs
        s1 = "[X]" if self.q1 else "[ ]"
        s2 = "[X]" if self.q2 else "[ ]"
        s3 = "[X]" if self.q3 else "[ ]"
        s4 = "[X]" if self.q4 else "[ ]"


        # ENVOI DES COMMANDES SELON LE MODE
        if (current_time - self.last_pub_time) >= 0.05:
            if self.mode_tourelle:
            	# --- MODE TOURELLE --
            	tourelle_msg = Vector3()
            	# Transformation de [-1.0 ; 1.0] vers [0 ; 255]
            	# (On convertit en int() puis en float() pour avoir un 127 ou 255 propre sans décimales)
            	val_pan=msg.axes[3]
            	val_tilt=msg.axes[1]
            	if abs(val_pan)<0.15:
            		val_pan=0.0
            	if abs(val_tilt)<0.15:
            		val_tilt=0.0
            	tourelle_msg.x = float(int((val_pan * 127.0) + 127.0))
            	tourelle_msg.y = float(int((val_tilt * 127.0) + 127.0))
            	tourelle_msg.z = float(self.indiceVitesse)
            	self.tourelle_pub.publish(tourelle_msg)
            	led_msg = LedControl()
            	led_msg.intensity = int(self.indiceLED)
            	led_msg.q1 = self.q1
            	led_msg.q2 = self.q2
            	led_msg.q3 = self.q3
            	led_msg.q4 = self.q4
            	self.led_pub.publish(led_msg)
            	zoom_cmd=0
            	if msg.buttons[4]:
            		zoom_cmd=1
            		self.get_logger().info(f"Zoom Activé")
            	elif len(msg.axes)>2 and msg.axes[2] < 0.5:
            		zoom_cmd=-1
            		self.get_logger().info(f"Zoom Désactivé")
            	msg_zoom=Int8()
            	msg_zoom.data=zoom_cmd                    
            	self.publisher_zoom.publish(msg_zoom)
            	#affichage
            	self.get_logger().info(f"TOURELLE PIPEEYE")
            	self.get_logger().info(
            		f"STICK G({(msg.axes[1]*127.0)+127.0:.2f}) "
            	 	f"D({(msg.axes[3]*127.0)+127.0:.2f}) | "
		        f"VIT: {self.indiceVitesse} | "
		        f"LUM: {self.indiceLED} | LED {s1}{s2}{s3}{s4} "
		)
            else:	
            	# --- MODE CONDUITE ---
            	twist_msg = Twist()
            	twist_msg.linear.x = self.linear_scale * msg.axes[1]  
            	twist_msg.angular.z = self.angular_scale * msg.axes[3]
            	self.cmd_vel_pub.publish(twist_msg)
            	self.get_logger().info(f"CONDUITE ")
            	self.get_logger().info(
            	f"STICK G({msg.axes[0]:.2f}, {msg.axes[1]:.2f}) "
            	f"D({msg.axes[3]:.2f}, {msg.axes[4]:.2f}) | "
            	f"Vit. Moteur: {twist_msg.linear.x:.2f} | Rot: {twist_msg.angular.z:.2f} | "
            	f"LED {s1}{s2}{s3}{s4} "
            	)
            self.last_pub_time=current_time
            	
	

        # Mise à jour mémoire
        self.last_buttons = list(msg.buttons)
        self.last_axes = list(msg.axes)

def main(args=None):
    rclpy.init(args=args)
    master_node = MasterTeleopNode()
    try:
        rclpy.spin(master_node)
    except KeyboardInterrupt:
        master_node.get_logger().info("Arrêt du programme")
    finally:
        master_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
