import time

class TimeController:
    def __init__(self):
        self.start_time = 0
        self.current_time = 0
        self.elapased = 0
        self.last_elapsed = 0
        self.delta = 0
    
    def start(self):
        self.start_time = time.time_ns()
        
    def update(self):
        self.current_time = time.time_ns()
        self.elapased = self.current_time - self.start_time
        self.delta = self.elapased - self.last_elapsed
        self.last_elapsed = self.elapased
    
    def get_elapsed_time_ns(self) -> float:
        return self.elapased

    def get_elapsed_time_s(self) -> float:
        return self.elapased / 1e9

    def get_delta_ns(self) -> float:
        return self.delta
    