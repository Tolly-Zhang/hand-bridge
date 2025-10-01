import time

class TimeController:
    def __init__(self):
        self.start_time_ns = 0
        self.current_time_ns = 0
        self.delta_time_ns = 0
    
    def start(self):
        self.start_time_ns = time.time_ns()
        
    def update(self):
        self.current_time_ns = time.time_ns()
        self.delta_time_ns = self.current_time_ns - self.start_time_ns
    
    def get_elapsed_time_ns(self) -> float:
        return self.delta_time_ns

    def get_elapsed_time_s(self) -> float:
        return self.delta_time_ns / 1e9