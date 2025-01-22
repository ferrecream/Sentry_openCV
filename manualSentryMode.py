import cv2
import serial
import time
from pynput import keyboard

# Initialize serial communication with Arduino
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Set resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 15)          # Set frame rate

# Load Haar Cascade for face detection
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Variables
manual_mode = False  # Tracks whether manual mode is active
keys_pressed = set()  # Tracks keys currently being pressed
last_x_error, last_y_error = None, None


def track_body(center_x, center_y, frame_width, frame_height):
    """
    Tracks the target and sends position errors or a 'shoot' command to the Arduino.
    """
    global last_x_error, last_y_error

    tolerance = 20  # pixels
    x_error = center_x - (frame_width // 2)
    y_error = center_y - (frame_height // 2)

    if abs(x_error) <= tolerance and abs(y_error) <= tolerance:
        if last_x_error != "shoot":
            print("Centered! Sending shoot command...")
            ser.write(b"shoot\n")
            last_x_error, last_y_error = "shoot", "shoot"
    else:
        if (x_error != last_x_error) or (y_error != last_y_error):
            command = f"{x_error},{y_error}\n"
            ser.write(command.encode('utf-8'))
            last_x_error, last_y_error = x_error, y_error


def manual_control():
    """
    Sends manual control commands to the Arduino based on key presses.
    """
    if 'z' in keys_pressed:  # Move up
        ser.write(b"0,-10\n")
    if 's' in keys_pressed:  # Move down
        ser.write(b"0,10\n")
    if 'q' in keys_pressed:  # Move left
        ser.write(b"-10,0\n")
    if 'd' in keys_pressed:  # Move right
        ser.write(b"10,0\n")
    if 'space' in keys_pressed:  # Shoot
        ser.write(b"shoot\n")


def on_press(key):
    """
    Detects when a key is pressed.
    """
    global manual_mode
    try:
        if key.char in ['z', 'q', 's', 'd', ' ']:
            keys_pressed.add(key.char)
    except AttributeError:
        if key == keyboard.Key.enter:
            manual_mode = not manual_mode
            print(f"Manual mode {'activated' if manual_mode else 'deactivated'}")
        elif key == keyboard.Key.esc:  # Exit the program with Esc
            return False


def on_release(key):
    """
    Detects when a key is released.
    """
    try:
        if key.char in ['z', 'q', 's', 'd', ' ']:
            keys_pressed.discard(key.char)
    except AttributeError:
        pass


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    while True:
        if manual_mode:
            manual_control()
        else:
            # Tracking mode
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = body_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                center_x = x + w // 2
                center_y = y + h // 2
                track_body(center_x, center_y, frame.shape[1], frame.shape[0])

            resized_frame = cv2.resize(frame, (320, 240))
            cv2.imshow('Frame', resized_frame)

        # Exit program by pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    listener.stop()
