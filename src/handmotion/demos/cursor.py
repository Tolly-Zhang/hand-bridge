from .base import BaseDemo
from ..payload import FramePayload

class CursorDemo(BaseDemo):
    id = "cursor"
    name = "Cursor Demo"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement cursor control logic
        pass
