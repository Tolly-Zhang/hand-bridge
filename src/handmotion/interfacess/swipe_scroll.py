from .base import BaseDemo
from ..payload import FramePayload

class SwipeScrollInterface(BaseDemo):
    id = "swipe_scroll"
    name = "Swipe Scroll Demo"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement swipe/scroll logic
        pass
