# Core loop: capture, mediapipe, payload, hotkeys

from .manager import InterfaceManager
from .payload import FramePayload
from .camera import Camera
from .mediapipe import MediaPipeHands
from .time_controller import TimeController
from .payload_builder import PayloadBuilder
from .calibration.calibration import Calibration

from .interfaces.mouse import MouseInterface
from .interfaces.led import LEDInterface
from .interfaces.motor import MotorInterface

from .adapters.cursor import CursorAdapter
from .adapters.esp32_serial import ESP32SerialAdapter

import keyboard

def main():

    # Initialize Camera, MediaPipeHands, TimeController, DemoManager instance
    camera = Camera()
    hands = MediaPipeHands()
    time_controller = TimeController()

    # Calibration.calibrate_pinch_distance(camera, hands, lm1=4, lm2=8, time_s=5)

    # esp32_serial_adapter = ESP32SerialAdapter(name="ESP32")
    # esp32_serial_adapter.list_ports()
    # esp32_serial_adapter.open_serial()
    # esp32_serial_adapter.establish_connection_handshake()

    cursor_adapter = CursorAdapter()

    # led_interface = LEDInterface(context={"esp32_serial_adapter": esp32_serial_adapter})
    # motor_interface = MotorInterface(context={"esp32_serial_adapter": esp32_serial_adapter})
    mouse_interface = MouseInterface(context={"mouse_controller": cursor_adapter})

    interface_manager = InterfaceManager(interfaces={
        # "led": led_interface,
        # "motor": motor_interface,
        "mouse": mouse_interface
    })

    interface_manager.set_active(["mouse"])

    time_controller.start()

    while True:

        time_controller.update(0.05)

        camera.read()

        results = hands.process_sync(camera.get_frame_rgb())
        hands.annotate_image(camera.get_frame_bgr())

        payload: FramePayload = PayloadBuilder.build_payload(frame_dimensions=camera.get_frame_dimensions(), 
                                                             time_ns=time_controller.get_elapsed_time_ns(), 
                                                             time_delta_ns=time_controller.get_delta_ns(),
                                                             hands=results)
        # payload.print_summary()

        camera.show_feed()

        interface_manager.on_frame(payload)

        # Exit on 'q' key press
        if keyboard.is_pressed('q'):
            print("Exiting...")
            break

        # time.sleep(1)  # Delay for testing purposes

    camera.shutdown()  # Ensure camera is shutdown properly
    # esp32_serial_adapter.close_serial()

if __name__ == "__main__":
    main()