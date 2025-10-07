from typing import List

from ..payload import FramePayload, Hand

DEFAULT_TIME_RANGE_S = 5  # Default time range in seconds for calibration

class PinchDistanceCalibration:

    def __init__(self):
        self.hand_queue: List[Hand] = []
        self.start_time: float = 0.0
        self.current_time: float = 0.0
    
    def add_frame(self, payload: FramePayload) -> None:

        if not payload.hands:
            print("No hands detected. Rejecting frame.")
            return
        
        if len(payload.hands) > 1:
            print("Warning: More than one hand detected. Rejecting frame.")
            return

        if len(payload.hands[0].world_landmarks) != 21:
            print("Warning: Hand does not have 21 landmarks. Rejecting frame.")
            return
        
        self.hand_queue.append(payload.hands[0])

        if len(self.hand_queue) == 1:
            self.start_time = payload.meta.timestamp_ns / 1e9  # Convert to seconds

        self.current_time = payload.meta.timestamp_ns / 1e9  # Convert to seconds

    def get_time_elapsed(self) -> float:
        return self.current_time - self.start_time
    
    def get_current_pinch_distance(self, hand: Hand, lm1: int, lm2: int) -> float:
        if not self.hand_queue:
            print("No frames available for calibration.")
            return 0.0
        
        lm1 = hand.world_landmarks[lm1]
        lm2 = hand.world_landmarks[lm2]
        dist = ((lm1.x - lm2.x) ** 2 + 
                (lm1.y - lm2.y) ** 2 + 
                (lm1.z - lm2.z) ** 2) ** 0.5
        return dist

    def calculate_average_pinch_distance(self, lm_index_1: int, lm_index_2: int) -> float:
        if not self.hand_queue:
            print("No frames available for calibration.")
            return 0.0
        
        total_distance = 0.0
        count = 0

        for hand in self.hand_queue:
            dist = self.get_current_pinch_distance(hand, lm_index_1, lm_index_2)
            total_distance += dist
            count += 1
        
        average_distance = total_distance / count if count > 0 else 0.0

        print(f"Average pinch distance between landmarks {lm_index_1} and {lm_index_2}: {average_distance:.4f}")
        return average_distance
