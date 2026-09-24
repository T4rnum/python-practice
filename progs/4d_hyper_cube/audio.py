import logging
import math
import struct
from typing import Final

import pygame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class AudioService:
    """Процедурный синтезатор звуков с поддержкой профилей."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate: Final[int] = sample_rate
        self.enabled: bool = True

        self.profile_names: tuple[str, ...] = (
            "Эмбиент Чайм",
            "Кибер-Пила (Synth)",
            "8-Bit Пульс",
            "Мягкий Орган",
        )
        self.profile_idx: int = 0

        try:
            pygame.mixer.init(
                frequency=self.sample_rate, size=-16, channels=1, buffer=512
            )
        except pygame.error as err:
            logging.warning("Ошибка инициализации звука: %s. Без звука.", err)
            self.enabled = False

    def next_profile(self) -> str:
        self.profile_idx = (self.profile_idx + 1) % len(self.profile_names)
        return self.get_profile_name()

    def get_profile_name(self) -> str:
        return self.profile_names[self.profile_idx]

    def play_step_tone(self, step: int, total_steps: int) -> None:
        if not self.enabled:
            return

        progress: float = step / max(1, total_steps)
        base_freq: float = 261.63  # Нота C4

        pentatonic_scale: tuple[float, ...] = (1.0, 1.125, 1.25, 1.5, 1.6875)
        scale_idx: int = int(progress * 15)
        octave: int = scale_idx // 5
        degree: int = scale_idx % 5

        freq: float = base_freq * pentatonic_scale[degree] * (2.0**octave)

        sound: pygame.mixer.Sound = self._synthesize_soft_chime(
            frequency=freq, duration=0.18, volume=0.12
        )
        sound.play()

    def play_completion_chime(self) -> None:
        if not self.enabled:
            return

        chord_freqs: tuple[float, ...] = (261.63, 329.63, 392.00, 523.25)
        for freq in chord_freqs:
            sound: pygame.mixer.Sound = self._synthesize_soft_chime(
                frequency=freq, duration=0.6, volume=0.10
            )
            sound.play()

    def _synthesize_soft_chime(
        self,
        frequency: float,
        duration: float,
        volume: float,
    ) -> pygame.mixer.Sound:
        n_samples: int = int(self.sample_rate * duration)
        buf: bytearray = bytearray()

        for i in range(n_samples):
            t: float = float(i) / self.sample_rate
            attack_time: float = 0.012

            if t < attack_time:
                envelope: float = math.sin((math.pi / 2.0) * (t / attack_time))
            else:
                decay: float = (t - attack_time) / (duration - attack_time)
                envelope = math.exp(-3.5 * decay)

            # Генерация волны в зависимости от выбранного профиля
            if self.profile_idx == 0:  # Эмбиент Чайм
                sample_wave = 0.80 * math.sin(
                    2.0 * math.pi * frequency * t
                ) + 0.20 * math.sin(4.0 * math.pi * frequency * t)
            elif self.profile_idx == 1:  # Кибер-Пила (Synth)
                raw_saw = 2.0 * (frequency * t - math.floor(0.5 + frequency * t))
                sample_wave = raw_saw * 0.75
            elif self.profile_idx == 2:  # 8-Bit Пульс (Square)
                sample_wave = (
                    0.6 if math.sin(2.0 * math.pi * frequency * t) >= 0 else -0.6
                )
            elif self.profile_idx == 3:  # Мягкий Орган
                sample_wave = (
                    0.50 * math.sin(2.0 * math.pi * frequency * t)
                    + 0.30 * math.sin(2.0 * math.pi * (frequency * 2) * t)
                    + 0.20 * math.sin(2.0 * math.pi * (frequency * 3) * t)
                )
            else:
                sample_wave = math.sin(2.0 * math.pi * frequency * t)

            sample_val: int = int(32767.0 * volume * envelope * sample_wave)
            sample_val = max(-32768, min(32767, sample_val))
            buf.extend(struct.pack("<h", sample_val))

        return pygame.mixer.Sound(buffer=bytes(buf))
