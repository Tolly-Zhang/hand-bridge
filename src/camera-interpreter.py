import cv2
import mediapipe as mp
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

# Resize window
cv2.resizeWindow('Webcam Feed', windowResolution[0], windowResolution[1])

# Prevent manual resizing 
# cv2.setWindowProperty('Webcam Feed', cv2.WND_PROP_FULLSCREEN, 0)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Convert the BGR frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and get hand landmarks
    results = hands.process(frame_rgb)

    # Draw hand landmarks on the frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the frame with hand landmarks
    cv2.imshow('Webcam Feed', frame)

    # Exit the loop when 'q' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("'q' pressed. Exiting.")
        break

cap.release()
cv2.destroyAllWindows()
