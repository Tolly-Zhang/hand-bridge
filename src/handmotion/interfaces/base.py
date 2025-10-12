from ..config.config import config

from abc import ABC, abstractmethod
from ..payload import FramePayload

INTERFACE_NAME_LENGTH = config.getint("DefaultInterface", "NAME_LENGTH")

class BaseInterface(ABC):
    id: str  # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str
    enabled: bool

    def __init__(self, context: dict) -> None:
        self.context = context
        self.hand = None
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True
        print(f"{self.name:<{INTERFACE_NAME_LENGTH}} Enabled")

    def disable(self) -> None:
        self.enabled = False
        print(f"{self.name:<{INTERFACE_NAME_LENGTH}} Disabled")

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> None:
        if not self.enabled:
            return
        
        self.hand = None

        if not payload.hands:
            return  # No hands detected
        # To be implemented by subclasses
