from typing import Dict
from .demos.base import BaseDemo
from .payload import FramePayload

class DemoManager:
    _instance = None

    def __new__(cls, demos: Dict[str, BaseDemo]):
        if cls._instance is None:
            cls._instance = super(DemoManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, demos: Dict[str, BaseDemo]):
        if self._initialized:
            return
        self.demos = demos
        self.active_ids = list(demos.keys())
        self._initialized = True

    @staticmethod
    def get_instance(demos: Dict[str, BaseDemo] = None):
        if DemoManager._instance is None:
            if demos is None:
                raise ValueError("DemoManager must be initialized with demos first.")
            DemoManager(demos)
        return DemoManager._instance

    def set_active(self, demo_ids: list[BaseDemo]) -> None:
        for demo_id in demo_ids:
            if demo_id in self.demos:
                self.active_ids.append(demo_id)
                self.demos[demo_id].enable()
        for k, v in self.demos.items():
            if k not in demo_ids:
                v.disable()
        print(f"Active demos set to: {self.active_ids}")

    def get_active(self) -> list[str]:
        return self.active_ids

    def on_frame(self, payload: FramePayload) -> None:
        for active_id in self.active_ids:
            self.demos[active_id].on_frame(payload)
