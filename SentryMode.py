import cv2
import serial
import time

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

# Variables for tracking
last_x_error, last_y_error = None, None

def track_body(center_x, center_y, frame_width, frame_height):
    """
    Tracks the target and sends position errors or a 'shoot' command to the Arduino.
    """
    global last_x_error, last_y_error

    # Define tolerance zone for centering
    tolerance = 20  # pixels
    x_error = center_x - (frame_width // 2)
    y_error = center_y - (frame_height // 2)

    if abs(x_error) <= tolerance and abs(y_error) <= tolerance:
        # If the target is centered, send 'shoot' command
        if last_x_error != "shoot":  # Avoid sending repeated 'shoot' commands
            print("Centered! Sending shoot command...")
            ser.write(b"shoot\n")
            last_x_error, last_y_error = "shoot", "shoot"
    else:
        # Send position error values if they have changed
        if (x_error != last_x_error) or (y_error != last_y_error):
            command = f"{x_error},{y_error}\n"
            ser.write(command.encode('utf-8'))
            last_x_error, last_y_error = x_error, y_error

try:
    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = body_cascade.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

        # Process detected faces
        for (x, y, w, h) in faces:
            # Draw a rectangle around the detected face (optional)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Calculate center of the detected face
            center_x = x + w // 2
            center_y = y + h // 2

            # Track the target
            track_body(center_x, center_y, frame.shape[1], frame.shape[0])

        # Resize the frame for display
        resized_frame = cv2.resize(frame, (320, 240))
        cv2.imshow('Frame', resized_frame)

        # Quit the program if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources on exit
    cap.release()
    cv2.destroyAllWindows()
