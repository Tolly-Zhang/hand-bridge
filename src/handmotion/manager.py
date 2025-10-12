from typing import Dict
from .interfaces.base import BaseInterface
from .payload import FramePayload

class InterfaceManager:
    _instance = None

    def __new__(cls, *dargs, **kwargs):
        if not cls._instance:
            cls._instance = super(InterfaceManager, cls).__new__(cls)
        else:
            print("Warning: InterfaceManager instance already exists. Returning the existing instance.")
        return cls._instance

    def __init__(self, interfaces: Dict[str, BaseInterface]):
        self.interfaces = interfaces
        self.active_ids = list(interfaces.keys())
        self._initialized = True

    def activate_all(self) -> None:
        for interface in self.interfaces.values():
            interface.enable()
        self.active_ids = list(self.interfaces.keys())
        print("All interfaces activated")

    def deactivate_all(self) -> None:
        for interface in self.interfaces.values():
            interface.disable()
        self.active_ids = []
        print("All interfaces deactivated")
    
    def set_active(self, interface_ids: list[BaseInterface]) -> None:
        for interface_id in interface_ids:
            if interface_id in self.interfaces:
                self.active_ids.append(interface_id)
                self.interfaces[interface_id].enable()

        for name, interface in self.interfaces.items():
            if name not in interface_ids:
                interface.disable()
            
        print(f"Active interfaces set to: {self.active_ids}")

    def get_active_interfaces(self) -> list[str]:
        return self.active_ids

    def on_frame(self, payload: FramePayload) -> None:
        for active_id in self.active_ids:
            self.interfaces[active_id].on_frame(payload)
