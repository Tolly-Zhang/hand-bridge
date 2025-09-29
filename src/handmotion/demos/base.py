from abc import ABC, abstractmethod
from ..payload import FramePayload

class BaseDemo(ABC):
    id: str  # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str

    def __init__(self, context: dict) -> None:
        self.context = context

    def enable(self) -> None:
        print(f"Demo {self.id}: {self.name} enabled")
        
    def disable(self) -> None:
        print(f"Demo {self.id}: {self.name} disabled")

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> None:
        pass
