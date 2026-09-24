import math

from config import Vector3D, Vector4D


class PathGenerator4D:
    """Вычисляет непрерывные спиральные пути в N-мерных гиперматрицах."""

    @staticmethod
    def _generate_2d_spiral(nx: int, ny: int) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        visited: set[tuple[int, int]] = set()
        x: int = 0
        y: int = 0
        dx: int = 1
        dy: int = 0
        total: int = nx * ny

        for _ in range(total):
            path.append((x, y))
            visited.add((x, y))
            if len(path) == total:
                break
            nx_x: int = x + dx
            nx_y: int = y + dy
            if not (0 <= nx_x < nx and 0 <= nx_y < ny) or (nx_x, nx_y) in visited:
                dx, dy = -dy, dx
                nx_x, nx_y = x + dx, y + dy
            x, y = nx_x, nx_y
        return path

    @classmethod
    def _generate_3d_spiral(
        cls, nx: int, ny: int, nz: int
    ) -> list[tuple[int, int, int]]:
        fwd_2d: list[tuple[int, int]] = cls._generate_2d_spiral(nx, ny)
        rev_2d: list[tuple[int, int]] = list(reversed(fwd_2d))
        path_3d: list[tuple[int, int, int]] = []

        for z in range(nz):
            sub_path = fwd_2d if z % 2 == 0 else rev_2d
            for px, py in sub_path:
                path_3d.append((px, py, z))
        return path_3d

    @classmethod
    def generate_4d_spiral(cls, nx: int, ny: int, nz: int, nw: int) -> list[Vector4D]:
        fwd_3d: list[tuple[int, int, int]] = cls._generate_3d_spiral(nx, ny, nz)
        rev_3d: list[tuple[int, int, int]] = list(reversed(fwd_3d))
        path_4d: list[Vector4D] = []

        for w in range(nw):
            sub_path = fwd_3d if w % 2 == 0 else rev_3d
            for x, y, z in sub_path:
                path_4d.append((x, y, z, w))
        return path_4d


class TesseractProjector:
    """Проецирует 4D-точки в 3D с вращением в гиперплоскости XW."""

    def __init__(self, dimensions: Vector4D, distance_4d: float = 4.0) -> None:
        self.nx: int = dimensions[0]
        self.ny: int = dimensions[1]
        self.nz: int = dimensions[2]
        self.nw: int = dimensions[3]
        self.distance_4d: float = distance_4d
        self.angle_4d: float = 0.0

    def set_dimensions(self, dimensions: Vector4D) -> None:
        self.nx, self.ny, self.nz, self.nw = dimensions

    def project(self, x: float, y: float, z: float, w: float) -> tuple[Vector3D, float]:
        cx: float = x - (self.nx - 1) / 2.0
        cy: float = y - (self.ny - 1) / 2.0
        cz: float = z - (self.nz - 1) / 2.0
        cw: float = w - (self.nw - 1) / 2.0

        cos_a: float = math.cos(self.angle_4d)
        sin_a: float = math.sin(self.angle_4d)

        rx: float = cx * cos_a - cw * sin_a
        rw: float = cx * sin_a + cw * cos_a
        ry: float = cy
        rz: float = cz

        scale_4d: float = self.distance_4d / (self.distance_4d - rw * 0.4)
        return (rx * scale_4d, ry * scale_4d, rz * scale_4d), scale_4d
