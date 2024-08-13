import cv2
import RPi.GPIO as GPIO
import time
import serial


ser = serial.Serial("/dev/ttyUSB0", 115200, timeout= 1)

# GPIO pin setup
DIR_X = 20  # Direction pin for X axis
STEP_X = 21  # Step pin for X axis
DIR_Y = 19  # Direction pin for Y axis
STEP_Y = 26  # Step pin for Y axis

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)


# Initialize the Pi Camera
cap = cv2.VideoCapture(0)

# Load pre-trained body detector
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

def track_body(center_x, center_y, frame_width, frame_height):
    # Define thresholds and steps based on your setup
    x_threshold = frame_width // 3
    y_threshold = frame_height // 3

    
    if center_x < x_threshold:
        ser.write(b'0')  # Move left
        print("send data to arduino")
    elif center_x > (frame_width - x_threshold):
        ser.write(b'1')  # Move right
        print("send data to arduino")
    if center_y < y_threshold:
        ser.write(b'2')  # Move up
        print("send data to arduino")
    elif center_y > (frame_height - y_threshold):
        ser.write(b'3')  # Move down
        print("send data to arduino")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bodies = body_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in bodies:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            center_x = x + w // 2
            center_y = y + h // 2
            track_body(center_x, center_y, frame.shape[1], frame.shape[0])
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()