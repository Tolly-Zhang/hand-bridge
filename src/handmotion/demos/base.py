from abc import ABC, abstractmethod
from ..payload import FramePayload

class BaseDemo(ABC):
    id: str  # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str
    enabled: bool = False

    def __init__(self, context: dict) -> None:
        self.context = context

    def enable(self) -> None:
        self.enabled = True
        print(f"Demo {self.id}: {self.name} enabled")

    def disable(self) -> None:
        self.enabled = False
        print(f"Demo {self.id}: {self.name} disabled")

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> None:
        pass
