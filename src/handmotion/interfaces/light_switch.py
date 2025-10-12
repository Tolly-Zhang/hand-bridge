from .interface_common import (
    # config,
    BaseInterface,
    FramePayload,
    get_hand_preference,
    get_thumb_tip_index,
    get_index_finger_tip_index,
    get_pinky_tip_index,
)

from ..adapters.esp32_serial import ESP32SerialAdapter

HAND_PREFERENCE = get_hand_preference("LEDInterface")

THUMB_TIP = get_thumb_tip_index()
INDEX_FINGER_TIP = get_index_finger_tip_index()
PINKY_TIP = get_pinky_tip_index()

class LightInterface(BaseInterface):
    id = "light"
    name = "Light Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context, "esp32_serial_adapter", ESP32SerialAdapter)

        self.pinch_state = False  # Track whether a pinch is currently active

    def on_frame(self, payload: FramePayload) -> None:

        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        # Compute distances
        is_pinch = self.hand_1.is_touching(THUMB_TIP, INDEX_FINGER_TIP)

        if is_pinch != self.pinch_state:
            self.pinch_state = is_pinch
            self.adapter.write_line("LIGHT TOGGLE")
            self.print_message("Pinch detected - Toggled Light")