"""
Testes da logica biomecanica com landmarks sinteticos (sem webcam).

Constroi uma face artificial com posicoes conhecidas para verificar:
    - calculo da abertura e do desvio lateral normalizados;
    - invariancia a distancia da camera e a inclinacao (roll) da cabeca;
    - deteccao de ciclos com histerese, filtragem de ruido e repetibilidade;
    - gravacao/exportacao em CSV;
    - o assistente de calibracao.
"""

import csv
import math
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mandibular.app import CalibrationAssistant
from mandibular.config import CycleConfig, Landmark
from mandibular.landmarks import FaceLandmarks
from mandibular.metrics import CycleDetector, MovementState, compute_frame_metrics
from mandibular.recorder import Sample, SessionRecorder

N_LANDMARKS = 478  # modelo Face Landmarker


def make_face(
    opening_px: float,
    lateral_px: float = 0.0,
    scale: float = 1.0,
    roll_deg: float = 0.0,
    center: tuple[float, float] = (300.0, 300.0),
) -> FaceLandmarks:
    """
    Cria landmarks sinteticos com abertura e desvio lateral controlados.

    `scale` simula aproximar/afastar da camera; `roll_deg` inclina a cabeca no
    plano da imagem (rotacao em torno de `center`).
    """
    pts = np.zeros((N_LANDMARKS, 2), dtype=np.float32)
    pts[Landmark.EYE_OUTER_LEFT] = (200.0, 200.0)
    pts[Landmark.EYE_OUTER_RIGHT] = (400.0, 200.0)
    pts[Landmark.NASION] = (300.0, 210.0)
    pts[Landmark.CHIN] = (300.0 + lateral_px, 450.0)
    pts[Landmark.UPPER_LIP_INNER] = (300.0, 350.0)
    pts[Landmark.LOWER_LIP_INNER] = (300.0, 350.0 + opening_px)
    pts[Landmark.NOSE_TIP] = (300.0, 300.0)
    pts[Landmark.MOUTH_LEFT] = (270.0, 350.0)
    pts[Landmark.MOUTH_RIGHT] = (330.0, 350.0)

    c = np.array(center, dtype=np.float32)
    # Escala em torno do centro.
    pts = (pts - c) * scale + c
    # Rotacao (roll) em torno do centro.
    if roll_deg:
        a = math.radians(roll_deg)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]],
                       dtype=np.float32)
        pts = (pts - c) @ rot.T + c
    return FaceLandmarks(points=pts, image_width=600, image_height=600)


# --------------------------------------------------------------------------
# Metricas por frame
# --------------------------------------------------------------------------
def test_opening_normalized():
    m = compute_frame_metrics(make_face(opening_px=100.0))
    assert abs(m.opening_rel - 0.5) < 1e-6, m.opening_rel
    assert abs(m.face_width_px - 200.0) < 1e-6


def test_lateral_sign_positive():
    m = compute_frame_metrics(make_face(0.0, lateral_px=40.0))
    assert abs(m.lateral_rel - 0.2) < 1e-6, m.lateral_rel


def test_lateral_sign_negative():
    m = compute_frame_metrics(make_face(0.0, lateral_px=-40.0))
    assert abs(m.lateral_rel + 0.2) < 1e-6, m.lateral_rel


def test_scale_invariance():
    """Aproximar/afastar da camera nao deve mudar as medidas relativas."""
    a = compute_frame_metrics(make_face(100.0, lateral_px=40.0, scale=1.0))
    b = compute_frame_metrics(make_face(100.0, lateral_px=40.0, scale=1.8))
    assert abs(a.opening_rel - b.opening_rel) < 1e-4, (a.opening_rel, b.opening_rel)
    assert abs(a.lateral_rel - b.lateral_rel) < 1e-4, (a.lateral_rel, b.lateral_rel)


def test_roll_invariance():
    """Inclinar a cabeca no plano (roll) nao deve mudar as medidas relativas."""
    a = compute_frame_metrics(make_face(100.0, lateral_px=40.0, roll_deg=0.0))
    b = compute_frame_metrics(make_face(100.0, lateral_px=40.0, roll_deg=20.0))
    assert abs(a.opening_rel - b.opening_rel) < 1e-3, (a.opening_rel, b.opening_rel)
    assert abs(a.lateral_rel - b.lateral_rel) < 1e-3, (a.lateral_rel, b.lateral_rel)


