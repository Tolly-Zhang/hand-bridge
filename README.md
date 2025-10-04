# HandBridge

Real-time hand tracking to control your computer with gestures. HandBridge uses MediaPipe Hands and OpenCV to detect hands from a webcam, builds a canonical per-frame payload, and routes it to simple interfaces like a cursor controller or swipe/scroll. It’s designed to be small, readable, and easy to extend.

Refer to `docs/system-architecture.md` for the MVP architecture and module contracts.

---

## Table of Contents

1. [Features](#features)
2. [Repository Structure](#repository-structure)
3. [Quick Start](#quick-start)
	- [Prerequisites](#prerequisites)
	- [Clone & Environment Setup](#clone-and-set-up-powershell)
	- [Run the Cursor Demo](#run-the-cursor-demo)
	- [Optional: ESP32 USB Driver (CP210x)](#optional-esp32-usb-driver-cp210x)
4. [Configuration](#configuration)
5. [Firmware (ESP32 / PlatformIO)](#firmware-esp32--platformio)
6. [How It Works](#how-it-works)
7. [Extending](#extending)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tips](#performance-tips)
10. [Known Limitations](#known-limitations)
11. [Roadmap](#roadmap)
12. [Dependencies](#dependencies)
13. [Contributing](#contributing)
14. [License](#license)
15. [Acknowledgments](#acknowledgments)

## Features

- Live webcam capture and MediaPipe hands detection
- Canonical per-frame payload with normalized coordinates and handedness
- Cursor control demo (move and click via pinch)
- Pluggable interface manager to route frames to one or more interfaces
- Simple configuration via `src/handmotion/config/config.ini`

---

## Repository structure

```
src/handmotion/
├─ core.py            # Main loop: camera → mediapipe → payload → interfaces
├─ camera.py          # Camera wrapper (OpenCV), singleton
├─ mediapipe.py       # MediaPipe Hands wrapper
├─ payload.py         # Canonical dataclasses (FramePayload, Hand, Landmark, Meta)
├─ payload_builder.py # Converts MediaPipe results → FramePayload
├─ time_controller.py # Simple loop timing + FPS estimation
├─ manager.py         # InterfaceManager (routes frames to active interfaces)
├─ adapters/
│  └─ cursor.py       # CursorAdapter using PyAutoGUI
├─ interfaces/
│  ├─ base.py         # BaseInterface contract
│  ├─ mouse.py        # MouseInterface (cursor demo)
│  └─ swipe_scroll.py # SwipeScrollInterface (stub, extendable)
└─ config/
	├─ config.py       # INI loader
	└─ config.ini      # Tunable parameters (camera, mediapipe, cursor demo)
```

Additional docs: `docs/system-architecture.md`.

---

## Quick start

### Prerequisites

- Windows, macOS, or Linux with a working webcam
- Python 3.10–3.12 recommended

On Windows, the `keyboard` package may require an elevated PowerShell to read key presses globally. If you hit permission issues, either run your terminal as Administrator or disable key handling and use the console to quit.

#### (Optional) ESP32 USB Driver (CP210x)
If you plan to build / flash the firmware in `firmware/esp-32/esp-32-firmware/`, many ESP32 DevKitC / “ESP32-WROOM-32” style boards expose a Silicon Labs **CP210x USB-to-UART** bridge. Install (or verify) the Virtual COM Port (VCP) driver so your OS creates a serial COM/tty device.

- **Windows 10/11:** Install the *CP210x Universal Windows Driver* from Silicon Labs. If you downloaded a ZIP, extract it and in **Device Manager → (Board) → Update driver → Browse my computer →** point to the extracted folder. Re‑plug the board; you should see **Silicon Labs CP210x USB to UART Bridge (COMx)**.
- **macOS:** Install the **CP210x VCP** macOS driver package from Silicon Labs (reboot may be required on older versions).
- **Linux:** Driver is in the kernel. Just ensure your user has serial permissions:
	```bash
	sudo usermod -a -G dialout $USER  # log out/in afterwards
	```

Verify the port (board plugged in):
```powershell
pio device list
```
Expect something like `COM5` (Windows) / `/dev/ttyUSB0` or `/dev/tty.SLAB_USBtoUART` (Linux/macOS).

PlatformIO `platformio.ini` example (already present—adjust `upload_port`):
```ini
[env:esp32dev]
platform  = espressif32
board     = esp32dev
framework = arduino
upload_port   = COM5
upload_speed  = 921600
monitor_port  = COM5
monitor_speed = 115200
```
Troubleshooting: If upload times out, hold BOOT, tap EN/RESET, then release BOOT to enter the ROM bootloader and retry.

#### (Optional) ESP32 USB driver (CP210x)
If you plan to flash / use the ESP32 firmware in `firmware/esp-32/`, most ESP32 DevKitC / “ESP32-WROOM-32/32D” boards expose a Silicon Labs **CP210x USB-to-UART** bridge. Install (or verify) the Virtual COM Port (VCP) driver so your OS creates a serial COM/tty device.

- **Windows 10/11:** Install the *CP210x Universal Windows Driver* from Silicon Labs. If you grabbed a ZIP, extract and install via: **Device Manager → (Board) → Update driver → Browse my computer →** point to the extracted folder. Re‑plug the board; you should see **Silicon Labs CP210x USB to UART Bridge (COMx)**.
- **macOS:** Install the **CP210x VCP** macOS driver package from Silicon Labs (may require reboot on older macOS versions).
- **Linux:** Driver is built into the kernel. Just ensure you have permission for the serial device:
	```bash
	sudo usermod -a -G dialout $USER   # log out/in afterwards
	```

**Verify the port**

With the board connected:
```powershell
pio device list
```
You should see something like `COM5` (Windows) or `/dev/ttyUSB0` / `/dev/tty.SLAB_USBtoUART` (Linux/macOS).

**PlatformIO config example** (adjust the port you discovered):
```ini
[env:esp32dev]
platform  = espressif32
board     = esp32dev
framework = arduino

upload_port   = COM5          ; or /dev/ttyUSB0 on Linux, /dev/tty.SLAB_USBtoUART on macOS
upload_speed  = 921600
monitor_port  = COM5
monitor_speed = 115200
```

**Troubleshooting**
- Upload times out: hold BOOT, tap EN/RESET, then release BOOT to force the ROM bootloader and retry.
- Port not appearing (Windows): check Device Manager; reinstall driver or try a different cable/USB port.
- Permission denied (Linux): confirm you re‑logged after adding to `dialout` group.

If you prefer to keep the main README slim, you can move this block to `docs/USB-DRIVER.md` and link it here.

### Clone and set up (PowerShell)

```powershell
# 1) Clone
git clone https://github.com/Tolly-Zhang/hand-bridge.git
cd hand-bridge

# 2) Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you’re on macOS/Linux, activate with `source .venv/bin/activate` instead.

### Run the cursor demo

```powershell
# From repo root
python .\src\handmotion\core.py
```

You’ll see a list of detected cameras. Enter the index you want to use. The app will start tracking, print the screen resolution, and move the cursor based on the configured landmarks.

- Quit: press `q`
- Default hand for control: set in `config.ini` under `[CursorDemo] HAND_PREFERENCE` (e.g., `Left` or `Right`)
- Default “click”: pinch distance threshold (thumb tip ↔ index tip) controlled by `[CursorDemo] CLICK_THRESHOLD`

> Note: The current cursor mapping uses the pinky tip as a placeholder. Update the landmark index in `interfaces/mouse.py` if you want fingertip index control instead.

### (Optional) Run the firmware build (ESP32)
See the [Firmware](#firmware-esp32--platformio) section below for details. A future `ESP32LEDInterface` will use a simple serial text protocol (stub already present in `interfaces/esp32_led.py`).

---

## Configuration

Edit `src/handmotion/config/config.ini` to adjust behavior:

```ini
[Camera]
INDEX = 0             ; Default camera index (you can also pick at runtime)
RESOLUTION_X = 1920
RESOLUTION_Y = 1080
FPS = 30

[MediaPipe]
STATIC_IMAGE_MODE = False
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MODEL_COMPLEXITY = 1

[LandmarkIndices]
WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20

[CursorDemo]
HAND_PREFERENCE = Left  ; Choose Left or Right
CLICK_THRESHOLD = 0.05   ; Pinch distance threshold for click
```

Tips:
- If your camera fails to open, try a different `INDEX` or reduce the resolution.
- `MODEL_COMPLEXITY` can be tuned for speed vs accuracy (0, 1, 2 in MediaPipe).

---

## Firmware (ESP32 / PlatformIO)

The repository contains an (currently separate) PlatformIO project for an ESP32 at:

```
firmware/esp-32/esp-32-firmware/
```

This is intended for future demos (e.g., LED control reacting to pinch gestures) via the `ESP32LEDInterface` stub (`src/handmotion/interfaces/esp32_led.py`). The Python side does not yet open a serial port—so the firmware is optional for now.

### Build / Upload

From the firmware project directory:

```powershell
cd firmware/esp-32/esp-32-firmware
pio run                 # build
pio run -t upload       # flash (ensure correct upload_port in platformio.ini)
pio device monitor      # open serial monitor
```

If you need to override the port on the fly:
```powershell
pio run -t upload --upload-port COM5
```

### Planned Serial Protocol (proposed)

| Gesture | Message (ASCII line) |
|---------|----------------------|
| Pinch on  | `LED:ON`  |
| Pinch off | `LED:OFF` |

Implementation steps (future):
1. Add a lightweight serial adapter (`adapters/esp32_serial.py`).
2. Initialize adapter in `core.py` and pass through context to `ESP32LEDInterface`.
3. Detect pinch transitions (logic similar to click threshold) and send lines with `\n`.

---

## How it works

1) `core.py` opens a camera, reads frames, and sends them to `MediaPipeHands`.

2) `payload_builder.py` converts MediaPipe output into a canonical `FramePayload` that includes image dimensions, timestamp/fps, and a list of hands with normalized landmarks.

3) `manager.py` forwards each payload to the active interfaces (e.g., `MouseInterface`).

4) `interfaces/mouse.py` maps normalized coordinates to screen pixels via `adapters/cursor.py` (PyAutoGUI) and performs clicks when the pinch distance passes a threshold.

The pipeline is intentionally simple: a single loop, one canonical payload per frame, and thin adapters.

See `docs/system-architecture.md` for a more detailed architecture spec (MVP constraints, future demos, and protocol ideas). That document describes hotkey-based demo switching; NOTE: the current code only wires the cursor interface (no active demo switching yet).

---

## Extending

- Implement new interfaces under `src/handmotion/interfaces/` by extending `BaseInterface`.
- Use the `FramePayload` in `payload.py` to consume hand landmarks.
- Wire up your new interface in `core.py` by creating an instance and adding it to `InterfaceManager`.

See `docs/system-architecture.md` for the baseline interface contract and ideas for additional demos (e.g., swipe/scroll, ESP32 LED).

Suggested next interfaces:
- Swipe scroll (map lateral velocity to scroll events)
- ESP32 LED (pinch start/end → serial message)
- Overlay HUD (OpenCV window showing landmarks + FPS)
- Gesture recorder/replayer

---

## Troubleshooting

- Keyboard permissions (Windows): if `q` isn’t detected, try running PowerShell as Administrator or swap to OpenCV’s `waitKey` handling.
- Cursor doesn’t move: ensure the window focus allows PyAutoGUI to move the cursor; check that normalized x/y are in [0,1] and that your chosen landmark is visible.
- Camera not found: verify the printed camera list, try a different index, or close other apps using the webcam.
- Performance: lower the resolution or `MODEL_COMPLEXITY` in `config.ini`.

---

## Performance Tips

- Prefer 1280x720 over 1920x1080 if CPU bound.
- Lower `MODEL_COMPLEXITY` (0) for speed; keep (1) for balanced accuracy.
- Avoid unnecessary OpenCV `imshow` calls in the main loop for minimal overhead (currently disabled/commented).
- Pinch detection threshold can be tuned to reduce false clicks if jittery.

---

## Known Limitations

- Only the cursor interface is currently active; demo switching (hotkeys) described in the architecture doc is not yet implemented.
- Pinky tip is used for cursor position (placeholder) instead of index fingertip.
- No smoothing / filtering applied (raw landmark positions → cursor); can cause jitter.
- No calibration for differing aspect ratios or multi-monitor setups.
- ESP32 interface stub has no logic yet.
- Requirements file includes some heavy dependencies (e.g., jax, matplotlib, Django, scipy) that are not strictly required for the core gesture pipeline—could be trimmed later.

---

---

## Roadmap

- Finish and enable the Swipe/Scroll interface
- Add overlay HUD and a calibration wizard
- Optional ESP32 serial demo for simple device control

Additional proposed items:
- Gesture smoothing & adaptive filtering
- Multi-demo hotkey switching (align code with architecture spec)
- Minimal overlay window with selectable landmarks
- Optional lightweight requirements subset (`requirements-min.txt`)
- Continuous integration lint/test workflow

---

## Dependencies

Primary runtime libraries actually used today:
- mediapipe (hand tracking)
- opencv-python / opencv-contrib-python (camera + potential visualization)
- pyautogui (cursor control & click)
- keyboard (hotkey quit)
- cv2_enumerate_cameras (camera enumeration convenience)

Potentially removable / currently unused in code:
- jax / jaxlib / ml_dtypes / opt_einsum
- matplotlib, scipy, sentencepiece
- Django (not referenced in `src/handmotion`)

Future optimization: move unused packages to a dev/experiments extras file or prune to speed up installation.

---

## Contributing

1. Fork & branch (`feat/<topic>` or `fix/<issue>`).
2. Keep changes small and focused; update `README.md` / docs if behavior changes.
3. Run a quick manual test (`python src/handmotion/core.py`).
4. Prefer adding type hints & docstrings for new interfaces/adapters.
5. If trimming dependencies, verify the core demo still runs before PR.

Potential future tooling:
- Pre-commit hooks (formatting / import sorting)
- Automated linting (ruff / mypy) – not yet configured.

---

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

- [MediaPipe Hands](https://developers.google.com/mediapipe)
- [OpenCV](https://opencv.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)