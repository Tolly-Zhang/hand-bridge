from ..config.config import config

from abc import ABC, abstractmethod
from ..payload import FramePayload

INTERFACE_NAME_LENGTH = config.getint("DefaultInterface", "NAME_LENGTH")
DEBUG = config.getboolean("DEFAULT", "DEBUG")


class BaseInterface(ABC):
    id: str
    name: str
    enabled: bool

    def __init__(self, context: dict, adapter_name: str = None, adapter_type: type = None) -> None:
        self.context = context
        self.adapter = None

        if adapter_name:
            self.adapter = context.get(adapter_name)

            if not self.adapter:
                raise ValueError(f"{self.name} requires '{adapter_name}' in context")
            
            if adapter_type and not isinstance(self.adapter, adapter_type):
                raise TypeError(f"{self.name} requires '{adapter_name}' to be a {adapter_type.__name__}")

        self.hand_1 = None
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
        
        self.hand_1 = None

        if not payload.hands:
            self.print_message("No Hands Detected")
            return False  # No hands detected
        # To be implemented by subclasses
        return True

    def find_hand(self, payload: FramePayload, preference: str) -> None:
        for hand in payload.hands:
            if hand.handedness == preference: 
                self.hand_1 = hand
                break

        if not self.hand_1:
            self.print_message(f"No {preference} hand detected")
            return False
        return True