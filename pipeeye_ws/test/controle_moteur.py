import RPi.GPIO as G
import time

servo_pin=17
G.setmode(G.BCM)
G.setup(servo_pin, G.OUT)
pwm=G.PWM(servo_pin, 50)
pwm.start(7.5)

try:
	while True:
		pwm.ChangeDutyCycle(5.5)
		time.sleep(1)
		pwm.ChangeDutyCycle(8.0)
		time.sleep(1)
except KeyboardInterrupt:
	pwm.stop()
	G.cleanup()
