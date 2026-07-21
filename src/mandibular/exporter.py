"""
Exportacao da sessao: cria uma pasta propria com CSV, resumo, metadados,
graficos e (opcionalmente) o video anotado.

Usa um identificador anonimo por padrao (sessao_AAAA-MM-DD_HH-MM-SS), sem
nome de paciente.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

import numpy as np

from .metrics import CycleDetector
from .plotting import plot_lateral_time, plot_opening_time, plot_trajectory
from .recorder import SessionRecorder

DISCLAIMER = (
    "Ferramenta de apoio funcional/didatico; nao substitui avaliacao "
    "profissional e nao constitui diagnostico de DTM."
)


def make_session_id(now: datetime | None = None) -> str:
    now = now or datetime.now()
    return "sessao_" + now.strftime("%Y-%m-%d_%H-%M-%S")


def export_session(
    recorder: SessionRecorder,
    cycles: CycleDetector,
    session_dir: str,
    session_id: str,
    ref_mm: float | None = None,
    video_path: str | None = None,
    extra_metadata: dict | None = None,
) -> dict[str, str]:
    """Exporta a sessao na pasta `session_dir`; retorna os caminhos gerados."""
    if recorder.is_empty:
        raise ValueError("Nao ha amostras para exportar.")

    os.makedirs(session_dir, exist_ok=True)
    paths: dict[str, str] = {}

    csv_path = os.path.join(session_dir, "dados.csv")
    recorder.to_csv(csv_path)
    paths["csv"] = csv_path

    use_mm = ref_mm is not None
    paths["abertura_png"] = plot_opening_time(
        recorder, os.path.join(session_dir, "abertura_tempo.png"), use_mm=use_mm
    )
    paths["lateral_png"] = plot_lateral_time(
        recorder, os.path.join(session_dir, "lateralidade_tempo.png"), use_mm=use_mm
    )
    paths["trajetoria_png"] = plot_trajectory(
        recorder,
        os.path.join(session_dir, "trajetoria_abertura_lateralidade.png"),
        use_mm=use_mm,
    )

    opening = np.array([s.opening_filtered for s in recorder.samples])
    lateral = np.array([s.lateral_filtered for s in recorder.samples])
    rep = cycles.repeatability()

    resumo = {
        "session_id": session_id,
        "n_amostras": len(recorder.samples),
        "repeticoes": cycles.repetitions,
        "abertura_minima": float(opening.min()),
        "abertura_maxima": float(opening.max()),
        "desvio_lateral_maximo_abs": float(np.abs(lateral).max()),
        "desvio_lateral_medio_abs": float(np.abs(lateral).mean()),
        "repetibilidade": rep,
        "aviso": DISCLAIMER,
    }
    resumo_path = os.path.join(session_dir, "resumo.json")
    with open(resumo_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)
    paths["resumo"] = resumo_path

    metadados = {
        "session_id": session_id,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "ref_mm": ref_mm,
        "calibrado": cycles.is_calibrated,
    }
    if extra_metadata:
        metadados.update(extra_metadata)
    metadados_path = os.path.join(session_dir, "metadados.json")
    with open(metadados_path, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)
    paths["metadados"] = metadados_path

    if video_path and os.path.exists(video_path):
        paths["video"] = video_path

    return paths
