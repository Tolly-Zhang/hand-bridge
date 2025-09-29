from .base import BaseDemo
from ..payload import FramePayload
from ..adapters.mouse import MouseController

class CursorDemo(BaseDemo):
    id = "cursor"
    name = "Cursor Demo"
    hand_preference = "R"  # Prefer right hand for cursor control

    def __init__(self, context: dict) -> None:
        super().__init__(context)
        self.mouse = context.get("mouse_controller")
        if not self.mouse:
            raise ValueError("CursorDemo requires a MouseController in context")
        
        self.hand = None  # Currently tracked hand
        self.pos_x, self.pos_y = 0.5, 0.5  # Start in the center of the screen
    
    def enable(self) -> None:
        super().enable()
        # Additional setup if needed
        
    def disable(self) -> None:
        super().disable()
        # Additional teardown if needed

    def on_frame(self, payload: FramePayload) -> None:
        # TODO: Implement cursor control logic
        pass
