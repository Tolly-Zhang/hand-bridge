from typing import Dict
from .demos.base import BaseDemo
from .payload import FramePayload

class DemoManager:
    def __init__(self, demos: Dict[str, BaseDemo]):
        self.demos = demos
        self.active_id = None

    def set_active(self, demo_id: str) -> None:
        if demo_id in self.demos:
            self.active_id = demo_id
            self.demos[demo_id].enable()
            for k, v in self.demos.items():
                if k != demo_id:
                    v.disable()
        print(f"Active demo set to: {self.active_id}")

    def get_active(self) -> str:
        return self.active_id

    def on_frame(self, payload: FramePayload) -> None:
        if self.active_id:
            self.demos[self.active_id].on_frame(payload)
