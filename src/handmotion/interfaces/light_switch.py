import math
from ..config.config import config

from .base import BaseInterface
from ..payload import FramePayload

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

        # Optional debug flag (add LEDInterface DEBUG = true in config if desired)
        # try:
        #     self.debug = config.getboolean("LEDInterface", "DEBUG")
        # except Exception:
        #     self.debug = False
        self.debug = False

    def enable(self) -> None:
        super().enable()
        # Additional setup if needed

    def disable(self) -> None:
        super().disable()
        # Additional teardown if needed

    def on_frame(self, payload: FramePayload) -> None:

        if not self.enabled:
            return

        print("[LightInterface] on_frame called")

        # Reset selected hand each frame to avoid using stale references
        self.hand = None

        if not payload.hands:
            if self.debug:
                print("[LEDInterface] No hands detected")
            return  # No hands detected

        for hand in payload.hands:
            if hand.handedness == HAND_PREFERENCE:
                self.hand = hand
                break

        if not self.hand:
            if self.debug:
                print(f"[LEDInterface] No {HAND_PREFERENCE} hand detected this frame")
            return

        # Convenience accessor
        wl = self.hand.world_landmarks
        thumb_tip = wl[THUMB_TIP]
        index_finger_tip = wl[INDEX_FINGER_TIP]

        # Compute distances (world coordinates are typically in meters)
        dist = math.dist((thumb_tip.x, thumb_tip.y, thumb_tip.z), (index_finger_tip.x, index_finger_tip.y, index_finger_tip.z))

        if self.debug:
            print("[LightInterface] Distances:", f"{dist:.4f}")

        is_pinch = dist < self.click_threshold

        if is_pinch and not self.pinch_active[0]:
            if self.debug:
                print("[LightInterface] Pinch detected - turning light ON")
            self.esp32_serial_adapter.write_line("LIGHT TOGGLE")

        # (Optional) could add a small hysteresis by using a release threshold > click_threshold