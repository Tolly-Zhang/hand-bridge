from .base import BaseInterface
from ..payload import FramePayload

class SwipeScrollInterface(BaseInterface):
    id = "swipe_scroll"
    name = "Swipe Scroll Interface"

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement swipe/scroll logic
        pass
