import OpenGL.GL as gl  # type: ignore[import-untyped]
from config import ColorRGBA, Vector3D


class TrailRenderer:
    """Отрисовывает светящийся энергетический шлейф траектории в 3D."""

    @staticmethod
    def render(trail_points: list[tuple[Vector3D, ColorRGBA]]) -> None:
        if len(trail_points) < 2:
            return

        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_LIGHTING)

        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        gl.glLineWidth(5.0)

        gl.glBegin(gl.GL_LINE_STRIP)
        total_pts: float = float(len(trail_points))
        for i, (pos, color) in enumerate(trail_points):
            alpha: float = (i + 1) / total_pts
            gl.glColor4f(color[0], color[1], color[2], alpha * 0.7)
            gl.glVertex3fv(pos)
        gl.glEnd()

        gl.glLineWidth(1.8)
        gl.glBegin(gl.GL_LINE_STRIP)
        for i, (pos, _) in enumerate(trail_points):
            alpha = (i + 1) / total_pts
            gl.glColor4f(1.0, 1.0, 1.0, alpha * 0.9)
            gl.glVertex3fv(pos)
        gl.glEnd()

        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


class CubeGeometryBuffer:
    """Запекает базовую геометрию вокселя в память GPU."""

    def __init__(self) -> None:
        self._list_id: int | None = None

    def compile(self) -> None:
        vertices: tuple[tuple[float, float, float], ...] = (
            (0.5, -0.5, -0.5),
            (0.5, 0.5, -0.5),
            (-0.5, 0.5, -0.5),
            (-0.5, -0.5, -0.5),
            (0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5),
            (-0.5, -0.5, 0.5),
            (-0.5, 0.5, 0.5),
        )
        surfaces: tuple[tuple[int, int, int, int], ...] = (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6),
        )
        edges: tuple[tuple[int, int], ...] = (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 7),
            (7, 6),
            (6, 4),
            (0, 4),
            (1, 5),
            (2, 7),
            (3, 6),
        )

        self._list_id = gl.glGenLists(1)
        gl.glNewList(self._list_id, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)
        for surface in surfaces:
            for vertex_idx in surface:
                gl.glVertex3fv(vertices[vertex_idx])
        gl.glEnd()

        gl.glColor3f(0.0, 0.0, 0.0)
        gl.glLineWidth(1.0)
        gl.glBegin(gl.GL_LINES)
        for edge in edges:
            for vertex_idx in edge:
                gl.glVertex3fv(vertices[vertex_idx])
        gl.glEnd()

        gl.glEndList()

    def draw(self) -> None:
        if self._list_id is None:
            self.compile()
        if self._list_id is not None:
            gl.glCallList(self._list_id)
