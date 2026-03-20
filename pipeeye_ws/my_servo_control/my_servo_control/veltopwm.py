import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
import RPi.GPIO as GPIO


class PWMController(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        
        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        # Set up GPIO pins for PWM output
        self.PWM_pins = [18, 23, 32, 12, 37, 16]  # Change pin numbers as needed
        for pin in self.PWM_pins:
            GPIO.setup(pin, GPIO.OUT)
        self.forwarda = GPIO.PWM(self.PWM_pins[0],50)
        self.backwarda = GPIO.PWM(self.PWM_pins[1],50)
        self.forwardb = GPIO.PWM(self.PWM_pins[2],50)
        self.backwardb = GPIO.PWM(self.PWM_pins[3],50)
        self.forwardc = GPIO.PWM(self.PWM_pins[4],50)
        self.backwardc = GPIO.PWM(self.PWM_pins[5],50)
        self.forwarda.start(0)
        self.backwarda.start(0)
        self.forwardb.start(0)
        self.backwardb.start(0)
        self.forwardc.start(0)
        self.backwardc.start(0)
        

    def listener_callback(self, msg):
        #self.get_logger().info('I heard: "%s"' % msg)
        vx = msg.linear.x*200
        angular = msg.angular.z*200
        self.get_logger().info('I heard: "%s"' % msg)
        #print(vx, angular)
        #print(' vx sent to ', self.PWM_pins[4])
        # PWM values for motors 1, 3, 5 (pins 18, 24, 16)
        if vx >= 0.0 and angular==0:
            self.forwarda.ChangeDutyCycle(vx)
            self.backwarda.ChangeDutyCycle(0)
            self.forwardb.ChangeDutyCycle(vx)
            self.backwardb.ChangeDutyCycle(0)
            self.forwardc.ChangeDutyCycle(vx)
            self.backwardc.ChangeDutyCycle(0)
            #print(' vx sent to ', self.PWM_pins[4])
        elif vx < 0.0 and angular==0:
            self.forwarda.ChangeDutyCycle(0)
            self.backwarda.ChangeDutyCycle(-vx)
            self.forwardb.ChangeDutyCycle(0)
            self.backwardb.ChangeDutyCycle(-vx)
            self.forwardc.ChangeDutyCycle(0)
            self.backwardc.ChangeDutyCycle(-vx)
        elif angular>=0.0 and vx ==0:
            self.forwarda.ChangeDutyCycle(angular)
            self.backwarda.ChangeDutyCycle(0)
            self.forwardb.ChangeDutyCycle(0)
            self.backwardb.ChangeDutyCycle(0)
            self.forwardc.ChangeDutyCycle(angular)
            self.backwardc.ChangeDutyCycle(0)
        elif angular<0.0 and vx==0:
            self.forwarda.ChangeDutyCycle(0)
            self.backwarda.ChangeDutyCycle(0)
            self.forwardb.ChangeDutyCycle(-angular)
            self.backwardb.ChangeDutyCycle(0)
            self.forwardc.ChangeDutyCycle(-angular)
            self.backwardc.ChangeDutyCycle(0)
        #self.get_logger().info('Publishing Twist command: Linear=%.2f, Angular=%.2f' %
        #                       (vx, angular))







    def set_pwm(self, pin, value):
        pwm = GPIO.PWM(pin, 100)  # Frequency: 100 Hz (adjust as needed)
        pwm.start(value * 100)  # Start PWM with the given duty cycle
        pwm.ChangeDutyCycle(value * 100)  # Change duty cycle
        if value == 0:
            pwm.stop()  # Stop PWM if the value is 0

def main(args=None):
    print('bihroijazoeir pozejfri azrt ')
    rclpy.init(args=args)
    pwm_controller = PWMController()
    rclpy.spin(pwm_controller)
    pwm_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

