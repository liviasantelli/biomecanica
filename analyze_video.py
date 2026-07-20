"""
Analise offline de um video gravado (sem webcam ao vivo).

Processa cada frame de um arquivo de video, calcula as metricas mandibulares,
detecta os ciclos de abertura/fechamento e gera:
    - CSV com a serie temporal;
    - grafico PNG da evolucao;
    - resumo com repetibilidade e comparacao com faixas de referencia.

Util para validacao com videos controlados (Semana 5 do cronograma) e para
reprocessar coletas sem depender da camera.

Exemplos:
    python analyze_video.py coleta.mp4
    python analyze_video.py coleta.mp4 --ref-mm 63 --calib-auto
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

import numpy as np

sys.path.insert(0, "src")

import cv2  # noqa: E402

from mandibular.config import AppConfig  # noqa: E402
from mandibular.landmarks import FaceMeshDetector  # noqa: E402
from mandibular.metrics import CycleDetector, compute_frame_metrics  # noqa: E402
from mandibular.plotting import plot_session  # noqa: E402
from mandibular.recorder import Sample, SessionRecorder  # noqa: E402

# Faixas de referencia (Biomecanica Funcional, Cap. 16 - ver docs/pesquisa).
REF_ABERTURA_MM = (40.0, 60.0)   # abertura da boca normal
REF_DIDUCAO_MM = (9.0, 12.0)     # amplitude de lateralizacao (diducao) normal


def analyze(path: str, ref_mm: float | None, calib_auto: bool, output_dir: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video nao encontrado: {path}")

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir o video: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    print(f"Video: {path}  ({fps:.1f} fps, {n_frames} frames)")

    detector = FaceMeshDetector(AppConfig().detection)
    recorder = SessionRecorder()

    # 1a passada: coleta metricas e (se calib-auto) descobre a faixa de abertura.
    openings: list[float] = []
    frames_data: list[tuple[int, float, object]] = []
    idx = 0
    faces_ok = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t = idx / fps
        ts_ms = int(t * 1000)
        face = detector.process(frame, ts_ms)
        if face is not None:
            faces_ok += 1
            m = compute_frame_metrics(face, ref_mm)
            openings.append(m.opening_rel)
            frames_data.append((idx, t, m))
        idx += 1
    cap.release()
    detector.close()

    if not frames_data:
        print("Nenhuma face detectada no video.")
        return

    print(f"Faces detectadas em {faces_ok}/{idx} frames "
          f"({100 * faces_ok / max(idx, 1):.0f}%).")

    # Detector de ciclos: calibra pela faixa observada (percentis, robusto a ruido).
    cycles = CycleDetector(AppConfig().cycle)
    if calib_auto or True:
        arr = np.array(openings)
        closed = float(np.percentile(arr, 5))
        opened = float(np.percentile(arr, 95))
        cycles.calibrate(closed, opened)
        print(f"Calibracao automatica: fechado~{closed:.3f}  aberto~{opened:.3f} (rel)")

    # 2a passada (sobre os dados ja extraidos): serie temporal + ciclos.
    for frame_idx, t, m in frames_data:
        cycles.update(m.opening_rel, t)
        recorder.add(
            Sample(
                frame=frame_idx,
                time_s=t,
                opening_rel=m.opening_rel,
                lateral_rel=m.lateral_rel,
                opening_mm=m.opening_mm,
                lateral_mm=m.lateral_mm,
                state=cycles.state,
                repetitions=cycles.repetitions,
            )
        )

    # Exporta.
    os.makedirs(output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(path))[0]
    csv_path = os.path.join(output_dir, f"{base}_{stamp}.csv")
    png_path = os.path.join(output_dir, f"{base}_{stamp}.png")
    recorder.to_csv(csv_path)
    plot_session(recorder, png_path, use_mm=(ref_mm is not None))

    _print_summary(recorder, cycles, ref_mm)
    print(f"\n[export] CSV: {csv_path}")
    print(f"[export] PNG: {png_path}")


def _print_summary(recorder, cycles, ref_mm) -> None:
    openings_rel = np.array([s.opening_rel for s in recorder.samples])
    lateral_rel = np.array([s.lateral_rel for s in recorder.samples])

    print("\n" + "=" * 52)
    print("RESUMO DA ANALISE")
    print("=" * 52)
    print(f"Repeticoes (ciclos abre/fecha): {cycles.repetitions}")
    print(f"Abertura maxima:  {openings_rel.max():.3f} rel")
    print(f"Desvio lateral:   min {lateral_rel.min():+.3f} / max {lateral_rel.max():+.3f} rel")
    print(f"Desvio lat. medio:{lateral_rel.mean():+.3f} rel (assimetria do caminho)")

    rep = cycles.repeatability()
    if rep:
        print(f"\nRepetibilidade ({int(rep['n_ciclos'])} ciclos):")
        print(f"  amplitude: media {rep['amplitude_media']:.3f}  "
              f"CV {rep['amplitude_cv']:.2f}")
        print(f"  duracao:   media {rep['duracao_media_s']:.2f}s  "
              f"CV {rep['duracao_cv']:.2f}")
        print("  (CV menor = movimento mais repetivel/consistente)")

    if ref_mm is not None:
        ab_mm = np.array([s.opening_mm for s in recorder.samples]).max()
        lat_amp_mm = (np.array([s.lateral_mm for s in recorder.samples]).max()
                      - np.array([s.lateral_mm for s in recorder.samples]).min())
        print("\nComparacao com faixas de referencia (em mm):")
        print(f"  abertura max = {ab_mm:.1f} mm  "
              f"(referencia normal: {REF_ABERTURA_MM[0]:.0f}-{REF_ABERTURA_MM[1]:.0f} mm)")
        print(f"  amplitude lateral = {lat_amp_mm:.1f} mm  "
              f"(referencia diducao: {REF_DIDUCAO_MM[0]:.0f}-{REF_DIDUCAO_MM[1]:.0f} mm)")
        print("  >> Valores estimados; apoio, nao diagnostico.")


def main() -> None:
    p = argparse.ArgumentParser(description="Analise offline de video mandibular.")
    p.add_argument("video", help="caminho do arquivo de video")
    p.add_argument("--ref-mm", type=float, default=None,
                   help="distancia real (mm) entre os cantos externos dos olhos")
    p.add_argument("--calib-auto", action="store_true",
                   help="(padrao) calibra a faixa pelos percentis do proprio video")
    p.add_argument("--output", default="resultados", help="pasta de saida")
    a = p.parse_args()
    analyze(a.video, a.ref_mm, a.calib_auto, a.output)


if __name__ == "__main__":
    main()
