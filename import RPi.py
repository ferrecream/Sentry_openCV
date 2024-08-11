import RPi.GPIO as GPIO
import time

# GPIO setup
DIR = 20  # Direction pin
STEP = 21  # Step pin
CW = 1  # Clockwise rotation
CCW = 0  # Counterclockwise rotation
SPR = 200  # Steps per revolution (1.8 degree step angle)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

# Set motor direction to clockwise
GPIO.output(DIR, CW)

try:
    while True:
        # Pulse the step pin
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(0.005)  # Adjust the delay to control speed
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(0.005)

except KeyboardInterrupt:
    # Cleanup GPIO settings
    GPIO.cleanup()