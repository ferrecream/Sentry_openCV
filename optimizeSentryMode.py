import cv2
import RPi.GPIO as GPIO
import time
import serial

# Setup serial communication
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

# GPIO pin setup
DIR_X = 20  # Direction pin for X axis
STEP_X = 21  # Step pin for X axis
DIR_Y = 19  # Direction pin for Y axis
STEP_Y = 26  # Step pin for Y axis

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

# Serial initialization
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

# Initialize the Pi Camera
cap = cv2.VideoCapture(0)

# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def track_face(center_x, center_y, frame_width, frame_height):
    x_threshold = frame_width // 3
    y_threshold = frame_height // 3
    
    if center_x < x_threshold:
        ser.write(b'0')  # Move left
    elif center_x > (frame_width - x_threshold):
        ser.write(b'1')  # Move right
    
    if center_y < y_threshold:
        ser.write(b'2')  # Move up
    elif center_y > (frame_height - y_threshold):
        ser.write(b'3')  # Move down

try:
    skip_frames = 2  # Process every 2nd frame
    frame_count = 0
    previous_roi = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % skip_frames != 0:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if previous_roi is not None:
            # Use a small ROI around the last detected position
            x, y, w, h = previous_roi
            roi_gray = gray[y:y+h, x:x+w]
            faces = face_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
            if len(faces) > 0:
                fx, fy, fw, fh = faces[0]
                fx += x
                fy += y
                previous_roi = (fx, fy, fw, fh)
        else:
            # Full frame detection
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
            if len(faces) > 0:
                previous_roi = faces[0]

        if previous_roi is not None:
            x, y, w, h = previous_roi
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            center_x = x + w // 2
            center_y = y + h // 2
            track_face(center_x, center_y, frame.shape[1], frame.shape[0])
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()