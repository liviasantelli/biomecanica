"""
Gravacao das medidas por frame e exportacao para CSV.

Cada linha registrada corresponde a um frame processado, permitindo
reconstruir a trajetoria temporal do movimento mandibular e documentar a
evolucao entre sessoes.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

from .metrics import FrameMetrics, MovementState


@dataclass
class Sample:
    """Uma amostra temporal do movimento."""
    frame: int
    time_s: float
    opening_rel: float
    lateral_rel: float
    opening_mm: float | None
    lateral_mm: float | None
    state: MovementState
    repetitions: int


@dataclass
class SessionRecorder:
    """Acumula as amostras de uma sessao e as exporta."""
    samples: list[Sample] = field(default_factory=list)

    def add(self, sample: Sample) -> None:
        self.samples.append(sample)

    @property
    def is_empty(self) -> bool:
        return len(self.samples) == 0

    def clear(self) -> None:
        self.samples.clear()

    def to_csv(self, path: str) -> str:
        """Exporta as amostras para um arquivo CSV. Retorna o caminho."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "frame",
                    "tempo_s",
                    "abertura_rel",
                    "desvio_lateral_rel",
                    "abertura_mm",
                    "desvio_lateral_mm",
                    "estado",
                    "repeticoes",
                ]
            )
            for s in self.samples:
                writer.writerow(
                    [
                        s.frame,
                        f"{s.time_s:.4f}",
                        f"{s.opening_rel:.6f}",
                        f"{s.lateral_rel:.6f}",
                        "" if s.opening_mm is None else f"{s.opening_mm:.3f}",
                        "" if s.lateral_mm is None else f"{s.lateral_mm:.3f}",
                        s.state.value,
                        s.repetitions,
                    ]
                )
        return path
