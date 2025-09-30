import cv2

DEFAULT_CAMERA_INDEX = 701

DEFAULT_CAMERA_RESOLUTION = (1920, 1080)  # Default resolution

CONVERT_BGR_TO_RGB = True  # Whether to convert BGR to RGB for processing

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

        print(f"Camera initialized with index {camera_index} at resolution {width}x{height}.")
    
    def read(self, convert_to_rgb=CONVERT_BGR_TO_RGB):
        ret, self.frame_bgr = self.cap.read()

        if not ret:
            raise RuntimeError("Failed to read frame from camera.")

        self.frame_rgb = cv2.cvtColor(self.frame_bgr, cv2.COLOR_BGR2RGB)

        return self.frame_rgb if convert_to_rgb else self.frame_bgr

    def show_feed(self, window_name="Camera Feed", wait_key=1):
        cv2.imshow(window_name, self.frame_bgr)
        cv2.waitKey(wait_key)

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

    def close_all(self):
        cv2.destroyAllWindows()

    def __del__(self):
        self.release()
        self.close_all()
        print("Camera resources released and windows closed.")