# System Architecture (MVP, 1-Week Build)

## MVP Goals (scoped)

* Real-time hand tracking with MediaPipe.
* One **canonical payload** per frame (normalized `[0,1]` coords + handedness).
* **One active demo at a time** (hotkeys to switch):
  `CursorDemo`, `SwipeScrollDemo`, *(optional)* `Esp32LedDemo`.
* Simple adapters for mouse/scroll (and optional serial).
* Clean, readable code that’s easy to extend later.

---

## Processing Loop (single-threaded, simple)

```
Capture frame (OpenCV) ─▶ MediaPipe detect_for_video(...)
                               │
                               ▼
                      Build FramePayload
                               │
                               ▼
                 DemoManager.forward_to_active_demo(...)
                               │
                               ├─ CursorDemo ──▶ MouseController
                               ├─ SwipeScrollDemo ─▶ Keyboard/Scroll
                               └─ Esp32LedDemo ─▶ Serial (optional)
```

* **One loop, one payload, one active demo.**
* Minimal state; no overlay or event bus; prints small HUD/help to the console.

---

## MediaPipe Operating Mode (MVP choice)

* **Default:** `VIDEO` mode (`detect_for_video(image, timestamp_ms)`), called from the capture loop.
  *Why:* dead simple, avoids async/callback plumbing, still “live” at 30 FPS.
* **Future option:** `LIVE_STREAM` (swap in later with a small wrapper change).

**Timing:** compute `timestamp_ms` from a monotonic clock; estimate FPS in the loop.

---

## Canonical Payload (lean)

Minimal data model passed to the active demo only.

### Dataclasses (signatures only; for Copilot to scaffold)

```python
# src/handmotion/payload.py
from dataclasses import dataclass
from typing import List, Literal

Handedness = Literal["Left", "Right"]

@dataclass
class Landmark:
    x_norm: float  # [0,1]
    y_norm: float  # [0,1]
    z_norm: float  # MediaPipe relative depth (optional use)

@dataclass
class Hand:
    handedness: Handedness
    confidence: float
    landmarks: List[Landmark]  # len == 21

@dataclass
class Meta:
    timestamp_ns: int
    width: int
    height: int
    fps_estimate: float

@dataclass
class FramePayload:
    meta: Meta
    hands: List[Hand]
```

**Notes**

* Only **normalized** coordinates are required for MVP; no px→cm calibration.
* If no hands are detected, `hands=[]` and demos should idle safely.

---

## Module Map (lean layout)

```
src/handmotion/
├─ core.py            # capture loop + mediapipe + payload builder + hotkeys
├─ payload.py         # dataclasses above
├─ manager.py         # DemoManager (tracks active demo id, forwards payload)
├─ adapters/
│  ├─ mouse.py        # MouseController (move/click/scroll)
│  └─ esp32_serial.py # optional: simple serial adapter
└─ demos/
   ├─ base.py         # BaseDemo interface
   ├─ cursor.py       # CursorDemo (index fingertip -> screen)
   ├─ swipe_scroll.py # SwipeScrollDemo (x-velocity -> scroll)
   └─ esp32_led.py    # optional: pinch on/off -> "LED:ON"/"LED:OFF"
```

---

## Demo Contract (MVP)

```python
# src/handmotion/demos/base.py
from abc import ABC, abstractmethod
from ..payload import FramePayload

class BaseDemo(ABC):
    id: str         # e.g. "cursor", "swipe_scroll", "esp32_led"
    name: str       # friendly name

    def init(self, context: dict) -> None: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...

    @abstractmethod
    def on_frame(self, payload: FramePayload) -> None: ...
```

**Context** passed at `init`: `{"mouse": MouseController, "serial": ESP32SerialAdapter|None, "config": dict}`.
Each demo reads `payload.hands` and decides what to do. No cross-demo coupling.

---

## Demo Behaviors (spec)

### CursorDemo

