from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal

Handedness = Literal["L", "R"]

@dataclass
class Landmark:
    x_norm: float  # [0,1]
    y_norm: float  # [0,1]
    z_norm: float  # MediaPipe relative depth (optional use)

    def __post_init__(self) -> None:
        assert 0.0 <= self.x_norm <= 1.0, f"x_norm must be in [0,1]. Got {self.x_norm} instead."
        assert 0.0 <= self.y_norm <= 1.0, f"y_norm must be in [0,1]. Got {self.y_norm} instead."

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x_norm, self.y_norm, self.z_norm)

@dataclass
class Hand:
    handedness: Handedness
    confidence: float
    landmarks: List[Landmark]  # len == 21

    def __post_init__(self) -> None:
        assert len(self.landmarks) == 21, f"Hand must have exactly 21 landmarks. Got {len(self.landmarks)} instead."
        assert 0.0 <= self.confidence <= 1.0, f"Confidence must be in [0,1]. Got {self.confidence} instead."

@dataclass
class Meta:
    timestamp_ns: int
    width: int
    height: int
    fps_estimate: float

    def __post_init__(self) -> None:
        assert self.width > 0, f"Width must be positive. Got {self.width} instead."
        assert self.height > 0, f"Height must be positive. Got {self.height} instead."
        assert self.fps_estimate > 0, f"FPS estimate must be positive. Got {self.fps_estimate} instead."

@dataclass
class FramePayload:
    meta: Meta
    hands: List[Hand]
