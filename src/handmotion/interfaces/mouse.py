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
        super().__init__(context)

        self.mouse: CursorAdapter = context.get("mouse_controller")
        
        if not self.mouse:
            raise ValueError(f"{self.name} requires 'mouse_controller' in context")
        
        self.pos_x, self.pos_y = 0.5, 0.5  # Start in the center of the screen
        self.click_threshold = CLICK_THRESHOLD  # Distance threshold for click detection

    def on_frame(self, payload: FramePayload) -> None:

        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        tracker: Landmark = self.hand.landmarks[TRACKER_LANDMARK]

        self.pos_x, self.pos_y = 1 - tracker.x, tracker.y
        self.mouse.move_norm(self.pos_x, self.pos_y)

        self.print_message(f"Cursor moved to: ({self.pos_x:.2f}, {self.pos_y:.2f})")

        # Example click detection (thumb tip to index tip distance)
        thumb_tip = self.hand.landmarks[THUMB_TIP]
        index_tip = self.hand.landmarks[INDEX_FINGER_TIP]

        thumb_index_dist = math.dist((thumb_tip.x, thumb_tip.y, thumb_tip.z),
                                     (index_tip.x, index_tip.y, index_tip.z))

        if thumb_index_dist < self.click_threshold:  # Arbitrary threshold for click detection
            self.mouse.click_once()
            self.print_message("Click detected")