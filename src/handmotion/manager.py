from typing import Dict
from .demos.base import BaseInterface
from .payload import FramePayload

class InterfaceManager:
    _instance = None

    def __new__(cls, demos: Dict[str, BaseInterface]):
        if not cls._instance:
            cls._instance = super(InterfaceManager, cls).__new__(cls)
        else:
            print("Warning: DemoManager instance already exists. Returning the existing instance.")
        return cls._instance

    def __init__(self, demos: Dict[str, BaseInterface]):
        self.demos = demos
        self.active_ids = list(demos.keys())
        self._initialized = True

    @staticmethod
    def get_instance(demos: Dict[str, BaseInterface] = None):
        if InterfaceManager._instance is None:
            if demos is None:
                raise ValueError("DemoManager must be initialized with demos first.")
            InterfaceManager(demos)
        return InterfaceManager._instance

    def set_active(self, demo_ids: list[BaseInterface]) -> None:
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
