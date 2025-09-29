from .base import BaseDemo
from ..payload import FramePayload

class Esp32LedDemo(BaseDemo):
    id = "esp32_led"
    name = "ESP32 LED Demo"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement ESP32 LED control logic
        pass
