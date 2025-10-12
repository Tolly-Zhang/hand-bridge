from ..config.config import config

from .base import BaseInterface
from ..payload import FramePayload

DEBUG = config.getboolean("DEFAULT", "DEBUG")

HAND_PREFERENCE = config.get("LEDInterface", "HAND_PREFERENCE")
CLICK_THRESHOLD = config.getfloat("MediaPipe", "CLICK_THRESHOLD")

THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
MIDDLE_FINGER_TIP = config.getint("LandmarkIndices", "MIDDLE_FINGER_TIP")
RING_FINGER_TIP = config.getint("LandmarkIndices", "RING_FINGER_TIP")
PINKY_TIP = config.getint("LandmarkIndices", "PINKY_TIP")

class LightInterface(BaseInterface):
    id = "light"
    name = "Light Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context)
        self.esp32_serial_adapter = context.get("esp32_serial_adapter")
        if not self.esp32_serial_adapter:
            raise ValueError("LEDInterface requires 'esp32_serial_adapter' in context")

        self.hand = None  # Currently tracked hand
        self.click_threshold = CLICK_THRESHOLD  # Distance threshold for click detection

        self.pinch_state = False  # Track whether a pinch is currently active

    def on_frame(self, payload: FramePayload) -> None:

        if not self.enabled:
            return

        if DEBUG:
            print("[LightInterface] on_frame called")

        # Reset selected hand each frame to avoid using stale references
        self.hand = None

        if not payload.hands:
            if DEBUG:
                print("[LEDInterface] No hands detected")
            return  # No hands detected

        for hand in payload.hands:
            if hand.handedness == HAND_PREFERENCE:
                self.hand = hand
                break

        if not self.hand:
            if DEBUG:
                print(f"[LEDInterface] No {HAND_PREFERENCE} hand detected this frame")
            return

        # Compute distances
        dist = self.hand.calculate_xyz_distance(THUMB_TIP, INDEX_FINGER_TIP)

        if DEBUG:
            print("[LightInterface] Distances:", f"{dist:.4f}")

        is_pinch = dist < self.click_threshold

        if is_pinch != self.pinch_state:
            self.pinch_state = is_pinch
            if DEBUG:
                print("[LightInterface] Pinch detected - toggling light")
            self.esp32_serial_adapter.write_line("LIGHT TOGGLE")