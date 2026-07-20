"""
Geracao de graficos da evolucao temporal do movimento mandibular.

Usa matplotlib com backend nao interativo ("Agg") para salvar imagens sem
depender de uma janela grafica.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .recorder import SessionRecorder  # noqa: E402


def plot_session(recorder: SessionRecorder, path: str, use_mm: bool = False) -> str:
    """
    Gera um grafico com a abertura bucal e o desvio lateral ao longo do tempo,
    marcando as repeticoes detectadas. Retorna o caminho salvo.
    """
    if recorder.is_empty:
        raise ValueError("Nao ha amostras para plotar.")

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    t = [s.time_s for s in recorder.samples]

    if use_mm and recorder.samples[0].opening_mm is not None:
        opening = [s.opening_mm for s in recorder.samples]
        lateral = [s.lateral_mm for s in recorder.samples]
        unit = "mm"
    else:
        opening = [s.opening_rel for s in recorder.samples]
        lateral = [s.lateral_rel for s in recorder.samples]
        unit = "rel. (larg. facial)"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax1.plot(t, opening, color="#1f77b4", linewidth=1.5)
    ax1.set_ylabel(f"Abertura bucal [{unit}]")
    ax1.set_title("Movimento mandibular - evolucao temporal")
    ax1.grid(True, alpha=0.3)

    # Marca as transicoes de repeticao (quando a contagem incrementa).
    prev = 0
    for s in recorder.samples:
        if s.repetitions > prev:
            ax1.axvline(s.time_s, color="#d62728", alpha=0.35, linestyle="--")
            prev = s.repetitions

    ax2.plot(t, lateral, color="#2ca02c", linewidth=1.5)
    ax2.axhline(0.0, color="gray", linewidth=0.8)
    ax2.set_ylabel(f"Desvio lateral [{unit}]")
    ax2.set_xlabel("Tempo [s]")
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
