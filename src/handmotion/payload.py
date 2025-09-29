from dataclasses import dataclass
from typing import List, Literal

Handedness = Literal["L", "R"]

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
