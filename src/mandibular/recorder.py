"""
Gravacao das medidas por frame e exportacao para CSV.

Cada linha registrada corresponde a um frame processado (com face valida ou
nao), permitindo reconstruir a trajetoria temporal do movimento mandibular,
auditar a qualidade da coleta e comparar sessoes.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

from .metrics import MovementState

CSV_COLUMNS = [
    "session_id",
    "frame",
    "timestamp",
    "tempo_s",
    "face_detectada",
    "frame_valido",
    "abertura_bruta",
    "abertura_relativa",
    "abertura_filtrada",
    "abertura_mm",
    "desvio_lateral_bruto",
    "desvio_lateral_relativo",
    "desvio_lateral_filtrado",
    "desvio_lateral_mm",
    "direcao",
    "estado_ciclo",
    "repeticoes",
    "aviso_qualidade",
]


@dataclass
class Sample:
    """Uma amostra temporal do movimento (item 12 do escopo funcional)."""
    session_id: str
    frame: int
    timestamp: str
    time_s: float
    face_detected: bool
    frame_valid: bool
    opening_raw: float
    opening_rel: float
    opening_filtered: float
    opening_mm: float | None
    lateral_raw: float
    lateral_rel: float
    lateral_filtered: float
    lateral_mm: float | None
    direction: str
    cycle_state: MovementState
    repetitions: int
    quality_warning: str | None

    def to_row(self) -> list:
        return [
            self.session_id,
            self.frame,
            self.timestamp,
            f"{self.time_s:.4f}",
            int(self.face_detected),
            int(self.frame_valid),
            f"{self.opening_raw:.4f}",
            f"{self.opening_rel:.6f}",
            f"{self.opening_filtered:.6f}",
            "" if self.opening_mm is None else f"{self.opening_mm:.3f}",
            f"{self.lateral_raw:.4f}",
            f"{self.lateral_rel:.6f}",
            f"{self.lateral_filtered:.6f}",
            "" if self.lateral_mm is None else f"{self.lateral_mm:.3f}",
            self.direction,
            self.cycle_state.value,
            self.repetitions,
            self.quality_warning or "",
        ]


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
            writer.writerow(CSV_COLUMNS)
            for s in self.samples:
                writer.writerow(s.to_row())
        return path
