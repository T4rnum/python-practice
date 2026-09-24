import logging
import math

import OpenGL.GL as gl  # type: ignore[import-untyped]
import OpenGL.GLU as glu  # type: ignore[import-untyped]
import pygame
from audio import AudioService
from config import ColorRGBA, Config, Vector3D, Vector4D
from graphics import CubeGeometryBuffer, TrailRenderer
from math_4d import PathGenerator4D, TesseractProjector


class Spiral4DApp:
    """Управляющий класс приложения."""

    def __init__(self, config: Config) -> None:
        self.cfg: Config = config
        self.audio: AudioService = AudioService()
        self.dim_size: int = self.cfg.matrix_size[0]

        self.projector: TesseractProjector = TesseractProjector(self.cfg.matrix_size)
        self.cube_gpu: CubeGeometryBuffer = CubeGeometryBuffer()
        self.font: pygame.font.Font | None = None

        self.path: list[Vector4D] = PathGenerator4D.generate_4d_spiral(
            *self.cfg.matrix_size
        )
        self.total_cells: int = len(self.path)

        self.filled_blocks: list[tuple[int, int, int, int, int]] = []
        self.step_index: int = 0
        self.time_accumulator: float = 0.0
        self.elapsed_time: float = 0.0

        self.is_running: bool = True
        self.is_done: bool = False
        self.paused: bool = False
        self.show_hud: bool = True
        self.is_fullscreen: bool = False

        self.rotate_x: float = 20.0
        self.rotate_y: float = 30.0
        self.mouse_down: bool = False
        self.last_mouse_pos: tuple[int, int] = (0, 0)
        self.target_fps: int = 60

        # Цветовые палитры и режимы динамической анимации цвета
        self.color_scheme_names: tuple[str, ...] = (
            "Гипер-Спектр",
            "Киберпанк",
            "Солнечная Вспышка",
            "Изумрудная Матрица",
            "Ледяной Океан",
        )
        self.color_scheme_idx: int = 0

        self.color_anim_mode_names: tuple[str, ...] = (
            "Статичный",
            "Волновой Перелив",
            "Дыхание Света",
            "Радужный Поток",
        )
        self.color_anim_mode_idx: int = 0

        # Режимы 4D вращения
        self.anim_mode_names: tuple[str, ...] = (
            "Плавный Ролл",
            "Гармоническая Осцилляция",
            "Двойной Гипер-Спин",
            "Статическая Изометрия",
        )
        self.anim_mode_idx: int = 0

    def _toggle_fullscreen(self) -> None:
        """Переключает между полноэкранным и оконным режимами."""
        self.is_fullscreen = not self.is_fullscreen
        flags: int = pygame.DOUBLEBUF | pygame.OPENGL

        if self.is_fullscreen:
            flags |= pygame.FULLSCREEN
            info = pygame.display.Info()
            screen_size = (info.current_w, info.current_h)
        else:
            screen_size = self.cfg.screen_size

        pygame.display.set_mode(screen_size, flags)

        # Перенастройка OpenGL Viewport и матрицы проекции
        gl.glViewport(0, 0, screen_size[0], screen_size[1])
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(
            45.0,
            (screen_size[0] / screen_size[1]),
            0.1,
            100.0,
        )
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(0.0, 0.0, -12.0)

        logging.info(
            "Режим экрана изменен: %s (%dx%d)",
            "Полноэкранный" if self.is_fullscreen else "Оконный",
            screen_size[0],
            screen_size[1],
        )

    def _rebuild_matrix(self) -> None:
        """Перестраивает размерность матрицы и путь спирали на лету."""
        self.cfg.matrix_size = (
            self.dim_size,
            self.dim_size,
            self.dim_size,
            self.dim_size,
        )
        self.projector.set_dimensions(self.cfg.matrix_size)
        self.path = PathGenerator4D.generate_4d_spiral(*self.cfg.matrix_size)
        self.total_cells = len(self.path)
        self.reset()
        logging.info("Размерность изменена: %dx%dx%dx%d", *self.cfg.matrix_size)

    def reset(self) -> None:
        self.filled_blocks.clear()
        self.step_index = 0
        self.time_accumulator = 0.0
        self.is_running = True
        self.is_done = False
        self.paused = False

    def update(self, dt: float) -> None:
        self.elapsed_time += dt

        if self.anim_mode_idx == 0:
            self.projector.angle_4d += 0.4 * dt
        elif self.anim_mode_idx == 1:
            self.projector.angle_4d = math.sin(self.elapsed_time * 1.5) * 1.2
        elif self.anim_mode_idx == 2:
            self.projector.angle_4d += 0.8 * dt
        elif self.anim_mode_idx == 3:
            self.projector.angle_4d = 0.785398

        if not self.is_running or self.paused or self.is_done:
            return

        self.time_accumulator += dt

        while self.time_accumulator >= self.cfg.step_delay:
            self.time_accumulator -= self.cfg.step_delay
            self._execute_step()
            if self.is_done:
                break

    def _execute_step(self) -> None:
        x, y, z, w = self.path[self.step_index]
        step: int = self.step_index + 1
        self.filled_blocks.append((x, y, z, w, step))

        self.audio.play_step_tone(step, self.total_cells)

        if step == self.total_cells:
            self.audio.play_completion_chime()
            self.is_done = True
            self.is_running = False
            return

        self.step_index += 1

    def _get_color_4d(self, w: int, step: int, alpha_factor: float = 1.0) -> ColorRGBA:
        total_w: int = max(1, self.cfg.matrix_size[3])
        w_norm: float = w / total_w
        step_norm: float = step / max(1, self.total_cells)

        r: float = 1.0
        g: float = 1.0
        b: float = 1.0

        # Базовая палитра
        if self.color_scheme_idx == 0:  # Гипер-Спектр
            hue: float = w_norm * 0.8
            r = abs(math.sin(hue * math.pi))
            g = abs(math.cos(hue * math.pi * 0.5))
            b = 1.0 - step_norm
        elif self.color_scheme_idx == 1:  # Киберпанк
            r = 0.9 - step_norm * 0.3
            g = w_norm * 0.8
            b = 1.0
        elif self.color_scheme_idx == 2:  # Солнечная Вспышка
            r = 1.0
            g = math.pow(w_norm, 1.5) * 0.8
            b = (1.0 - step_norm) * 0.2
        elif self.color_scheme_idx == 3:  # Изумрудная Матрица
            r = 0.1
            g = 0.5 + w_norm * 0.5
            b = step_norm * 0.4
        elif self.color_scheme_idx == 4:  # Ледяной Океан
            r = step_norm * 0.5
            g = 0.6 + w_norm * 0.4
            b = 1.0

        # Динамическая анимация цвета поверх палитры
        if self.color_anim_mode_idx == 1:  # Волновой Перелив
            shift = math.sin(self.elapsed_time * 2.0 + step * 0.1) * 0.2
            r = min(1.0, max(0.0, r + shift))
            g = min(1.0, max(0.0, g + math.cos(self.elapsed_time * 1.5) * 0.2))
            b = min(1.0, max(0.0, b - shift))
        elif self.color_anim_mode_idx == 2:  # Дыхание Света
            pulse = 0.75 + 0.25 * math.sin(self.elapsed_time * 3.0)
            r *= pulse
            g *= pulse
            b *= pulse
        elif self.color_anim_mode_idx == 3:  # Радужный Поток
            flow = (step_norm + self.elapsed_time * 0.2) % 1.0
            r = abs(math.sin(flow * math.pi))
            g = abs(math.sin((flow + 0.33) * math.pi))
            b = abs(math.sin((flow + 0.66) * math.pi))

        return (r, g, b, 0.85 * alpha_factor)

    def _render_hud(self) -> None:
        """Отрисовывает 2D-панель управления поверх 3D-сцены."""
        if not self.show_hud or self.font is None:
            return

        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        screen_w, screen_h = viewport[2], viewport[3]

        dim_str: str = (
            f"{self.dim_size}x{self.dim_size}x{self.dim_size}x{self.dim_size}"
        )
        palette_str: str = self.color_scheme_names[self.color_scheme_idx]
        color_anim_str: str = self.color_anim_mode_names[self.color_anim_mode_idx]
        anim_str: str = self.anim_mode_names[self.anim_mode_idx]
        sound_str: str = self.audio.get_profile_name()
        screen_mode_str: str = "FULL" if self.is_fullscreen else "WINDOW"

        lines: list[str] = [
            f"Управление [{screen_mode_str}]:",
            " [F11 / F] — Полноэкранный режим",
            " [H]       — Скрыть / Показать интерфейс",
            " [Q / E]   — 4D Анимация: " + anim_str,
            " [◄ / ►]   — Размер: " + dim_str,
            " [C]       — Палитра: " + palette_str,
            " [V]       — Анимация цвета: " + color_anim_str,
            " [B]       — Звук: " + sound_str,
            " [Пробел] — Пауза",
            " [R]       — Сброс",
            " [▲ / ▼]   — Скорость шага",
            " [ЛКМ / Скролл] — Вращение / Зум",
        ]

        padding: int = 12
        line_height: int = 20
        panel_w: int = 400
        panel_h: int = len(lines) * line_height + padding * 2

        hud_surface: pygame.Surface = pygame.Surface(
            (panel_w, panel_h), pygame.SRCALPHA
        )
        hud_surface.fill((10, 14, 28, 195))

        for idx, line in enumerate(lines):
            color = (255, 215, 0) if idx == 0 else (220, 225, 240)
            txt_surf = self.font.render(line, True, color)
            hud_surface.blit(txt_surf, (padding, padding + idx * line_height))

        texture_data: bytes = pygame.image.tobytes(hud_surface, "RGBA", True)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        glu.gluOrtho2D(0, screen_w, screen_h, 0)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        tex_id: int = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            panel_w,
            panel_h,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            texture_data,
        )

        gl.glEnable(gl.GL_TEXTURE_2D)
        x: float = 15.0
        y: float = 15.0

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0.0, 1.0)
        gl.glVertex2f(x, y)
        gl.glTexCoord2f(1.0, 1.0)
        gl.glVertex2f(x + panel_w, y)
        gl.glTexCoord2f(1.0, 0.0)
        gl.glVertex2f(x + panel_w, y + panel_h)
        gl.glTexCoord2f(0.0, 0.0)
        gl.glVertex2f(x, y + panel_h)
        gl.glEnd()

        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDeleteTextures([tex_id])
        gl.glEnable(gl.GL_DEPTH_TEST)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

    def render(self) -> None:
        gl.glClear(int(gl.GL_COLOR_BUFFER_BIT) | int(gl.GL_DEPTH_BUFFER_BIT))
        gl.glClearColor(0.04, 0.04, 0.07, 1.0)

        gl.glPushMatrix()
        gl.glRotatef(self.rotate_x, 1, 0, 0)
        gl.glRotatef(self.rotate_y, 0, 1, 0)

        num_blocks: int = len(self.filled_blocks)
        spawn_progress: float = (
            min(1.0, self.time_accumulator / self.cfg.step_delay)
            if not self.is_done
            else 1.0
        )

        trail_points: list[tuple[Vector3D, ColorRGBA]] = []

        for i, (x, y, z, w, step) in enumerate(self.filled_blocks):
            pos_3d, scale_4d = self.projector.project(x, y, z, w)
            color = self._get_color_4d(w, step)

            if i >= max(0, num_blocks - self.cfg.trail_length):
                trail_points.append((pos_3d, color))

            if i == num_blocks - 1 and not self.is_done:
                smooth_t: float = (
                    spawn_progress * spawn_progress * (3 - 2 * spawn_progress)
                )
                block_scale: float = scale_4d * 0.8 * smooth_t
                color = self._get_color_4d(w, step, alpha_factor=smooth_t)
            else:
                block_scale = scale_4d * 0.8

            gl.glPushMatrix()
            gl.glTranslatef(*pos_3d)
            gl.glScalef(block_scale, block_scale, block_scale)

            gl.glColor4fv(color)
            self.cube_gpu.draw()

            gl.glPopMatrix()

        TrailRenderer.render(trail_points)

        gl.glPopMatrix()

        self._render_hud()

        pygame.display.flip()

    def _detect_refresh_rate(self) -> int:
        try:
            hz: int = pygame.display.get_current_refresh_rate()
            if hz > 0:
                logging.info("Частота обновления монитора: %d Гц", hz)
                return hz
        except Exception:
            pass

        return 60

    def run(self) -> None:
        pygame.init()
        pygame.font.init()

        flags: int = pygame.DOUBLEBUF | pygame.OPENGL
        try:
            pygame.display.set_mode(self.cfg.screen_size, flags, vsync=1)
        except pygame.error:
            pygame.display.set_mode(self.cfg.screen_size, flags)

        pygame.display.set_caption("4D Hyper-Spiral Visualizer")
        clock: pygame.time.Clock = pygame.time.Clock()

        try:
            self.font = pygame.font.SysFont("Consolas", 14)
        except Exception:
            self.font = pygame.font.Font(None, 16)

        self.target_fps = self._detect_refresh_rate()

        gl.glEnable(gl.GL_DEPTH_TEST)
        glu.gluPerspective(
            45.0,
            (self.cfg.screen_size[0] / self.cfg.screen_size[1]),
            0.1,
            100.0,
        )
        gl.glTranslatef(0.0, 0.0, -12.0)

        fps_timer: float = 0.0

        while True:
            dt: float = min(clock.tick(self.target_fps) / 1000.0, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_F11, pygame.K_f):
                        self._toggle_fullscreen()
                    elif event.key == pygame.K_h:
                        self.show_hud = not self.show_hud
                    elif event.key == pygame.K_c:
                        self.color_scheme_idx = (self.color_scheme_idx + 1) % len(
                            self.color_scheme_names
                        )
                    elif event.key == pygame.K_v:
                        self.color_anim_mode_idx = (self.color_anim_mode_idx + 1) % len(
                            self.color_anim_mode_names
                        )
                    elif event.key == pygame.K_b:
                        self.audio.next_profile()
                    elif event.key == pygame.K_q:
                        self.anim_mode_idx = (self.anim_mode_idx - 1) % len(
                            self.anim_mode_names
                        )
                    elif event.key == pygame.K_e:
                        self.anim_mode_idx = (self.anim_mode_idx + 1) % len(
                            self.anim_mode_names
                        )
                    elif event.key == pygame.K_LEFT:
                        if self.dim_size > 2:
                            self.dim_size -= 1
                            self._rebuild_matrix()
                    elif event.key == pygame.K_RIGHT:
                        if self.dim_size < 6:
                            self.dim_size += 1
                            self._rebuild_matrix()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        self.cfg.step_delay = max(0.02, self.cfg.step_delay - 0.04)
                    elif event.key == pygame.K_DOWN:
                        self.cfg.step_delay += 0.04
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_down = True
                        self.last_mouse_pos = (event.pos[0], event.pos[1])
                    elif event.button == 4:
                        gl.glTranslatef(0.0, 0.0, 1.0)
                    elif event.button == 5:
                        gl.glTranslatef(0.0, 0.0, -1.0)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_down = False
                elif event.type == pygame.MOUSEMOTION and self.mouse_down:
                    dx: float = float(event.pos[0] - self.last_mouse_pos[0])
                    dy: float = float(event.pos[1] - self.last_mouse_pos[1])
                    self.rotate_y += dx * 0.4
                    self.rotate_x += dy * 0.4
                    self.last_mouse_pos = (event.pos[0], event.pos[1])

            self.update(dt)
            self.render()

            fps_timer += dt
            if fps_timer >= 0.2:
                pygame.display.set_caption(
                    f"4D Visualizer | FPS: {clock.get_fps():.0f}/{self.target_fps}Hz | "
                    f"Размер: {self.dim_size}^4"
                )
                fps_timer = 0.0
