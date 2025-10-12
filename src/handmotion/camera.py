from .config.config import config

import cv2
from cv2_enumerate_cameras import enumerate_cameras
import numpy as np

DEFAULT_CAMERA_INDEX = config.getint("Camera", "INDEX")
DEFAULT_CAMERA_RESOLUTION = (config.getint("Camera", "RESOLUTION_X"), config.getint("Camera", "RESOLUTION_Y"))
DEFAULT_CAMERA_FPS = config.getint("Camera", "FPS")
DEFAULT_WINDOW_NAME = config.get("Camera", "WINDOW_NAME")

class Camera:
    """Singleton class to manage camera access."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Camera, cls).__new__(cls)
        else:
            print("Warning: Camera instance already exists. Returning the existing instance.")
        return cls._instance

    def __init__(self, camera_index=DEFAULT_CAMERA_INDEX, width=DEFAULT_CAMERA_RESOLUTION[0], height=DEFAULT_CAMERA_RESOLUTION[1]):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera with index {camera_index}.")

        print(f"Camera initialized with index {camera_index} at resolution {width}x{height}")

    def print_cameras(self) -> None:
        cameras = list(enumerate_cameras())

        if not cameras:
            print("No cameras found.")
            return
        
        print("Available cameras:")
        for camera_info in cameras:
            print(f"  Index: {camera_info.index}, Name: {camera_info.name}")

    def read(self) -> None:
        ret, self.frame_bgr = self.cap.read()

        if not ret:
            raise RuntimeError("Failed to read frame from camera.")

        self.frame_rgb = cv2.cvtColor(self.frame_bgr, cv2.COLOR_BGR2RGB)

    def get_frame_rgb(self) -> np.ndarray:
        return self.frame_rgb

    def get_frame_bgr(self) -> np.ndarray:
        return self.frame_bgr

    def get_frame_dimensions(self) -> tuple:
        return (self.frame_rgb.shape[1], self.frame_rgb.shape[0])

    def show_feed(self, window_name=DEFAULT_WINDOW_NAME, wait_key=1):
        cv2.imshow(window_name, self.frame_bgr)
        cv2.waitKey(wait_key)

    def release(self) -> None:
        if self.cap.isOpened():
            self.cap.release()

    def close_all(self) -> None:
        cv2.destroyAllWindows()

    def shutdown(self) -> None:
        print("Shutting down camera...")
        self.release()
        self.close_all()
    
    def __del__(self):
        self.shutdown()