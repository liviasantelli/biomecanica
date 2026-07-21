"""
Geracao de graficos da evolucao temporal do movimento mandibular.

Usa matplotlib com backend nao interativo ("Agg") para salvar imagens sem
depender de uma janela grafica. Os graficos usam os valores filtrados (EMA),
que sao os mesmos usados para a deteccao de ciclos e o biofeedback.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .recorder import SessionRecorder  # noqa: E402


def _series(recorder: SessionRecorder, use_mm: bool) -> tuple[list, list, list, str]:
    t = [s.time_s for s in recorder.samples]
    if use_mm and recorder.samples[0].opening_mm is not None:
        opening = [s.opening_mm for s in recorder.samples]
        lateral = [s.lateral_mm for s in recorder.samples]
        unit = "mm"
    else:
        opening = [s.opening_filtered for s in recorder.samples]
        lateral = [s.lateral_filtered for s in recorder.samples]
        unit = "rel. (larg. facial)"
    return t, opening, lateral, unit


def _ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


def plot_opening_time(recorder: SessionRecorder, path: str, use_mm: bool = False) -> str:
    """Grafico da abertura bucal filtrada ao longo do tempo, com repeticoes marcadas."""
    if recorder.is_empty:
        raise ValueError("Nao ha amostras para plotar.")
    _ensure_parent(path)

    t, opening, _lateral, unit = _series(recorder, use_mm)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, opening, color="#1f77b4", linewidth=1.5)
    ax.set_ylabel(f"Abertura bucal [{unit}]")
    ax.set_xlabel("Tempo [s]")
    ax.set_title("Abertura bucal - evolucao temporal")
    ax.grid(True, alpha=0.3)

    prev = 0
    for s in recorder.samples:
        if s.repetitions > prev:
            ax.axvline(s.time_s, color="#d62728", alpha=0.35, linestyle="--")
            prev = s.repetitions

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_lateral_time(recorder: SessionRecorder, path: str, use_mm: bool = False) -> str:
    """Grafico do desvio lateral filtrado ao longo do tempo."""
    if recorder.is_empty:
        raise ValueError("Nao ha amostras para plotar.")
    _ensure_parent(path)

    t, _opening, lateral, unit = _series(recorder, use_mm)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, lateral, color="#2ca02c", linewidth=1.5)
    ax.axhline(0.0, color="gray", linewidth=0.8)
    ax.set_ylabel(f"Desvio lateral [{unit}]")
    ax.set_xlabel("Tempo [s]")
    ax.set_title("Desvio lateral da mandibula - evolucao temporal")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_trajectory(recorder: SessionRecorder, path: str, use_mm: bool = False) -> str:
    """Grafico da trajetoria abertura x desvio lateral (visao geral do padrao de movimento)."""
    if recorder.is_empty:
        raise ValueError("Nao ha amostras para plotar.")
    _ensure_parent(path)

    _t, opening, lateral, unit = _series(recorder, use_mm)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(lateral, opening, color="#9467bd", linewidth=0.8, alpha=0.7)
    ax.scatter(lateral, opening, c=range(len(opening)), cmap="viridis", s=6)
    ax.axvline(0.0, color="gray", linewidth=0.8)
    ax.set_xlabel(f"Desvio lateral [{unit}]")
    ax.set_ylabel(f"Abertura bucal [{unit}]")
    ax.set_title("Trajetoria: abertura x desvio lateral")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
