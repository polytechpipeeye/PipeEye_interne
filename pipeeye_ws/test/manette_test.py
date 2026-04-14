#!/usr/bin/env python3

import threading
import math
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Vector3
from my_robot_interface.msg import LedControl # importer msg personnalisé pour la LED

from evdev import InputDevice, categorize, ecodes, list_devices
from std_msgs.msg import Int8
from rcl_interfaces.msg import Log

def difference(a, b):
    # Retourne la différence absolue entre deux valeurs, sert pour le filtrage
    return abs(a - b)


def find_ps4_controller():
    # récuperer une liste devices depuis list devices
    devices = [InputDevice(path) for path in list_devices()]
    for dev in devices:
        # si dev.name contient "Sony" ou "Wireless", retourner dev
        if "Wireless" in dev.name or "Sony" in dev.name:
            return dev
    return None


class RightStickPublisher(Node):
    """
    Node ROS2 qui lit le joystick droit (axes ABS_RX, ABS_RY)
    d'une manette PS4 branchée en USB et publie les valeurs brutes (0 à 255)
    sur le topic nommé /right_stick sous la forme d'un Vector3 (x = RX, y = RY, z = 0).
    """

    def __init__(self):
        super().__init__('stick_publisher') # déclarer noeud nommé stick_publisher
        self.log_sub=self.create_subscription(Log,"/rosout",self.rosout_callback,10); 
        # On récupère la manette via evdev
        gamepad = find_ps4_controller()  # variable locale

        # On vérifie si on a trouvé quelque chose
        if gamepad is None:
            self.get_logger().error("Manette PS4 non trouvée. Branche-la en USB et réessaie.") # error print si pas de manette
            raise SystemExit # sortie du programme

        # on passe la variable locale en variable globale
        self.gamepad = gamepad

        self.get_logger().info(f"Manette détectée : {self.gamepad.name} sur {self.gamepad.path}") # simple print pour confirmer la connexion avec la manette

        # attributs : valeurs courantes des joysticks (axes RX et LY)
        
        # variables zone morte
        self.deadzone_radius = 20.0  # Rayon de la zone morte réglable (0 à 127)
        self.center_val = 127.5      # Centre d'un axe 0-255
        
        self.rx = 0.0
        self.ly = 0.0
        self.indiceVitesse = 1.0
        self.indiceLED = 1.0
        self.flagFlèche = False
        self.padOldState = 0
        
        self.q1 = False
        self.q2 = False
        self.q3 = False
        self.q4 = False
        #self.is_red=False
        #self.padOldStateX=0
        
        # déclarer un publisher "right_stick" de type Vector3
        # déclarer un publisher "LEDinput" de type LedControl (personnalisé)
        self.publisher_ = self.create_publisher(Vector3, 'right_stick', 10)
        self.publisherLED = self.create_publisher(LedControl, 'LEDinput', 10)
        self.publisher_zoom=self.create_publisher(Int8, 'camera/zoom_cmd', 10)
        self.zoom_cmd=0
        # thread dédié à la lecture bloquante de la manette
        self.joy_thread = threading.Thread(
            target=self.joystick_loop,
            daemon=True
        )
        
        self.joy_thread.start() # lancer la méthode à executer
        self.get_logger().info("Thread de lecture joystick lancé.") # print pour l'annoncer
        self.get_logger().info(f"Vitesse initiale : {self.indiceVitesse}")
        self.get_logger().info(f"Indice LED initial : {self.indiceLED}")

    def rosout_callback(self,msg):
    	if "AXE" in msg.msg :
    	    print(f":{msg.msg}")
    	
    def changeSpeedIndex(self):
        if self.indiceVitesse == 1:
            self.indiceVitesse = 2
        elif self.indiceVitesse == 2:
            self.indiceVitesse = 3
        elif self.indiceVitesse == 3:
            self.indiceVitesse = 1
        else:
            self.indiceVitesse = 1
            
    def changeLEDindex(self):
        if self.indiceLED == 1:
            self.indiceLED = 2
        elif self.indiceLED == 2:
            self.indiceLED = 3
        elif self.indiceLED == 3:
            self.indiceLED = 4
        elif self.indiceLED == 4:
            self.indiceLED = 1
        else:
            self.indiceLED = 1

    def joystick_loop(self):
        """
        Boucle bloquante exécutée dans un thread séparé.
        """
        try:
            for event in self.gamepad.read_loop():
            
                # Filtre : on n'accepte que les axes ou les touches
                if event.type not in [ecodes.EV_ABS, ecodes.EV_KEY]:
                    continue

                changed = False
                
                # --- BLOC DES BOUTONS ---

                # creation et initialisation du message msgLED de type LedControl
                
                msgLED = LedControl()
                msgLED.intensity = int(self.indiceLED)
                            
                if event.type == ecodes.EV_KEY:
                    if event.code == ecodes.BTN_TL: # L1
                        if event.value==1:
                            self.zoom_cmd=1
                        else :
                            self.zoom_cmd=0
                        msg_zoom=Int8()
                        msg_zoom.data=self.zoom_cmd
                        self.publisher_zoom.publish(msg_zoom)
                        self.get_logger().info(f"Zoom Activé")
                    elif event.code == ecodes.BTN_TR2: # R2
                        if event.value==1:
                            self.zoom_cmd=-1
                        else:
                            self.zoom_cmd=0
                        msg_zoom=Int8()
                        msg_zoom.data=self.zoom_cmd
                        self.publisher_zoom.publish(msg_zoom)
                        self.get_logger().info(f"Zoom Désactivé")
                    if event.value == 1: # Appui
                        button_pressed = True
                        
                        if event.code == ecodes.BTN_SOUTH: # Croix
                            self.q1 = not self.q1
                        elif event.code == ecodes.BTN_EAST: # Rond
                            self.q2 = not self.q2
                        elif event.code == ecodes.BTN_NORTH: # Triangle
                            self.q3 = not self.q3
                        elif event.code == ecodes.BTN_WEST: # Carré
                            self.q4 = not self.q4
                        elif event.code == ecodes.BTN_TR: # R1
                            self.changeLEDindex()
                        
                        else:
                            button_pressed = False

                        if button_pressed == True:
                            msgLED = LedControl()
                            msgLED.intensity = int(self.indiceLED)
                            msgLED.q1 = self.q1
                            msgLED.q2 = self.q2
                            msgLED.q3 = self.q3
                            msgLED.q4 = self.q4
                            #msgLED.is_red=self.is_red
                        
                            # --- AFFICHAGE VISUEL [X] [ ] ---
                            s1 = "[X]" if self.q1 else "[ ]"
                            s2 = "[X]" if self.q2 else "[ ]"
                            s3 = "[X]" if self.q3 else "[ ]"
                            s4 = "[X]" if self.q4 else "[ ]"
                            #s5= "[RED]" if self.is_red else "[WHITE]"
                                
                            self.get_logger().info(f"STICK: x= {msg.x} y= {msg.y} | VIT: {msg.z} | LUM: {msgLED.intensity} | LED {s1}{s2}{s3}{s4}")
                            
                            # publication ROS                        
                            self.publisherLED.publish(msgLED)
                            
                            
                    # On continue la boucle pour ne pas traiter le bouton comme un axe
                    continue 
                
                # --- BLOC DES AXES ---
                abs_event = categorize(event)
                axis = ecodes.ABS[abs_event.event.code]
                value = abs_event.event.value
                
                if axis == "ABS_RX":
                    if self.rx is None or difference(self.rx, value) >= 2:
                        self.rx = value
                        changed = True

                elif axis == "ABS_Y":
                    if self.ly is None or difference(self.ly, value) >= 2:
                        self.ly = value
                        changed = True
                        
                elif axis == "ABS_HAT0Y":
                    if value != self.padOldState:
                        if value == -1:  # Flèche HAUT
                            self.changeSpeedIndex()
                            changed = True 

                        self.padOldState = value
                #elif axis == "ABS_HAT0X":
                    #if value != self.padOldStateX:
                        #if value == -1:  # Flèche Gauche
                            #self.is_red= not self.is_red
                            #changed = True 
                        #self.padOldStateX = value
                        
                # publication ros
                if changed:
                    msg = Vector3()
                    # initialisation des valeurs à envoyer
                    msg.x = float(self.rx)
                    msg.y = float(self.ly)
                    msg.z = float(self.indiceVitesse)
                    # envoi et print du "message"
                    self.publisher_.publish(msg)
                    self.get_logger().info(f"STICK: x= {msg.x}, y= {msg.y} | VIT ={msg.z} ||")

        except OSError as e:
            self.get_logger().error(f"Erreur lors de la lecture de la manette : {e}")


def main(args=None):
    rclpy.init(args=args)
    node = RightStickPublisher()
    
    try:
        # Lance le processing des callbacks ROS2
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Message propre lors du Ctrl+C
        node.get_logger().info("Arrêt du programme")
    finally:
        # Destruction du node et fermeture propre de ROS2
        node.destroy_node()
        rclpy.shutdown()
        print("\nNode stick_publisher fermé")


if __name__ == '__main__':
    main()
