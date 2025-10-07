# Core loop: capture, mediapipe, payload, hotkeys

from .manager import InterfaceManager
from .payload import FramePayload
from .camera import Camera
from .mediapipe import MediaPipeHands
from .time_controller import TimeController
from .payload_builder import PayloadBuilder
from .calibration.calibration import Calibration

from .adapters.cursor import CursorAdapter
from .interfaces.mouse import MouseInterface

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

    camera_index = int(input("Enter camera index: "))

    # Initialize Camera, MediaPipeHands, TimeController, DemoManager instance
    camera = Camera(camera_index=camera_index)
    hands = MediaPipeHands()
    time_controller = TimeController()

    mouse_controller = CursorAdapter()

    mouse_controller.printRange()

    cursor_demo = MouseInterface(context={"mouse_controller": mouse_controller})
    cursor_demo.enable()

    demo_manager = InterfaceManager(demos={"cursor": cursor_demo})

    time_controller.start()

    while True:
        
        time_controller.update()

        camera.read()


        results = hands.process_sync(camera.get_frame_rgb())
        hands.annotate_image(camera.get_frame_bgr())

        payload = PayloadBuilder.build(frame_dimensions=camera.get_frame_dimensions(), 
                                       time_ns=time_controller.get_elapsed_time_ns(), 
                                       time_delta_ns=time_controller.get_delta_ns(),
                                       hands=results)
        # payload.print_summary()

        # camera.show_feed()

        demo_manager.on_frame(payload)

        # Exit on 'q' key press
        if keyboard.is_pressed('q'):
            print("Exiting...")
            break

        # time.sleep(1)  # Delay for testing purposes

    camera.shutdown()  # Ensure camera is shutdown properly

if __name__ == "__main__":
    main()