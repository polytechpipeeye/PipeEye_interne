import board
import neopixel
import time

# Test direct sur GPIO 12 (Pin 32)
pixels = neopixel.NeoPixel(board.D18, 18)

while True:
    print("Test Allumage Rouge...")
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(1)
    print("Test Extinction...")
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(1)
