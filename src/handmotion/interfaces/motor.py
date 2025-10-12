from .interface_common import (
    # config,
    BaseInterface,
    FramePayload,
    get_hand_preference,
    get_click_threshold,
    get_thumb_tip_index,
    get_index_finger_tip_index,
)

from ..adapters.esp32_serial import ESP32SerialAdapter

HAND_PREFERENCE = get_hand_preference("MotorInterface")
CLICK_THRESHOLD = get_click_threshold()

THUMB_TIP = get_thumb_tip_index()
INDEX_FINGER_TIP = get_index_finger_tip_index()

class MotorInterface(BaseInterface):
    id = "motor"
    name = "Motor Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context, "esp32_serial_adapter", ESP32SerialAdapter)

    def on_frame(self, payload: FramePayload) -> None:
        
        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        distance = self.hand_1.calculate_xyz_distance(THUMB_TIP, INDEX_FINGER_TIP)

        speed = (distance - CLICK_THRESHOLD) / (0.15 - CLICK_THRESHOLD) * 10
        speed = min(max(speed, 0), 10)
        
        command = f"THROTTLE {int(speed)}"
        self.adapter.write_line(command)
        self.print_message(f"Sent command: {command}")