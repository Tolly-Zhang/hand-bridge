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

class LEDInterface(BaseInterface):
    id = "led"
    name = "LED Interface"

    def __init__(self, context: dict) -> None:
        super().__init__(context)
        self.esp32_serial_adapter = context.get("esp32_serial_adapter")
        if not self.esp32_serial_adapter:
            raise ValueError("LEDInterface requires 'esp32_serial_adapter' in context")

        # Track LED states in a list for scalability
        self.led_states = [False, False, False, False]
        # Track whether a pinch is currently active (for edge detection)
        self.pinch_active = [False, False, False, False]

        self.hand = None  # Currently tracked hand
        self.click_threshold = CLICK_THRESHOLD  # Distance threshold for click detection

    def on_frame(self, payload: FramePayload) -> None:

        if DEBUG:
            print("[LEDInterface] on_frame called")

        super().on_frame(payload)

        for hand in payload.hands:
            if hand.handedness == HAND_PREFERENCE:
                self.hand = hand
                break

        if not self.hand:
            if DEBUG:
                print(f"[LEDInterface] No {HAND_PREFERENCE} hand detected this frame")
            return

        # Compute distances
        distances = [
            hand.calculate_xyz_distance(THUMB_TIP, INDEX_FINGER_TIP),
            hand.calculate_xyz_distance(THUMB_TIP, MIDDLE_FINGER_TIP),
            hand.calculate_xyz_distance(THUMB_TIP, RING_FINGER_TIP),
            hand.calculate_xyz_distance(THUMB_TIP, PINKY_TIP)
        ]

        if DEBUG:
            print("[LEDInterface] Distances:", ", ".join(f"{d:.4f}" for d in distances))

        for i, dist in enumerate(distances):
            is_pinch = dist < self.click_threshold

            # Edge detection: trigger only when going from not-pinched to pinched
            if is_pinch and not self.pinch_active[i]:
                # Toggle LED state
                self.led_states[i] = not self.led_states[i]
                cmd = f"LED {'H' if self.led_states[i] else 'L'} {i}"
                self.esp32_serial_adapter.write_line(cmd)

                if DEBUG:
                    print(f"[LEDInterface] Pinch detected on finger {i}. Sent: {cmd}")

            # Update pinch active state
            self.pinch_active[i] = is_pinch