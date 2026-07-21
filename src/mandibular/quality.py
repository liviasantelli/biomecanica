"""
Controle de qualidade do frame.

Classifica cada frame em nao detectado / invalido / valido, e produz uma
orientacao curta para o usuario corrigir o posicionamento. Isso evita que
ruido de deteccao (rosto pequeno demais, cabeca inclinada, movimento brusco)
contamine as metricas e a contagem de ciclos.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .config import Landmark, QualityConfig
from .landmarks import FaceLandmarks


class FrameQuality(str, Enum):
    NAO_DETECTADA = "face_nao_detectada"
    INVALIDA = "invalida"
    VALIDA = "valida"


@dataclass
class QualityResult:
    quality: FrameQuality
    message: str | None  # orientacao para o usuario; None quando o frame e valido


def assess_quality(
    face: FaceLandmarks | None,
    prev_nasion: np.ndarray | None,
    config: QualityConfig | None = None,
) -> QualityResult:
    """Avalia a qualidade do frame atual a partir dos landmarks detectados."""
    config = config or QualityConfig()

    if face is None:
        return QualityResult(FrameQuality.NAO_DETECTADA, "Face nao detectada")

    h, w = face.image_height, face.image_width
    eye_l = face.point(Landmark.EYE_OUTER_LEFT)
    eye_r = face.point(Landmark.EYE_OUTER_RIGHT)
    nasion = face.point(Landmark.NASION)
    chin = face.point(Landmark.CHIN)

    pts = np.array([eye_l, eye_r, nasion, chin])
    if (
        np.any(pts[:, 0] < 0)
        or np.any(pts[:, 0] > w)
        or np.any(pts[:, 1] < 0)
        or np.any(pts[:, 1] > h)
    ):
        return QualityResult(FrameQuality.INVALIDA, "Centralize o rosto")

    face_width = float(np.linalg.norm(eye_r - eye_l))
    img_diag = float(np.hypot(w, h))
    if img_diag < 1e-6:
        img_diag = 1.0

    if face_width < config.min_face_width_fraction * img_diag:
        return QualityResult(FrameQuality.INVALIDA, "Aproxime-se da camera")
    if face_width > config.max_face_width_fraction * img_diag:
        return QualityResult(FrameQuality.INVALIDA, "Afaste-se da camera")

    dx, dy = eye_r - eye_l
    roll_deg = float(np.degrees(np.arctan2(dy, dx)))
    if abs(roll_deg) > config.max_roll_deg:
        return QualityResult(FrameQuality.INVALIDA, "Mantenha a cabeca estavel (nao incline)")

    if prev_nasion is not None:
        jump = float(np.linalg.norm(nasion - prev_nasion)) / max(face_width, 1e-6)
        if jump > config.max_global_jump_fraction:
            return QualityResult(FrameQuality.INVALIDA, "Mantenha a cabeca estavel")

    return QualityResult(FrameQuality.VALIDA, None)
