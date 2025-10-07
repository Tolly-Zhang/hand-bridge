# HandBridge

Real-time hand (and simple gesture) tracking to control your computer and attached hardware (ESP32) with gestures. HandBridge uses **MediaPipe Hands** + **OpenCV** to extract 21 landmarks per detected hand, converts them to a canonical per‑frame payload, then routes that payload to one or more active interfaces (cursor, LEDs, motor throttle, etc.) via a lightweight manager.

The current implementation has evolved beyond the original MVP architecture in `docs/system-architecture.md`. Where the doc specifies a *single* active demo with async MediaPipe calls, the code presently:

* Uses a synchronous `process_sync` call (not `detect_async`).
* Allows **multiple interfaces enabled concurrently** (cursor, LED, motor) — though the manager logic can be refined (see Roadmap).
* Adds early hardware integrations (ESP32 LED & Motor) plus a calibration utility for pinch distance.

This README reflects the **actual code** as of the latest revision and highlights divergences from the original architecture spec.

---

## Table of Contents

1. [Features](#features)
2. [Repository Structure](#repository-structure)
3. [Quick Start](#quick-start)
	- [Prerequisites](#prerequisites)
	- [Clone & Environment Setup](#clone-and-set-up-powershell)
	- [Run (No Hardware)](#run-no-hardware)
	- [Run (With ESP32 Hardware)](#run-with-esp32-hardware)
	- [Optional: ESP32 USB Driver (CP210x)](#optional-esp32-usb-driver-cp210x)
4. [Calibration](#calibration)
5. [Configuration](#configuration)
6. [Hardware Protocols (LED & Motor)](#hardware-protocols-led--motor)
7. [Firmware (ESP32 / PlatformIO)](#firmware-esp32--platformio)
8. [How It Works](#how-it-works)
9. [Extending](#extending)
10. [Troubleshooting](#troubleshooting)
11. [Performance Tips](#performance-tips)
12. [Known Divergences vs Architecture Doc](#known-divergences-vs-architecture-doc)
13. [Known Limitations](#known-limitations)
14. [Roadmap](#roadmap)
15. [Dependencies](#dependencies)
16. [Contributing](#contributing)
17. [License](#license)
18. [Acknowledgments](#acknowledgments)

## Features

Core:
* Live webcam capture + MediaPipe Hands (21 landmarks per hand)
* Canonical per-frame payload (`FramePayload`) including metadata & world and normalized landmarks
* Interface Manager dispatches payloads to any enabled interfaces
* Pinch-distance calibration helper (captures an empirical threshold)

User / Desktop Interfaces:
* Cursor control: moves pointer (currently mapped to pinky fingertip) & clicks on pinch (thumb↔index)

Hardware Interfaces (ESP32 over serial):
* LED interface: toggles up to 4 LEDs (thumb pinch to each finger) — sends `LED H|L <channel>`
* Motor interface: maps pinch distance (thumb↔index) to a throttle value (`THROTTLE 0–10`)

Infrastructure & Extensibility:
* Configurable via `config.ini` (camera, thresholds, handedness per interface)
* Thin adapters (`CursorAdapter`, `ESP32SerialAdapter`) isolate side-effects
* Dataclass-based payload for clarity & testability

---

## Repository Structure

```
src/handmotion/
├─ core.py              # Main loop: camera → mediapipe → payload → interfaces
├─ camera.py            # Camera singleton (OpenCV)
├─ mediapipe.py         # MediaPipe Hands sync wrapper
├─ payload.py           # Dataclasses (Landmark, Hand, Meta, FramePayload)
├─ payload_builder.py   # MediaPipe results → FramePayload
├─ time_controller.py   # Loop timing & FPS estimate
├─ manager.py           # InterfaceManager (multi-enable currently)
├─ calibration/         # Pinch distance calibration utilities
├─ adapters/
│  ├─ cursor.py         # PyAutoGUI based cursor adapter
│  └─ esp32_serial.py   # Serial adapter (READY handshake, LED/THROTTLE cmds)
├─ interfaces/
│  ├─ base.py           # BaseInterface contract
│  ├─ mouse.py          # Cursor demo interface
│  ├─ led.py            # LED toggle interface (multi-finger pinch)
│  ├─ motor.py          # Motor throttle interface (pinch distance mapping)
│  └─ swipe_scroll.py   # (Placeholder / planned)
└─ config/
	├─ config.py         # INI loader
	└─ config.ini        # Parameters (camera, mediapipe, thresholds, handedness)
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

### Run (No Hardware)

```powershell
# From repo root
python .\src\handmotion\core.py
```

You’ll see an enumerated list of cameras. Enter an index. Cursor will move (pinky tip) & click on pinches.

Controls & notes:
* Quit: press `q`
* Preferred hand: `[CursorInterface] HAND_PREFERENCE`
* Click threshold: stored as `CLICK_THRESHOLD` under `[MediaPipe]` (after calibration or manual edit)
* Landmark used for motion: `PINKY_TIP` (placeholder) → change in `interfaces/mouse.py` if desired

If you have no ESP32 connected but the code attempts serial open on a non-existent port, edit `core.py` to comment out the hardware sections or update the default port in `esp32_serial.py`.

### Run (With ESP32 Hardware)

1. Connect your ESP32 and note the COM port (e.g., `COM5`).
2. Update either:
	* `DEFAULT_PORT` in `adapters/esp32_serial.py`, or
	* Dynamically call `esp32_serial_adapter.set_port("COM5")` (add near initialization in `core.py`).
3. Ensure firmware implements the handshake (`READY` → `READY_ACK`) and responds to commands (see Hardware Protocols section).
4. Launch as above. The LED & Motor interfaces are enabled depending on `InterfaceManager.set_active([...])` call.

To focus only on certain interfaces, adjust:
```python
interface_manager = InterfaceManager(demos={ ... })
interface_manager.set_active(["mouse"])  # or ["led"], ["motor"], or multiple
```

Currently `set_active` does not clear previous entries (see Roadmap). Disabled interfaces still receive IDs but guard with `self.enabled` internally.

### (Optional) Run the firmware build (ESP32)
See the [Firmware](#firmware-esp32--platformio) section for details. Current interfaces expect commands defined below (LED & THROTTLE). A readiness handshake is already implemented in the Python serial adapter.

---

## Calibration

Pinch distance varies by user / camera position. Use the built-in calibration routine (currently commented in `core.py`).

1. Uncomment the line in `core.py`:
```python
# Calibration.calibrate_pinch_distance(camera, hands, lm1=4, lm2=8, time_s=5)
```
2. Run the app. Follow on-screen instructions (perform pinches for the duration).
3. Record the printed average distance; set it as `CLICK_THRESHOLD` under `[MediaPipe]` in `config.ini`.

Future improvement: auto-write the result back into `config.ini`.

---

## Configuration

Edit `src/handmotion/config/config.ini`.

Key sections (example abbreviated — actual file may differ if calibrated):
```ini
[Camera]
INDEX = 0                ; Overridden by runtime prompt; config value can be a fallback
RESOLUTION_X = 1920
RESOLUTION_Y = 1080
FPS = 30

[MediaPipe]
STATIC_IMAGE_MODE = False
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MODEL_COMPLEXITY = 1
CLICK_THRESHOLD = 0.045889540241904704  ; Calibrated pinch distance threshold

[LandmarkIndices]
WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20

[CursorInterface]
HAND_PREFERENCE = Left

[LEDInterface]
HAND_PREFERENCE = Left
DEBUG = True

[MotorInterface]
HAND_PREFERENCE = Left
```

Tips:
* Unusual `INDEX` values (e.g., 701) are placeholders—select a valid camera at runtime.
* `CLICK_THRESHOLD` lives under `[MediaPipe]` (shared by interfaces) — unify / split later if per-interface thresholds are needed.
* Set `DEBUG = True` for verbose LED interface logs.
* For multi-monitor or aspect-ratio mismatches, consider adding normalization or mapping logic (future work).

---

## Hardware Protocols (LED & Motor)

The serial adapter performs a basic handshake and then sends human-readable ASCII commands terminated by `\n`.

### Connection Handshake
| Direction | Message       | Notes                                      |
|-----------|---------------|--------------------------------------------|
| Host → ESP32 | `READY`        | Sent once after serial port opens         |
| ESP32 → Host | `READY_ACK`    | Firmware must reply to confirm readiness  |

Python waits until `READY_ACK` before proceeding.

### LED Interface Commands
On each pinch edge (thumb to one of four other fingers), a toggle is sent:
```
LED H <i>   # Turn LED channel <i> on  (0..3)
LED L <i>   # Turn LED channel <i> off
```
Channels map (current implementation):
0 = Thumb↔Index, 1 = Thumb↔Middle, 2 = Thumb↔Ring, 3 = Thumb↔Pinky.

### Motor Interface Commands
Pinch distance maps to a throttle bucket 0–10 (clamped):
```
THROTTLE <n>
```
Transmitted every frame while active. Firmware should debounce / ignore repeats if needed.

---

---

## Firmware (ESP32 / PlatformIO)

The repository contains an (currently separate) PlatformIO project for an ESP32 at:

```
firmware/esp-32/esp-32-firmware/
```

Implements the receiving side of the `READY`/`READY_ACK`, `LED H|L <i>`, and `THROTTLE <n>` commands. Reference the examples in `board-1/` and `board-2/` (placeholders to expand). The Python side **already opens** the serial port on startup.

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

### Example Firmware Pseudocode (Handshake)
```c++
void setup() {
	Serial.begin(115200);
}

void loop() {
	if (Serial.available()) {
		String line = Serial.readStringUntil('\n');
		line.trim();
		if (line == "READY") {
			Serial.println("READY_ACK");
		} else if (line.startsWith("LED ")) {
			// Parse: LED H 0  / LED L 2
		} else if (line.startsWith("THROTTLE ")) {
			// Parse throttle integer
		}
	}
}
```

---

## How It Works

1. `core.py` enumerates cameras, opens user-selected device.
2. Each loop iteration: read frame (BGR→RGB), synchronously process with MediaPipe.
3. `payload_builder.py` constructs `FramePayload` (meta, normalized + world landmarks, handedness, confidence, in-frame heuristic).
4. `InterfaceManager.on_frame()` iterates enabled interface IDs; each interface gates on its `enabled` flag.
5. Interfaces consume the landmarks:
	* Mouse: move & pinch click
	* LED: pinch edges toggle channels
	* Motor: pinch distance → throttle scaling
6. Keyboard `q` exits; windows are closed and serial connection terminated.

Design keeps side-effects in adapters and a narrow data model. Future work may reintroduce hotkey-based switching or smoothing layers.

---

## Extending

* Create a new file in `interfaces/` extending `BaseInterface`.
* Add any hardware / OS side-effects in an adapter under `adapters/`.
* Register in `core.py` and pass required context objects (serial adapters, cursor adapter, etc.).
* For gesture logic, prefer using world landmarks for distance-based thresholds & normalized for cursor mapping.

Suggested additions:
* SwipeScrollInterface (horizontal motion → scroll)
* HUD / overlay (OpenCV debug window with FPS & pinch distances)
* Smoothing filter (EMA or Kalman) for cursor stability
* Recording/replay of `FramePayload` sequences for offline testing
* Config-driven interface enabling instead of hard-coded `set_active`

---

## Troubleshooting

- Keyboard permissions (Windows): if `q` isn’t detected, try running PowerShell as Administrator or swap to OpenCV’s `waitKey` handling.
- Cursor doesn’t move: ensure PyAutoGUI has permission (macOS accessibility / Wayland issues) & landmark chosen is visible.
- Camera not found: verify the printed camera list, try a different index, or close other apps using the webcam.
- Performance: lower the resolution or `MODEL_COMPLEXITY` in `config.ini`.
- Serial not opening: verify COM port, cable, and that no other monitor is attached; list ports via adapter `list_ports()` call or use `pio device list`.
- No `READY_ACK`: ensure firmware prints exactly `READY_ACK` with newline.

---

## Performance Tips

- Prefer 1280x720 over 1920x1080 if CPU bound.
- Lower `MODEL_COMPLEXITY` (0) for speed; keep (1) for balanced accuracy.
- Avoid unnecessary `print` spam inside tight loops (reduce LED/motor debug or add rate limiting).
- Pinch detection threshold can be tuned to reduce false clicks if jittery.

---

## Known Divergences vs Architecture Doc

| Topic | Architecture Doc | Current Code | Notes |
|-------|------------------|--------------|-------|
| MediaPipe mode | Async (`detect_async`) | Sync `process_sync` | Simpler initial implementation |
| Single active demo | Yes | Multiple enabled (manager retains list) | Manager design needs cleanup |
| Hotkeys (1/2/3) | Implemented per spec | Not implemented | Could map via `keyboard` lib |
| Cursor landmark | Index fingertip | Pinky fingertip | Placeholder; easy to change |
| Payload contents | Normalized only | Normalized + world coords + in-frame flag | Expanded for distance logic |
| ESP32 LED protocol | `LED:ON/OFF` | `LED H/L <i>` | Adopted multi-channel toggle |
| Gesture smoothing | 3–5 frame | None | Roadmap item |

---

## Known Limitations

- InterfaceManager duplicates IDs and does not truly “switch” — potential cleanup needed.
- Pinky tip placeholder for cursor control (less ergonomic than index tip).
- No temporal smoothing (cursor jitter on small tremors).
- No monitor / aspect-ratio transformation layer (assumes uniform [0,1] scaling).
- Heavy unused dependencies inflate install time (see Dependencies section).
- No automated tests or CI pipeline yet.
- Serial port is assumed present; failure path not gracefully skipping hardware interfaces.

---

---

## Roadmap

Near-term:
* Refactor `InterfaceManager` to maintain a set and truly replace active list.
* Implement hotkeys (1=cursor, 2=led, 3=motor, q=quit) using `keyboard` or OpenCV `waitKey`.
* Switch cursor landmark to index fingertip + add smoothing (EMA / windowed avg).
* Graceful fallback if serial open fails (auto-disable hardware interfaces).
* Trim unused dependencies or split into `requirements.txt` + `requirements-dev.txt`.

Medium:
* Swipe/Scroll interface.
* Overlay HUD (landmarks, FPS, pinch distances, throttle).
* Auto-calibration tool writing back to config.
* Logging abstraction with verbosity levels.

Longer-term:
* Async pipeline & optional threading.
* Recording & replay harness for regression tests.
* Plugin discovery via entry points / dynamic import.
* Packaging & PyPI distribution.

---

## Dependencies

Primary runtime (actively referenced in code):
* mediapipe
* opencv-contrib-python (contains features superset; opencv-python duplication can be removed)
* pyautogui (+ its transitive dependencies)
* keyboard
* cv2_enumerate_cameras
* pyserial (required by `esp32_serial.py`) ✅ (added — was missing)

Potentially removable / currently unused:
* jax / jaxlib / ml_dtypes / opt_einsum
* matplotlib, scipy, sentencepiece
* Django

Recommended consolidation:
* Remove `opencv-python` (keep only `opencv-contrib-python`)
* Split heavy ML / plotting stacks into `requirements-dev.txt`
* Provide a minimal install profile for end users focused on gesture control only

Future optimization: scripted dependency audit + automated pruning via a tool (e.g., `deptry`, already listed).

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