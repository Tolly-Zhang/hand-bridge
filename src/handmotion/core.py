# Core loop: capture, mediapipe, payload, hotkeys

from .manager import DemoManager
from .payload import FramePayload
from .camera import Camera
from .mediapipe import MediaPipeHands
from .payload_builder import PayloadBuilder

from cv2_enumerate_cameras import enumerate_cameras
import keyboard
import time

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

    # Initialize MediaPipeHands
    hands = MediaPipeHands()

    while True:
        time.sleep(1)  # Delay for testing purposes
        camera.read()
        results = hands.process_sync(camera.get_frame_rgb())
        hands.annotate_image(camera.get_frame_bgr())

        payload = PayloadBuilder.build(meta=None, hands=results)
        payload.print_summary()

        camera.show_feed()

        # Exit on 'q' key press
        if keyboard.is_pressed('q'):
            print("Exiting...")
            break

    del camera  # Ensure camera resources are released

if __name__ == "__main__":
    main()