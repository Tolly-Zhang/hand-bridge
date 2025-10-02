from .base import BaseInterface
from ..payload import FramePayload

class SwipeScrollDemo(BaseInterface):
    id = "swipe_scroll"
    name = "Swipe Scroll Demo"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement swipe/scroll logic
        pass
