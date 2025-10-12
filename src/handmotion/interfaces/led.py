from .interface_common import (
    # config,
    BaseInterface,
    FramePayload,
    get_hand_preference,
    get_thumb_tip_index,
    get_index_finger_tip_index,
    get_middle_finger_tip_index,
    get_ring_finger_tip_index,
    get_pinky_tip_index,
)

from ..adapters.esp32_serial import ESP32SerialAdapter

HAND_PREFERENCE = get_hand_preference("LEDInterface")

THUMB_TIP = get_thumb_tip_index()
INDEX_FINGER_TIP = get_index_finger_tip_index()
MIDDLE_FINGER_TIP = get_middle_finger_tip_index()
RING_FINGER_TIP = get_ring_finger_tip_index()
PINKY_TIP = get_pinky_tip_index()

class LEDInterface(BaseInterface):
    id = "led"
    name = "LED Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context, "esp32_serial_adapter", ESP32SerialAdapter)

        # Track LED states in a list for scalability
        self.led_states = [False, False, False, False]
        # Track whether a pinch is currently active (for edge detection)
        self.pinch_active = [False, False, False, False]

    def on_frame(self, payload: FramePayload) -> None:

        if not super().on_frame(payload):
            return

        if not super().find_hand(payload, HAND_PREFERENCE):
            return

        self.pinch_active = [
            self.hand_1.is_touching(THUMB_TIP, INDEX_FINGER_TIP),
            self.hand_1.is_touching(THUMB_TIP, MIDDLE_FINGER_TIP),
            self.hand_1.is_touching(THUMB_TIP, RING_FINGER_TIP),
            self.hand_1.is_touching(THUMB_TIP, PINKY_TIP)
        ]

        for i, is_pinch in enumerate(self.pinch_active):

            # Edge detection: trigger only when going from not-pinched to pinched
            if is_pinch != self.pinch_active[i]:
                # Toggle LED state
                self.led_states[i] = not self.led_states[i]
                cmd = f"LED {'H' if self.led_states[i] else 'L'} {i}"
                self.adapter.write_line(cmd)

                self.print_message(f"Pinch detected on finger {i}. Sent: {cmd}")

            # Update pinch active state
            self.pinch_active[i] = is_pinch