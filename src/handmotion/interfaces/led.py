from .base import BaseInterface
from ..payload import FramePayload

class LEDInterface(BaseInterface):
    id = "led"
    name = "LED Interface"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement LED control logic
        pass
