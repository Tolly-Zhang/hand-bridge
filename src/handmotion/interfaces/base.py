from ..config.config import config

from abc import ABC, abstractmethod
from ..payload import FramePayload

INTERFACE_NAME_LENGTH = config.getint("DefaultInterface", "NAME_LENGTH")
DEBUG = config.getboolean("DEFAULT", "DEBUG")

class BaseInterface(ABC):
    id: str  # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str
    enabled: bool

    def __init__(self, context: dict, adapter: str) -> None:
        self.context = context
        self.adapter = context.get(adapter)
        if not self.adapter:
            raise ValueError(f"{self.name} requires '{adapter}' in context")

        self.hand = None
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True
        self.print_message("Enabled")

    def disable(self) -> None:
        self.enabled = False
        self.print_message("Disabled")

    def print_message(self, message: str) -> None:
        if DEBUG:
            print(f"[{self.name}] {message}")

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> bool:

        if not self.enabled:
            return False
        
        self.hand = None

        if not payload.hands:
            self.print_message("No Hands Detected")
            return False  # No hands detected
        # To be implemented by subclasses
        return True

    def find_hand(self, payload: FramePayload, preference: str) -> None:
        for hand in payload.hands:
            if hand.handedness == preference: 
                self.hand = hand
                break

        if not self.hand:
            self.print_message(f"No {preference} hand detected")
            return False
        return True