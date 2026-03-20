import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
import RPi.GPIO as G
import time

servo_pin_x=23
servo_pin_y=22
G.setmode(G.BCM)
G.setup(servo_pin_x, G.OUT)
G.setup(servo_pin_y, G.OUT)
pwm_x=G.PWM(servo_pin_x, 50)
pwm_y=G.PWM(servo_pin_y, 50)
pwm_x.start(0)
pwm_y.start(0)
stop=7.0
duree_max=3.0  # secondes max dans le même sens
# Vitesse axe X
VX={
    1: {"gauche": 4.0,  "droite": 9.5},
    2: {"gauche": 3.5,  "droite": 10.0},
    3: {"gauche": 3.0,  "droite": 10.5},
}

# Vitesse axe Y
VY={
    1: {"gauche": 8.5,  "droite": 5.0},
    2: {"gauche": 9.0,  "droite": 4.5},
    3: {"gauche": 10.0, "droite": 3.5},
}
class ServoSubscriber(Node):
    def __init__(self):
        super().__init__('subscriber_servo')
        self.create_subscription(Vector3,'right_stick',self.listener_callback,10)
        self.dir_x="stop"
        self.last_dir_x="stop"
        self.start_time_x= None
        self.butee_x=False
        self.dir_y="stop"
        self.last_dir_y="stop"
        self.start_time_y=None
        self.butee_y=False
        self.vitesse=1
        self.create_timer(0.05, self.watchdog_timer) # 20 Hz
        self.dir_butee_x=None
        self.dir_butee_y=None

    def listener_callback(self, msg):

        if msg._x < 120:
            self.dir_x="droite"
        elif msg._x > 140:
            self.dir_x="gauche"
        else:
            self.dir_x="stop"
        if msg._y < 120:
            self.dir_y="gauche"
        elif msg._y > 140:
            self.dir_y="droite"
        else:
            self.dir_y="stop"
        self.vitesse = int(msg.z)
        
        if self.butee_x and self.dir_x==self.dir_butee_x:
        	self.dir_x="stop"
        if self.butee_y and self.dir_y==self.dir_butee_y:
        	self.dir_y="stop"

        if self.butee_x:
            if (
                self.dir_butee_x=="gauche" and self.dir_x=="droite"
                or self.dir_butee_x=="droite" and self.dir_x=="gauche"
            ):
                self.get_logger().info("[X] Déblocage butée (sens opposé)")
                self.butee_x=False
                self.dir_butee_x=None
                self.start_time_x=time.monotonic()        
        if self.butee_y:
            if (
                self.dir_butee_y=="gauche" and self.dir_y=="droite"
                or self.dir_butee_y=="droite" and self.dir_y=="gauche"
            ):
                self.get_logger().info("[Y] Déblocage butée (sens opposé)")
                self.butee_y=False
                self.dir_butee_y=None
                self.start_time_y=time.monotonic()

        if self.dir_x != self.last_dir_x and not self.butee_x:
            self.get_logger().info(f"[X] direction {self.last_dir_x} -> {self.dir_x}")
            self.start_time_x=time.monotonic() if self.dir_x != "stop" else None
            
        if self.dir_y != self.last_dir_y and not self.butee_y:
            self.get_logger().info(f"[Y] direction {self.last_dir_y} -> {self.dir_y}")
            self.start_time_y=time.monotonic() if self.dir_y != "stop" else None

        self.last_dir_x=self.dir_x
        self.last_dir_y=self.dir_y
        self.apply_pwm()
        self.get_logger().info(
            f"[CMD] x:{msg._x} y:{msg._y} vitesse:{self.vitesse}"
        )

    def watchdog_timer(self):
        now=time.monotonic()
        if self.start_time_x and not self.butee_x:
            elapsed=now-self.start_time_x
            if elapsed >= duree_max:
                self.butee_x=True
                self.dir_butee_x=self.dir_x
                pwm_x.ChangeDutyCycle(stop)
                self.get_logger().warn(f"[BUTEE]AXE X atteinte à {elapsed:.2f}s ({self.dir_x})")
        if self.start_time_y and not self.butee_y:
            elapsed=now-self.start_time_y
            if elapsed >= duree_max:
                self.butee_y=True
                self.dir_butee_y=self.dir_y
                pwm_y.ChangeDutyCycle(stop)
                self.get_logger().warn(f"[BUTEE] AXE Y atteinte à {elapsed:.2f}s ({self.dir_y})")

    def apply_pwm(self):

        if self.butee_x or self.dir_x=="stop":
            pwm_x.ChangeDutyCycle(stop)
        else:
            pwm_x.ChangeDutyCycle(VX[self.vitesse][self.dir_x])
        if self.butee_y or self.dir_y=="stop":
            pwm_y.ChangeDutyCycle(stop)
        else:
            pwm_y.ChangeDutyCycle(VY[self.vitesse][self.dir_y])

def main(args=None):
    rclpy.init(args=args)
    node=ServoSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    pwm_x.stop()
    pwm_y.stop()
    G.cleanup()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

