import pigpio
import time

# GPIO pin configuration
DIR_X = 20  # Direction pin for X axis
STEP_X = 21  # Step pin for X axis
DIR_Y = 19  # Direction pin for Y axis
STEP_Y = 26  # Step pin for Y axis

# Microstepping configuration (if using microstepping pins)
MS1 = 17  # Microstepping pin MS1
MS2 = 27  # Microstepping pin MS2
MS3 = 22  # Microstepping pin MS3

# Initialize pigpio
pi = pigpio.pi()

# Set GPIO mode
pi.set_mode(DIR_X, pigpio.OUTPUT)
pi.set_mode(STEP_X, pigpio.OUTPUT)
pi.set_mode(DIR_Y, pigpio.OUTPUT)
pi.set_mode(STEP_Y, pigpio.OUTPUT)
pi.set_mode(MS1, pigpio.OUTPUT)
pi.set_mode(MS2, pigpio.OUTPUT)
pi.set_mode(MS3, pigpio.OUTPUT)

# Set microstepping mode (example: 1/8 step)
pi.write(MS1, 1)
pi.write(MS2, 1)
pi.write(MS3, 0)

# Function to move stepper motor
def move_stepper(dir_pin, step_pin, steps, direction, delay=0.005, invert_direction=False):
    # Invert the direction if required
    if invert_direction:
        direction = not direction
    pi.write(dir_pin, direction)
    
    for _ in range(steps):
        pi.write(step_pin, 1)
        time.sleep(delay)
        pi.write(step_pin, 0)
        time.sleep(delay)

try:
    # Example: Move X axis motor 200 steps clockwise
    move_stepper(DIR_X, STEP_X, 200, 1, invert_direction=True)

    # Example: Move Y axis motor 200 steps counterclockwise
    move_stepper(DIR_Y, STEP_Y, 200, 0)

except KeyboardInterrupt:
    # Cleanup
    pi.stop()