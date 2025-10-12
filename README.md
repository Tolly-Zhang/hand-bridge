## HandBridge

Real-time hand and gesture tracking for desktop control with optional ESP32 hardware integrations. HandBridge uses **MediaPipe Hands** plus **OpenCV** to extract per-frame landmarks, builds a canonical payload, and forwards it to whichever interfaces are active (mouse, LEDs, motor).

The codebase has drifted from the early MVP documented in `docs/system-architecture.md`. This README reflects the current implementation, while calling out any notable differences from that architecture document.

---

## Table of Contents

1. [Features](#features)
2. [Repository Structure](#repository-structure)
3. [Quick Start](#quick-start)
	- [Prerequisites](#prerequisites)
	- [Clone & Environment Setup](#clone--environment-setup)
	- [Run Without Hardware](#run-without-hardware)
	- [Enable ESP32 Hardware](#enable-esp32-hardware)
4. [ESP32 USB Driver (Optional)](#esp32-usb-driver-optional)
5. [Calibration](#calibration)
6. [Configuration](#configuration)
7. [Hardware Protocols](#hardware-protocols)
8. [Firmware Project](#firmware-project)
9. [How It Works](#how-it-works)
10. [Extending](#extending)
11. [Troubleshooting](#troubleshooting)
12. [Performance Tips](#performance-tips)
13. [Differences vs Architecture Doc](#differences-vs-architecture-doc)
14. [Known Limitations](#known-limitations)
15. [Roadmap](#roadmap)
16. [Dependencies](#dependencies)
17. [Contributing](#contributing)
18. [License](#license)
19. [Acknowledgments](#acknowledgments)

---

## Features

- Synchronous MediaPipe Hands pipeline with camera auto-enumeration and manual index selection.
- Canonical `FramePayload` dataclass that stores metadata, normalized landmarks, world landmarks, and in-frame flags.
- Singleton `InterfaceManager` that cleanly enables/disables a set of interfaces every time `set_active` is called.
- Cursor control via `MouseInterface`: configurable tracker landmark (default index fingertip) and pinch-to-click.
- ESP32-focused hardware interfaces (`LEDInterface`, `MotorInterface`) that communicate through a shared serial adapter (`ESP32SerialAdapter`) with a READY/READY_ACK handshake.
- Pinch-distance calibration helper for tuning click thresholds.

---

## Repository Structure

```
src/handmotion/
├─ core.py              # Main loop (camera → mediapipe → payload → interfaces)
├─ camera.py            # Camera singleton with optional camera selection prompt
├─ mediapipe.py         # MediaPipe Hands wrapper (sync)
├─ payload.py           # Payload dataclasses
├─ payload_builder.py   # Converts MediaPipe results into FramePayload
├─ time_controller.py   # Tracks elapsed time and frame delta
├─ manager.py           # InterfaceManager singleton (activates/deactivates interfaces)
├─ calibration/
│  ├─ calibration.py    # Pinch-distance calibration routine
│  └─ pinch_distance.py # Helper logic for pinch statistics
├─ adapters/
│  ├─ cursor.py         # PyAutoGUI wrapper for normalized cursor moves/clicks
│  └─ esp32_serial.py   # PySerial wrapper with handshake helpers
├─ interfaces/
│  ├─ base.py           # BaseInterface contract (enable/disable + hand helpers)
│  ├─ interface_common.py # Config helpers shared by interfaces
│  ├─ led.py            # Finger pinch toggles LED channels over serial
│  ├─ motor.py          # Thumb–index distance mapped to throttle buckets
│  └─ mouse.py          # Cursor control + pinch click
└─ config/
	├─ config.py         # Config parser bootstrap
	└─ config.ini        # Runtime configuration

docs/system-architecture.md  # Original MVP architecture notes (historic)
firmware/esp-32/esp-32-firmware/ # PlatformIO project for ESP32 firmware
```

---

## Quick Start

### Prerequisites

- Windows, macOS, or Linux
- Python 3.10 – 3.12 (tested)
- Webcam accessible by OpenCV

Windows-only note: the `keyboard` package may need an elevated PowerShell to capture the `q` key globally. If the exit key is ignored, run the shell as Administrator or adjust the quit logic to rely on OpenCV `waitKey`.

### Clone & Environment Setup

```powershell
git clone https://github.com/Tolly-Zhang/hand-bridge.git
cd hand-bridge

python -m venv .venv
\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS/Linux activation: `source .venv/bin/activate`.

### Run Without Hardware

```powershell
python -m handmotion.core
```

- Choose a camera index when prompted (prompt enabled by `[Camera] ASK_FOR_INDEX = True`).
- Move your index finger to steer the cursor (landmark index set in config).
- Pinch thumb and index to trigger a left click.
- Press `q` to exit.

The viewport window name defaults to `[Camera] WINDOW_NAME`. Frames are annotated with hand landmarks for visual feedback.

### Enable ESP32 Hardware

Hardware support is present but disabled by default in `core.py`. To use it:

1. Instantiate the serial adapter and open the port:
	```python
	esp32_serial_adapter = ESP32SerialAdapter(name="ESP32")
	esp32_serial_adapter.list_ports()
	esp32_serial_adapter.open_serial()
	esp32_serial_adapter.establish_connection_handshake()
	```
2. Pass the adapter into the LED and/or motor interfaces and register them with the `InterfaceManager`:
	```python
	led_interface = LEDInterface({"esp32_serial_adapter": esp32_serial_adapter})
	motor_interface = MotorInterface({"esp32_serial_adapter": esp32_serial_adapter})
	interface_manager = InterfaceManager({
	    "mouse": mouse_interface,
	    "led": led_interface,
	    "motor": motor_interface,
	})
	interface_manager.set_active(["mouse", "led", "motor"])
	```
3. Update the serial port in `config.ini` (`[ESP32Adapter] PORT = COMx`) or call `set_port()` before opening the connection.

The Python adapter expects the firmware to respond with `READY_ACK` after it sends `READY`. See [Hardware Protocols](#hardware-protocols) for details.

---

## ESP32 USB Driver (Optional)

Many ESP32 DevKitC / “ESP32-WROOM-32” boards expose the Silicon Labs CP210x USB-to-UART bridge. Install the VCP driver so the board appears as a serial device:

- **Windows 10/11:** Install the *CP210x Universal Windows Driver* from Silicon Labs. In Device Manager, update the driver for the board and point to the extracted folder. Replug the board; it should appear as **Silicon Labs CP210x USB to UART Bridge (COMx)**.
- **macOS:** Install the CP210x VCP package from Silicon Labs (restart on older macOS versions).
- **Linux:** Driver ships with the kernel. Ensure your user is in the `dialout` (or equivalent) group: `sudo usermod -a -G dialout $USER` then log out/in.

Verify connectivity with `pio device list` or `python -m serial.tools.list_ports`.

---

## Calibration

Pinch distance varies per person and camera placement. The helper in `Calibration.calibrate_pinch_distance` collects pinch samples and reports an average distance that you can copy into `[MediaPipe] CLICK_THRESHOLD` in `config.ini`.

Usage (manual step in `core.py`):

```python
# Calibration.calibrate_pinch_distance(camera, hands, lm1=4, lm2=8, time_s=5)
```

Uncomment the line, run the script, follow on-screen instructions, then re-comment once finished. A future enhancement will persist the result automatically.

---

## Configuration

All runtime settings live in `src/handmotion/config/config.ini`. Key entries:

```ini
[Camera]
INDEX = 701               ; Placeholder, overridden when asked at runtime
ASK_FOR_INDEX = True
RESOLUTION_X = 1920
RESOLUTION_Y = 1080
FPS = 30
WINDOW_NAME = "Camera Feed"

[MediaPipe]
MAX_NUM_HANDS = 2
MODEL_COMPLEXITY = 1
CLICK_THRESHOLD = 0.045889540241904704

[CursorInterface]
HAND_PREFERENCE = Left
TRACKER_LANDMARK = 8      ; 8 = index fingertip

[LEDInterface]
HAND_PREFERENCE = Left
DEBUG = True

[MotorInterface]
HAND_PREFERENCE = Left

[ESP32Adapter]
PORT = COM3
BAUDRATE = 115200
```

`TRACKER_LANDMARK` comes directly from the indices defined under `[LandmarkIndices]`, allowing quick experimentation (e.g., swap to 12 for middle finger). Ensure the COM port matches your board before opening the serial connection.

---

## Hardware Protocols

The serial protocol is newline-terminated ASCII:

- **Handshake:** Host sends `READY`, firmware responds `READY_ACK`.
- **LED toggle:** `LED H|L <channel>` toggles one of four channels (thumb-index through thumb-pinky).
- **Motor throttle:** `THROTTLE <0–10>` maps pinch distance to a coarse throttle bucket.

`LEDInterface` performs edge detection so commands fire only on pinch transitions. `MotorInterface` clamps output between 0 and 10 to simplify firmware-side handling.

---

## Firmware Project

`firmware/esp-32/esp-32-firmware` is a PlatformIO project intended to mirror the Python protocol.

Typical workflow:

```powershell
cd firmware/esp-32/esp-32-firmware
pio run                 # build
pio run -t upload       # flash (set upload_port if needed)
pio device monitor      # open serial monitor
```

Override the upload port inline: `pio run -t upload --upload-port COM5`.

The firmware should read lines with `Serial.readStringUntil('\n')`, trim them, and branch on `READY`, `LED`, and `THROTTLE` commands as described above.

---

## How It Works

1. `Camera` enumerates video devices (if configured) and streams frames in BGR + RGB.
2. `MediaPipeHands.process_sync` returns hand landmarks for the current frame.
3. `PayloadBuilder` converts raw landmarks into the strongly typed `FramePayload` dataclasses.
4. `InterfaceManager` loops over the active interface IDs (which are reset on every `set_active` call) and invokes `on_frame` on each interface.
5. Each interface gates on `self.enabled` and the requested hand preference before executing side effects through its adapter.
6. When `q` is pressed, the script exits gracefully and the camera shuts down.

This architecture keeps OS/hardware side effects in adapters, enabling easier testing and substitution when adding new devices.

---

## Extending

- Create a new class in `interfaces/` extending `BaseInterface`.
- Inject any dependencies via the `context` dictionary; they are lazily instantiated through adapters if missing.
- Register the interface in `core.py` and include it in `interface_manager.set_active([...])`.
- For hardware, add a dedicated adapter under `adapters/` to isolate serial/network logic.

Ideas: swipe-to-scroll interface, on-screen HUD overlay, smoothing filters, or offline payload record/replay tools.

---

## Troubleshooting

- `q` key ignored on Windows → run PowerShell as Administrator or change quit logic.
- Cursor stuck → ensure PyAutoGUI has accessibility permissions (macOS) or Wayland compatibility.
- No camera preview → confirm index selection, free the device from other apps, or disable the prompt (`ASK_FOR_INDEX = False`).
- Serial errors → verify COM port, cable, and that no monitor is running; list ports via `ESP32SerialAdapter.list_ports()`.
- Missing `READY_ACK` → confirm the firmware echoes `READY_ACK` exactly (uppercase, newline).

---

## Performance Tips

- Lower camera resolution (e.g., 1280×720) or `MODEL_COMPLEXITY = 0` if CPU-bound.
- Reduce verbose logging inside tight loops to avoid console bottlenecks.
- Adjust `CLICK_THRESHOLD` if pinch detection is too sensitive or laggy.

---

## Differences vs Architecture Doc

| Topic | Architecture Doc | Current State |
|-------|------------------|---------------|
| MediaPipe mode | Async `detect_async` | Sync `process_sync` for simplicity |
| Interface switching | Hotkey-driven single demo | Explicit `set_active` list (no hotkeys yet) |
| Cursor landmark | Hard-coded index finger | Configurable via `[CursorInterface] TRACKER_LANDMARK` (defaults to index finger) |
| Payload fields | Normalized landmarks only | Normalized + world landmarks + metadata |
| Serial protocol | `LED:ON/OFF` | `LED H|L <channel>` + `THROTTLE <n>` commands |

Refer to `docs/system-architecture.md` for the historical plan.

---

## Known Limitations

- No temporal smoothing; cursor jitter is possible with noisy input.
- Hardware interfaces require manual enabling/editing in `core.py`.
- No automated tests or CI pipeline.
- Serial failure cases (e.g., port missing) rely on manual guarding by the user.

---

## Roadmap

- Add hotkeys to toggle interfaces at runtime.
- Persist calibration results directly to `config.ini`.
- Introduce smoothing/filters for cursor control.
- Improve hardware setup flow (auto-disable when serial open fails).
- Add optional HUD overlay and swipe/scroll gestures.

---

## Dependencies

Current runtime dependencies (see `requirements.txt`):

- `cv2_enumerate_cameras`
- `keyboard`
- `mediapipe`
- `opencv-python`
- `PyAutoGUI`
- `pyserial`

If you prefer OpenCV contrib features, swap `opencv-python` for `opencv-contrib-python`. Keep `requirements.txt` minimal for faster installs.

---

## Contributing

1. Fork the repo and create a feature branch.
2. Keep PRs focused and update documentation when behavior changes.
3. Run `python -m handmotion.core` (with or without hardware) to sanity check.
4. Add type hints or docstrings for new interfaces/adapters where clarity helps.

Potential future tooling: pre-commit hooks, linting (ruff/mypy), or simple CI smoke tests.

---

## License

MIT License — see `LICENSE` for details.

---

## Acknowledgments

- [MediaPipe Hands](https://developers.google.com/mediapipe)
- [OpenCV](https://opencv.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)