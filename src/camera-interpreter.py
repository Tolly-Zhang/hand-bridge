import cv2
from cv2_enumerate_cameras import enumerate_cameras

# List all available cameras
cameras = enumerate_cameras()

# Enumerate cameras using the default API preference
for camera_info in enumerate_cameras():
    print(f'{camera_info.index}: {camera_info.name}')

# cameraIndex = int(input("Enter camera index: "))
cameraIndex = 701

# Initialize webcam
cap = cv2.VideoCapture(cameraIndex)

if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

cv2.namedWindow('Webcam Feed')  # Create the window once

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Display the current frame
    cv2.imshow('Webcam Feed', frame)

    # Exit the loop when 'q' and 'c' are both pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        if cv2.waitKey(1) & 0xFF == ord('c'):
            print("'q' and 'c' pressed. Exiting.")
            break

cap.release()
cv2.destroyAllWindows()
