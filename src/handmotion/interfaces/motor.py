from ..config.config import config

from .base import BaseInterface
from typing import Any  # Add this if you want to use Any as a placeholder

from ..payload import FramePayload

HAND_PREFERENCE = config.get("MotorInterface", "HAND_PREFERENCE")
CLICK_THRESHOLD = config.getfloat("MediaPipe", "CLICK_THRESHOLD")

THUMB_TIP = config.getint("LandmarkIndices", "THUMB_TIP")
INDEX_FINGER_TIP = config.getint("LandmarkIndices", "INDEX_FINGER_TIP")

class MotorInterface(BaseInterface):
    id = "motor"
    name = "Motor Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context)

        self.esp32_serial_adapter = context.get("esp32_serial_adapter")
        
        if not self.esp32_serial_adapter:
            raise ValueError(f"{self.name} requires 'esp32_serial_adapter' in context")

    def on_frame(self, payload: FramePayload) -> None:
        
        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        distance = self.hand.calculate_xyz_distance(THUMB_TIP, INDEX_FINGER_TIP)

        speed = (distance - CLICK_THRESHOLD) / (0.15 - CLICK_THRESHOLD) * 10
        speed = min(max(speed, 0), 10)
        
        command = f"THROTTLE {int(speed)}"
        self.esp32_serial_adapter.write_line(command)
        self.print_message(f"Sent command: {command}")