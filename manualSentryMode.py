import cv2
import serial
import time
from pynput import keyboard
from threading import Thread

# Initialize serial communication with Arduino
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

# Load Haar Cascade for face detection
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Variables
manual_mode = False
keys_pressed = set()
frame = None
running = True


class CameraThread:
    """Threaded camera class for continuous frame capture."""
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.capture.set(cv2.CAP_PROP_FPS, 15)
        self.frame = None
        self.running = True
        self.thread = Thread(target=self.update, daemon=True)

    def start(self):
        """Start the thread."""
        self.thread.start()

    def update(self):
        """Continuously capture frames."""
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                self.frame = frame

    def read(self):
        """Get the latest frame."""
        return self.frame

    def stop(self):
        """Stop the thread."""
        self.running = False
        self.thread.join()
        self.capture.release()


def track_body(center_x, center_y, frame_width, frame_height):
    """Track the target and send commands to the Arduino."""
    tolerance = 20  # pixels
    x_error = center_x - (frame_width // 2)
    y_error = center_y - (frame_height // 2)

    x_error = x_error * 2.5 #stepper speed adsjusment
    y_error = y_error * 7.5 
    
    if abs(x_error) <= tolerance and abs(y_error) <= tolerance:
        ser.write(b"shoot\n")
    else:
        command = f"{y_error},{x_error}\n"
        ser.write(command.encode('utf-8'))


def manual_control():
    """Send manual control commands based on key presses."""
    if 'q' in keys_pressed:
        ser.write(b"0,-300\n")  # Move up
    if 'd' in keys_pressed:
        ser.write(b"0,300\n")  # Move down
    if 'z' in keys_pressed:
        ser.write(b"-100,0\n")  # Move left
    if 's' in keys_pressed:
        ser.write(b"100,0\n")  # Move right
    if 'space' in keys_pressed:
        ser.write(b"shoot\n")  # Shoot


def on_press(key):
    """Handle key press events."""
    global manual_mode
    try:
        if key.char in ['z', 'q', 's', 'd', ' ']:
            keys_pressed.add(key.char)
    except AttributeError:
        if key == keyboard.Key.enter:
            manual_mode = not manual_mode
            print(f"Manual mode {'activated' if manual_mode else 'deactivated'}")
        elif key == keyboard.Key.esc:
            global running
            running = False
            return False


def on_release(key):
    """Handle key release events."""
    try:
        if key.char in ['z', 'q', 's', 'd', ' ']:
            keys_pressed.discard(key.char)
    except AttributeError:
        pass


# Initialize threaded camera and keyboard listener
camera = CameraThread()
listener = keyboard.Listener(on_press=on_press, on_release=on_release)

try:
    camera.start()
    listener.start()

    while running:
        frame = camera.read()
        if frame is None:
            continue

        if manual_mode:
            manual_control()
        else:
            # Tracking mode
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = body_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                center_x = x + w // 2
                center_y = y + h // 2
                track_body(center_x, center_y, frame.shape[1], frame.shape[0])

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False

finally:
    camera.stop()
    listener.stop()
    cv2.destroyAllWindows()
