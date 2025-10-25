import time

from .config.config import config

DEFAULT_FPS = config.getint("TimeController", "FPS")

class TimeController:
    def __init__(self):
        self.start_time = 0
        self.current_time = 0
        self.elapsed = 0
        self.last_elapsed = 0
        self.delta = 0
    
    def start(self):
        self.start_time = time.time_ns()
        
    def update(self, sleep_time_s: float = 1 / DEFAULT_FPS) -> None:
        self.current_time = time.time_ns()

        if sleep_time_s > 0:
            time.sleep(max(self.last_elapsed / 1e9 + sleep_time_s - self.current_time / 1e9, 0))

        self.elapsed = self.current_time - self.start_time
        self.delta = self.elapsed - self.last_elapsed
        self.last_elapsed = self.elapsed

    def get_elapsed_time_ns(self) -> float:
        return self.elapsed

    def get_elapsed_time_s(self) -> float:
        return self.get_elapsed_time_ns() / 1e9
    
    def get_delta_ns(self) -> float:
        return self.delta
    
    def get_delta_s(self) -> float:
        return self.get_delta_ns() / 1e9

    def print_elapsed(self) -> None:
        print(f"Time (Elapsed): {self.get_elapsed_time_s():.4f}", 
              " s")

    def print_delta(self) -> None:
        print(f"Time (Delta):   {self.get_delta_s():.4f}", 
              " s")