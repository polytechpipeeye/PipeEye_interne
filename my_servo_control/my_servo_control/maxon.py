import rclpy
from rclpy.node import Node
import time
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
        self.A=304.8
        self.R=218.9/2
        self.v21= self.A/(self.A+self.R)
        self.v31= (self.A-self.R)/(self.R+self.A)
        #GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        # Set up GPIO pins for PWM output
        self.PWM_pins = [11, 12, 22, 24, 26]  # Change pin numbers as needed
        for pin in self.PWM_pins:
            GPIO.setup(pin, GPIO.OUT)
        self.forward = False 
        self.enable = False 
        self.motor_pwm1 = GPIO.PWM(self.PWM_pins[2],50)
        self.motor_pwm2 = GPIO.PWM(self.PWM_pins[3],50)
        self.motor_pwm3 = GPIO.PWM(self.PWM_pins[4],50)
        self.motor_pwm1.start(10)
        self.motor_pwm2.start(10)
        self.motor_pwm3.start(10)
        GPIO.output(self.PWM_pins[0],self.forward)
        GPIO.output(self.PWM_pins[1],self.enable)
        time.sleep(1)
        GPIO.output(self.PWM_pins[1],True) #led of driver will be green

    def listener_callback(self, msg):
        #self.get_logger().info('I heard: "%s"' % msg)
        vx = msg.linear.x*200
        angular = msg.angular.z*200
        self.get_logger().info('I heard: "%s"' % msg)
        #print(vx, angular)
        #print(' vx sent to ', self.PWM_pins[4])
        # PWM values for motors 1, 3, 5 (pins 18, 24, 16)
        if vx >= 0.0 and angular==0:
            if vx>=90.0:
                vx=90
            elif vx<=10.0:
                vx=10
            GPIO.output(self.PWM_pins[0],False)
            self.motor_pwm1.ChangeDutyCycle(vx)
            self.motor_pwm2.ChangeDutyCycle(vx)
            self.motor_pwm3.ChangeDutyCycle(vx)
            
            #GPIO.output(self.PWM_pins[1],self.enable)
            #print(' vx sent to ', self.PWM_pins[4])
        elif vx < 0.0 and angular==0:
            if vx<=-90:
                vx=-90
            elif vx>=-10:
                vx=-10
            GPIO.output(self.PWM_pins[0],True)
            self.motor_pwm1.ChangeDutyCycle(-vx)
            self.motor_pwm2.ChangeDutyCycle(-vx)
            self.motor_pwm3.ChangeDutyCycle(-vx)
            
        elif angular>=0.0 and vx ==0:
            if angular>=90:
                angular=90
            elif angular<=10:
                angular=10
            GPIO.output(self.PWM_pins[0],False)
            self.motor_pwm1.ChangeDutyCycle(angular*self.v21)  #middle
            self.motor_pwm2.ChangeDutyCycle(angular)
            self.motor_pwm3.ChangeDutyCycle(angular*self.v31) # d3if
            
        elif angular<0.0 and vx==0:
            if angular<=-90:
                angular=-90
            elif angular>=-10:
                angular=-10 
            self.forward = False 
            self.enable = True 
            GPIO.output(self.PWM_pins[0],False)
            self.motor_pwm1.ChangeDutyCycle(-angular*self.v21) #middle
            self.motor_pwm2.ChangeDutyCycle(-angular*self.v31) #d3if
            self.motor_pwm3.ChangeDutyCycle(-angular)
            
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

