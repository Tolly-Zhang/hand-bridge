from ..config.config import config

from .base import BaseInterface

from ..payload import FramePayload
from ..payload import Landmark

from ..adapters.cursor import CursorAdapter

import math

HAND_PREFERENCE = config.get("CursorDemo", "HAND_PREFERENCE")
CLICK_THRESHOLD = config.getfloat("CursorDemo", "CLICK_THRESHOLD")

WRIST = config.getint("LandmarkIndices", "WRIST")
THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")
MIDDLE_FINGER_TIP = config.getint("LandmarkIndices", "MIDDLE_FINGER_TIP")
RING_FINGER_TIP = config.getint("LandmarkIndices", "RING_FINGER_TIP")
PINKY_TIP = config.getint("LandmarkIndices", "PINKY_TIP")

class MouseInterface(BaseInterface):
    id = "cursor"
    name = "Cursor Demo"
    hand_preference = HAND_PREFERENCE  # Preferred hand for cursor control

    def __init__(self, context: dict) -> None:
        super().__init__(context)
        self.mouse = context.get("mouse_controller")
        if not self.mouse:
            raise ValueError("CursorDemo requires 'mouse_controller' in context")
        
        self.hand = None  # Currently tracked hand
        self.pos_x, self.pos_y = 0.5, 0.5  # Start in the center of the screen
        self.click_threshold = CLICK_THRESHOLD  # Distance threshold for click detection

    def enable(self) -> None:
        super().enable()
        # Additional setup if needed
        
    def disable(self) -> None:
        super().disable()
        # Additional teardown if needed

    def on_frame(self, payload: FramePayload) -> None:

        if not self.enabled:
            return

        if not payload.hands:
            print("No hands detected")
            return                                      # No hands detected
        
        for hand in payload.hands:
            if hand.handedness == self.hand_preference:
                self.hand = hand
                break
        if not self.hand:
            print(f"Error: No {self.hand_preference} hand detected")
            return
        self.pos_x = 1 - self.hand.landmarks[PINKY_TIP].x     # Pinky finger tip
        self.pos_y = self.hand.landmarks[PINKY_TIP].y     # Pinky finger tip
        self.mouse.move_norm(self.pos_x, self.pos_y)

        print(f"Cursor moved to: ({self.pos_x:.2f}, {self.pos_y:.2f})")

        # Example click detection (thumb tip to index tip distance)
        thumb_tip = self.hand.landmarks[THUMB_TIP]
        index_tip = self.hand.landmarks[INDEX_FINGER_TIP]

        thumb_index_dist = math.dist((thumb_tip.x, thumb_tip.y, thumb_tip.z),
                                     (index_tip.x, index_tip.y, index_tip.z))

        if thumb_index_dist < self.click_threshold:  # Arbitrary threshold for click detection
            self.mouse.click_once()
            print("Click detected")
