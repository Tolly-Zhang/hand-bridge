# HandBridge

Real-time hand tracking to control your computer with gestures. HandBridge uses MediaPipe Hands and OpenCV to detect hands from a webcam, builds a canonical per-frame payload, and routes it to simple interfaces like a cursor controller or swipe/scroll. It’s designed to be small, readable, and easy to extend.

Refer to `docs/system-architecture.md` for the MVP architecture and module contracts.

---

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

## How it works

1) `core.py` opens a camera, reads frames, and sends them to `MediaPipeHands`.

2) `payload_builder.py` converts MediaPipe output into a canonical `FramePayload` that includes image dimensions, timestamp/fps, and a list of hands with normalized landmarks.

3) `manager.py` forwards each payload to the active interfaces (e.g., `MouseInterface`).

4) `interfaces/mouse.py` maps normalized coordinates to screen pixels via `adapters/cursor.py` (PyAutoGUI) and performs clicks when the pinch distance passes a threshold.

The pipeline is intentionally simple: a single loop, one canonical payload per frame, and thin adapters.

---

## Extending

- Implement new interfaces under `src/handmotion/interfaces/` by extending `BaseInterface`.
- Use the `FramePayload` in `payload.py` to consume hand landmarks.
- Wire up your new interface in `core.py` by creating an instance and adding it to `InterfaceManager`.

See `docs/system-architecture.md` for the baseline interface contract and ideas for additional demos (e.g., swipe/scroll, ESP32 LED).

---

## Troubleshooting

- Keyboard permissions (Windows): if `q` isn’t detected, try running PowerShell as Administrator or swap to OpenCV’s `waitKey` handling.
- Cursor doesn’t move: ensure the window focus allows PyAutoGUI to move the cursor; check that normalized x/y are in [0,1] and that your chosen landmark is visible.
- Camera not found: verify the printed camera list, try a different index, or close other apps using the webcam.
- Performance: lower the resolution or `MODEL_COMPLEXITY` in `config.ini`.

---

## Roadmap

- Finish and enable the Swipe/Scroll interface
- Add overlay HUD and a calibration wizard
- Optional ESP32 serial demo for simple device control

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

- [MediaPipe Hands](https://developers.google.com/mediapipe)
- [OpenCV](https://opencv.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)