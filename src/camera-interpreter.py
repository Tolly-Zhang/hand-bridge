import cv2
from cv2_enumerate_cameras import enumerate_cameras

cameraIndex = 701
cameraResolution = (1920, 1080)  # 4K resolution
windowResolution = (1920, 1080)  # Window size
fps = 30

# List all available cameras
cameras = enumerate_cameras()

# Enumerate cameras using the default API preference
for camera_info in enumerate_cameras():
    print(f'{camera_info.index}: {camera_info.name}')

# cameraIndex = int(input("Enter camera index: "))

# Initialize webcam
cap = cv2.VideoCapture(cameraIndex)

# Set the codec to MJPEG
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# Set the resolution to 3840x2160 (4K)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cameraResolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraResolution[1])

# Optionally, set the FPS (frames per second)
cap.set(cv2.CAP_PROP_FPS, fps)

if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Retrieve camera properties
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

# Display camera information
print(f"Camera Index: {cameraIndex}")
print(f"Resolution: {frame_width}x{frame_height}")
print(f"FPS: {fps if fps > 0 else 'Not available'}")


cv2.namedWindow('Webcam Feed', cv2.WINDOW_NORMAL)  # Create the window once

#Resize window
cv2.resizeWindow('Webcam Feed', windowResolution[0], windowResolution[1])

# # Prevent manual resizing
# cv2.setWindowProperty('Webcam Feed', cv2.WND_PROP_FULLSCREEN, 0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Display the current frame
    cv2.imshow('Webcam Feed', frame)

    # Exit the loop when 'q' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("'q' pressed. Exiting.")
        break

cap.release()
cv2.destroyAllWindows()
