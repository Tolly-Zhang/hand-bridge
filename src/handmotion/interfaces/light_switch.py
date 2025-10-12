from ..config.config import config

from .base import BaseInterface
from ..payload import FramePayload

HAND_PREFERENCE = config.get("LEDInterface", "HAND_PREFERENCE")

THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
PINKY_TIP = config.getint("LandmarkIndices", "PINKY_TIP")

class LightInterface(BaseInterface):
    id = "light"
    name = "Light Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context, "esp32_serial_adapter")

        self.pinch_state = False  # Track whether a pinch is currently active

    def on_frame(self, payload: FramePayload) -> None:

        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        # Compute distances
        is_pinch = self.hand.is_touching(THUMB_TIP, INDEX_FINGER_TIP)

        if is_pinch != self.pinch_state:
            self.pinch_state = is_pinch
            self.adapter.write_line("LIGHT TOGGLE")
            self.print_message("Pinch detected - Toggled Light")