def test_mm_calibration():
    m = compute_frame_metrics(make_face(100.0), reference_distance_mm=60.0)
    assert abs(m.opening_mm - 30.0) < 1e-6, m.opening_mm


# --------------------------------------------------------------------------
# Deteccao de ciclos
# --------------------------------------------------------------------------
def _run_signal(det: CycleDetector, values, fps=30, hold=5):
    dt = 1.0 / fps
    t = 0.0
    for v in values:
        for _ in range(hold):
            det.update(v, t)
            t += dt
    return t


def test_cycle_detection_count():
    det = CycleDetector(CycleConfig(min_cycle_seconds=0.05))
    det.calibrate(0.0, 0.5)
    for _ in range(5):
        _run_signal(det, [0.0, 0.5, 0.0])
    assert det.repetitions == 5, det.repetitions
    rep = det.repeatability()
    assert rep["amplitude_cv"] < 1e-3, rep
    assert rep["n_ciclos"] == 5


def test_hysteresis_ignores_small_noise():
    """Ruido dentro da banda de histerese nao deve contar repeticoes."""
    det = CycleDetector(CycleConfig())  # open=0.60, close=0.25 da faixa
    det.calibrate(0.0, 1.0)
    # Oscila entre 0.30 e 0.45: acima do close_th mas abaixo do open_th (0.60).
    for _ in range(10):
        _run_signal(det, [0.30, 0.45])
    assert det.repetitions == 0, det.repetitions


def test_min_cycle_seconds_filters_fast_flicker():
    """Ciclos mais rapidos que min_cycle_seconds sao descartados."""
    det = CycleDetector(CycleConfig(min_cycle_seconds=0.30))
    det.calibrate(0.0, 0.5)
    # Cada abre/fecha dura ~0.10 s (2 amostras a 30 fps) < 0.30 s -> ignorado.
    for _ in range(6):
        _run_signal(det, [0.0, 0.5, 0.0], hold=1)
    assert det.repetitions == 0, det.repetitions


def test_state_machine_transitions():
    det = CycleDetector(CycleConfig(min_cycle_seconds=0.0))
    det.calibrate(0.0, 1.0)
    det.update(0.0, 0.0)
    assert det.state == MovementState.FECHADO
    det.update(0.9, 0.1)   # cruza o limiar: inicia a abertura
    assert det.state == MovementState.ABRINDO
    det.update(0.9, 0.2)   # mantem aberto
    assert det.state == MovementState.ABERTO
    det.update(0.1, 0.3)   # fecha: conclui o ciclo
    assert det.state == MovementState.FECHANDO
    assert det.repetitions == 1


# --------------------------------------------------------------------------
# Gravacao / CSV
# --------------------------------------------------------------------------
def test_recorder_csv_roundtrip():
    rec = SessionRecorder()
    for i in range(3):
        rec.add(Sample(i, i * 0.1, 0.2 + i * 0.01, -0.05, None, None,
                       MovementState.FECHADO, 0))
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s.csv")
        rec.to_csv(path)
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
    assert rows[0][0] == "frame" and rows[0][2] == "abertura_rel"
    assert len(rows) == 4  # cabecalho + 3 amostras
    assert rows[1][6] == "fechado"


# --------------------------------------------------------------------------
# Assistente de calibracao
# --------------------------------------------------------------------------
def test_calibration_assistant():
    ca = CalibrationAssistant()
    ca.start()
    t = 0.0
    result = None
    # Alimenta o valor conforme a fase atual do assistente (0=fechado, 1=aberto).
    # O proprio assistente avanca a fase quando o tempo de espera se esgota.
    while ca.active and result is None:
        v = 0.05 if ca.phase == 0 else 0.55
        result = ca.update(v, t)
        t += 1.0 / 40
    closed, opened = result
    assert abs(closed - 0.05) < 1e-2, closed
    assert abs(opened - 0.55) < 1e-2, opened
    assert not ca.active


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"OK  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FALHOU  {fn.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} testes passaram.")
    sys.exit(1 if failed else 0)
