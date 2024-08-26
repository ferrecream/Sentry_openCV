import cv2
import serial
import time

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
ser.setDTR(False)
time.sleep(1)
ser.flushInput()
ser.setDTR(True)
time.sleep(2)

cap = cv2.VideoCapture(0)
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def track_body(center_x, center_y, frame_width, frame_height):
    # Calculate the offsets (errors) from the center of the frame
    x_error = center_x - (frame_width // 2)
    y_error = center_y - (frame_height // 2)
    
    # Send the error values to the Arduino
    command = f"{x_error},{y_error}\n"
    ser.write(command.encode('utf-8'))

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = body_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
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