# Core loop: capture, mediapipe, payload, hotkeys

from .manager import DemoManager
from .payload import FramePayload
from .camera import Camera

import mediapipe as mp
import cv2
from cv2_enumerate_cameras import enumerate_cameras

def main():
    # List available cameras
    cameras = list(enumerate_cameras())
    if not cameras:
        print("No cameras found.")
        return
    for camera_info in cameras:
        print(f"{camera_info.index}: {camera_info.name}")

    # camera_index = int(input("Enter camera index: "))

    # Initialize Camera instance
    camera = Camera()

    # Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    while True:
        frame = camera.read()
        # Optionally, process with MediaPipe here
        # results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Show the frame
        camera.show_feed()

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    del camera  # Ensure camera resources are released

if __name__ == "__main__":
    main()