import rclpy
from rclpy.node import Node
import board
import neopixel
import time

# Message imports
from my_robot_interface.msg import LedControl 
from std_msgs.msg import ColorRGBA

class NeoPixelPWMController(Node):
    def __init__(self):
        super().__init__('neopixel_test')
        
        # --- PWM CONFIGURATION (GPIO 12) ---
        self.num_pixels = 12
        try:
            # GPIO 12 is board.D12
            self.pixels = neopixel.NeoPixel(
                board.D12, 
                self.num_pixels, 
                brightness=0.2, 
                auto_write=False,
                pixel_order=neopixel.GRB # Use RGB if colors are swapped
            )
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            self.get_logger().info("PWM Controller initialized on GPIO 12.")
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            self.get_logger().error(f"Failed to start PWM. Did you use sudo? Error: {e}")

        # --- STATE ---
        self.current_mask = 0
        self.r, self.g, self.b = 255, 255, 255

        # --- SUBSCRIPTIONS ---
        # Note: Ensure these topic names match your publisher exactly
        self.create_subscription(LedControl, 'LEDinput', self.led_callback, 10)
        self.create_subscription(ColorRGBA, 'led_color', self.color_callback, 10)

    def led_callback(self, msg):
        # VISUAL CHECK: Print this so you know the message actually arrived
        print(f"RECEIVED: Q1={msg.q1} Q2={msg.q2} Q3={msg.q3} Q4={msg.q4} | Int={msg.intensity}")
        
        new_mask = 0
        if msg.q1: new_mask |= (1 << 0)
        if msg.q2: new_mask |= (1 << 1)
        if msg.q3: new_mask |= (1 << 2)
        if msg.q4: new_mask |= (1 << 3)

        self.pixels.brightness = float(msg.intensity) / 4.0
        self.current_mask = new_mask
        if msg.is_red:
            self.r, self.g, self.b=255, 0, 0
        else:
        	self.r, self.g, self.b=0, 0, 0
        self.update_hardware()

    def color_callback(self, msg):
        self.r, self.g, self.b = int(msg.r), int(msg.g), int(msg.b)
        self.update_hardware()

    def update_hardware(self):
        # Clear buffer
        self.pixels.fill((0, 0, 0))
        
        # Fill quadrants (3 LEDs each)
        for q in range(4):
            if (self.current_mask >> q) & 1:
                start = q * 3
                for i in range(start, start + 3):
                    if i < self.num_pixels:
                        self.pixels[i] = (self.r, self.g, self.b)
        
        # Write to hardware
        self.pixels.show()

def main(args=None):
    rclpy.init(args=args)
    node = NeoPixelPWMController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Turn off LEDs on exit
        node.pixels.fill((0, 0, 0))
        node.pixels.show()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
