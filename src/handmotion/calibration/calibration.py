from ..camera import Camera
from ..mediapipe import MediaPipeHands
from ..time_controller import TimeController
from ..payload_builder import PayloadBuilder

from .pinch_distance import PinchDistanceCalibration

class Calibration:
    @staticmethod
    def calibrate_pinch_distance(camera: Camera, hands: MediaPipeHands, lm1: int, lm2: int, time_s: int = 5):
        calibration = PinchDistanceCalibration()
        time_controller = TimeController()

        time_controller.start()

        print("CALIBRATION: Starting pinch distance calibration. Please perform pinch gestures with one hand in view.")
        print("Press enter to begin...")
        input()
        print("Calibration started.")

        while True:
            time_controller.update()

            camera.read()

            results = hands.process_sync(camera.get_frame_rgb())

            hands.annotate_image(camera.get_frame_bgr())
            camera.show_feed()

            payload = PayloadBuilder.build(frame_dimensions=camera.get_frame_dimensions(), 
                                        time_ns=time_controller.get_elapsed_time_ns(), 
                                        time_delta_ns=time_controller.get_delta_ns(),
                                        hands=results)
            
            calibration.add_frame(payload)

            elapsed_time = calibration.get_time_elapsed()
            if calibration.hand_queue:
                print(f"\rElapsed Time: {elapsed_time:.2f}s. Distance: {calibration.get_current_pinch_distance(calibration.hand_queue[-1], lm1, lm2):.2f}", end="")

            if elapsed_time >= time_s:
                break

        average_distance = calibration.calculate_average_pinch_distance(lm1, lm2)
        print("\nCalibration completed.")
        return average_distance