* **Input:** right-hand **index fingertip** (`landmarks[8].(x_norm,y_norm)`).
* **Map:** normalized → screen pixels; clamp to bounds; 3–5 frame smoothing.
* **Click:** pinch threshold (distance index tip ↔ thumb tip) or “tap” on rapid in/out.

### SwipeScrollDemo

* **Input:** palm proxy (e.g., average of wrist + MCPs) or index MCP (`landmarks[5]`).
* **Detect:** Δx over ~100–150 ms; if |Δx|>τ, emit a burst of scroll events.

  * Option A: horizontal scroll (Δx→dx).
  * Option B: map sideways swipe to up/down scroll if preferred.

### Esp32LedDemo (optional)

* **Pinch start:** write `b"LED:ON\n"` to serial.
* **Pinch end:** write `b"LED:OFF\n"`.
* **Port/baud** from config; reconnect if needed.

---

## Adapters (thin, testable)

```python
# adapters/mouse.py
class MouseController:
    def move_norm(self, x: float, y: float) -> None: ...
    def click(self, button: str = "left") -> None: ...
    def scroll(self, dx: int = 0, dy: int = 0) -> None: ...
```

```python
# adapters/esp32_serial.py (optional)
class ESP32SerialAdapter:
    def connect(self, port: str, baud: int = 115200) -> None: ...
    def write_line(self, s: str) -> None: ...
    def close(self) -> None: ...
```

---

## DemoManager (one active demo)

```python
# src/handmotion/manager.py
class DemoManager:
    def __init__(self, demos: dict[str, BaseDemo]): ...
    def set_active(self, demo_id: str) -> None: ...
    def get_active(self) -> str: ...
    def on_frame(self, payload: FramePayload) -> None: ...
```

* Holds a dict of demos (instantiated and `init(...)`ed at startup).
* Forwards each frame to **only** the active demo.
* Ignores frames if there’s no active demo (e.g., startup).

---

## Hotkeys (no overlay UI)

* `1` → `DemoManager.set_active("cursor")`
* `2` → `DemoManager.set_active("swipe_scroll")`
* `3` → `DemoManager.set_active("esp32_led")` *(optional)*
* `H` → print help to console
* `Q` / `Esc` → quit

Implement key handling in `core.py` (OpenCV window key capture or `keyboard` lib).

---

## Core Loop Responsibilities (`core.py`)

* Open camera (prefer 1280×720 @ 30 FPS).

* For each iteration:

  1. Grab frame + `timestamp_ns`.
  2. Call MediaPipe `detect_for_video(...)`.
  3. Build `FramePayload` (normalized coords + handedness + `Meta`).
  4. `DemoManager.on_frame(payload)`.
  5. Handle hotkeys; print minimal FPS every second.

* Safe idle: if `hands=[]`, demos should **not** move cursor/scroll.

---

## Minimal Config (inline or `configs/default.toml`)

```toml
[engine]
fps_target = 30
resolution = "1280x720"

[cursor_demo]
smoothing_window = 5
deadzone_norm = 0.01

[swipe_scroll_demo]
window_ms = 120
delta_x_threshold = 0.08
scroll_burst = 60    # lines per swipe

[esp32]
port = "COM5"        # or "/dev/ttyUSB0"
baud = 115200
```

---

## MVP Acceptance Criteria

* Runs at ~30 FPS with 720p webcam.
* `1/2/3` hotkeys switch demos instantly.
* Cursor demo tracks fingertip; click works via pinch/tap.
* Swipe demo reliably scrolls with left/right swipes.
* *(Optional)* ESP32 LED toggles on pinch start/end.
* README shows 2–3 GIFs + quick start commands.

---

## Upgrade Path (post-MVP)

* Swap `detect_for_video` → `detect_async` (LIVE_STREAM).
* Add overlay HUD + calibration wizard.
* Restore arbitration for multi-demo composition.
* Add kinematics and richer gesture events.

---

**End of MVP System Architecture.**
