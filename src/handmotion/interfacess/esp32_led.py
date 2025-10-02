from .base import BaseInterface
from ..payload import FramePayload

class ESP32LEDInterface(BaseInterface):
    id = "esp32_led"
    name = "ESP32 LED Demo"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement ESP32 LED control logic
        pass
