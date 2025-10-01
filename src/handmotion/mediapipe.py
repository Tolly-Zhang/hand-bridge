from .config.config import config

import mediapipe as mp
import time

STATIC_IMAGE_MODE = config.getboolean("MediaPipe", "STATIC_IMAGE_MODE")
MAX_NUM_HANDS = config.getint("MediaPipe", "MAX_NUM_HANDS")
MIN_DETECTION_CONFIDENCE = config.getfloat("MediaPipe", "MIN_DETECTION_CONFIDENCE")
MIN_TRACKING_CONFIDENCE = config.getfloat("MediaPipe", "MIN_TRACKING_CONFIDENCE")
MODEL_COMPLEXITY = config.getint("MediaPipe", "MODEL_COMPLEXITY")

class MediaPipeHands:
    def __init__(
            self, 
            static_image_mode=STATIC_IMAGE_MODE, 
            max_num_hands=MAX_NUM_HANDS, 
            min_detection_confidence=MIN_DETECTION_CONFIDENCE, 
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE, 
            model_complexity=MODEL_COMPLEXITY
            ):
        
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity
        )
        print(
            f"MediaPipe Hands initialized with parameters:\n"
            f"  static_image_mode: {static_image_mode}\n"
            f"  max_num_hands: {max_num_hands}\n"
            f"  min_detection_confidence: {min_detection_confidence}\n"
            f"  min_tracking_confidence: {min_tracking_confidence}\n"
            f"  model_complexity: {model_complexity}"
        )

    def process_sync(self, image):
        self.results = self.hands.process(image)
        return self.results

    def annotate_image(self, image):
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS
                )
        return image

    def process_sync_with_time_ns(self, image):
        start_ns = time.time_ns()
        self.results = self.hands.process(image)
        end_ns = time.time_ns()
        processing_time = 1e-9 * (end_ns - start_ns)
        return self.results, processing_time
