from dataclasses import dataclass

Vector4D = tuple[int, int, int, int]
Vector3D = tuple[float, float, float]
ColorRGBA = tuple[float, float, float, float]


@dataclass
class Config:
    matrix_size: Vector4D = (3, 3, 3, 3)
    step_delay: float = 0.22
    trail_length: int = 12
    screen_size: tuple[int, int] = (1024, 768)