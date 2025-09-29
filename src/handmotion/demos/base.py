from abc import ABC, abstractmethod
from ..payload import FramePayload

class BaseDemo(ABC):
    id: str  # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str

    def init(self, context: dict) -> None:
        pass
    def enable(self) -> None:
        pass
    def disable(self) -> None:
        pass

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> None:
        pass
