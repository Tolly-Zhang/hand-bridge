from ..config.config import config

from .base import BaseInterface

from ..payload import FramePayload
from ..payload import Landmark

from ..adapters.cursor import CursorAdapter

import math

HAND_PREFERENCE = config.get("CursorInterface", "HAND_PREFERENCE")
CLICK_THRESHOLD = config.getfloat("MediaPipe", "CLICK_THRESHOLD")

THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
TRACKER_LANDMARK = config.getint("CursorInterface", "TRACKER_LANDMARK")

class MouseInterface(BaseInterface):
    id = "mouse"
    name = "Mouse Interface"
    hand_preference = HAND_PREFERENCE  # Preferred hand for cursor control

    def __init__(self, context: dict) -> None:
        super().__init__(context, "mouse_controller")
        
        self.pos_x, self.pos_y = 0.5, 0.5  # Start in the center of the screen

    def on_frame(self, payload: FramePayload) -> None:

        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        tracker: Landmark = self.hand_1.landmarks[TRACKER_LANDMARK]

        self.pos_x, self.pos_y = 1 - tracker.x, tracker.y
        self.adapter.move_norm(self.pos_x, self.pos_y)

        self.print_message(f"Cursor moved to: ({self.pos_x:.2f}, {self.pos_y:.2f})")

        # Click Detection
        if self.hand_1.is_touching(THUMB_TIP, INDEX_FINGER_TIP):
            self.adapter.click_once()
            self.print_message("Click detected")