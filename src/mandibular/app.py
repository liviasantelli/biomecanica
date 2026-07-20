"""
Aplicacao em tempo real: captura por webcam, deteccao facial, calculo das
metricas, interface visual com biofeedback e exportacao de dados.

Controles do teclado:
    C  - calibrar (assistente: boca fechada -> boca aberta)
    R  - iniciar/parar gravacao da sessao
    E  - exportar CSV + grafico da sessao gravada
    Z  - zerar sessao (amostras e contagem de repeticoes)
    Q / ESC - sair
"""

from __future__ import annotations

import os
import time
from datetime import datetime

import cv2
import numpy as np

from .config import AppConfig, HIGHLIGHT_POINTS, Landmark
from .landmarks import FaceMeshDetector
from .metrics import (
    CycleDetector,
    MovementState,
    compute_frame_metrics,
)
from .plotting import plot_session
from .recorder import Sample, SessionRecorder


# Cores (BGR).
_C_PONTO = (0, 255, 0)
_C_LINHA = (255, 200, 0)
_C_TEXTO = (255, 255, 255)
_C_PAINEL = (30, 30, 30)
_C_REC = (0, 0, 255)
_C_OK = (0, 220, 0)
_C_ALERTA = (0, 180, 255)


class CalibrationAssistant:
    """Assistente de calibracao em duas fases: boca fechada e boca aberta."""

    HOLD_SECONDS = 1.5

    def __init__(self):
        self.active = False
        self.phase = 0          # 0 = fechado, 1 = aberto
        self.phase_start = 0.0
        self.closed_samples: list[float] = []
        self.open_samples: list[float] = []

    def start(self) -> None:
        self.active = True
        self.phase = 0
        self.phase_start = time.perf_counter()
        self.closed_samples.clear()
        self.open_samples.clear()

    def update(self, opening: float, now: float) -> tuple[float, float] | None:
        """
        Coleta amostras da fase atual. Retorna (fechado, aberto) quando a
        calibracao termina; caso contrario, None.
        """
        if not self.active:
            return None

        elapsed = now - self.phase_start
        if self.phase == 0:
            self.closed_samples.append(opening)
            if elapsed >= self.HOLD_SECONDS:
                self.phase = 1
                self.phase_start = now
        else:
            self.open_samples.append(opening)
            if elapsed >= self.HOLD_SECONDS:
                self.active = False
                closed = float(np.median(self.closed_samples)) if self.closed_samples else 0.0
                opened = float(np.max(self.open_samples)) if self.open_samples else closed + 0.1
                return closed, opened
        return None

    def instruction(self, now: float) -> str:
        remaining = max(0.0, self.HOLD_SECONDS - (now - self.phase_start))
        if self.phase == 0:
            return f"CALIBRANDO: mantenha a BOCA FECHADA ({remaining:.1f}s)"
        return f"CALIBRANDO: abra a BOCA ao maximo ({remaining:.1f}s)"


class MandibularApp:
    def __init__(self, config: AppConfig | None = None):
        self.cfg = config or AppConfig()
        self.detector = FaceMeshDetector(self.cfg.detection)
        self.cycles = CycleDetector(self.cfg.cycle)
        self.recorder = SessionRecorder()
        self.calib = CalibrationAssistant()

        self.recording = False
        self.frame_idx = 0
        self.t0 = time.perf_counter()
        self._last_ts_ms = -1
        self.last_status = ""

    # -- Desenho ----------------------------------------------------------
    def _draw_landmarks(self, frame: np.ndarray, face) -> None:
        # Linha media (nasion -> queixo) e eixo inter-ocular.
        for a, b in [
            (Landmark.NASION, Landmark.CHIN),
            (Landmark.EYE_OUTER_LEFT, Landmark.EYE_OUTER_RIGHT),
            (Landmark.UPPER_LIP_INNER, Landmark.LOWER_LIP_INNER),
        ]:
            pa = tuple(np.round(face.point(a)).astype(int))
            pb = tuple(np.round(face.point(b)).astype(int))
            cv2.line(frame, pa, pb, _C_LINHA, 1, cv2.LINE_AA)

        for idx in HIGHLIGHT_POINTS:
            p = tuple(np.round(face.point(idx)).astype(int))
            cv2.circle(frame, p, 3, _C_PONTO, -1, cv2.LINE_AA)

    def _draw_panel(self, frame: np.ndarray, lines: list[tuple[str, tuple]]) -> None:
        pad = 12
        line_h = 26
        w = 360
        h = pad * 2 + line_h * len(lines)
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (10 + w, 10 + h), _C_PAINEL, -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
        y = 10 + pad + 18
        for text, color in lines:
            cv2.putText(frame, text, (10 + pad, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, color, 1, cv2.LINE_AA)
            y += line_h

    def _draw_opening_bar(self, frame: np.ndarray, opening_rel: float) -> None:
        """Barra de biofeedback da abertura (0..faixa calibrada)."""
        h, w = frame.shape[:2]
        x0, y0 = w - 60, 60
        bar_h = h - 120
        cv2.rectangle(frame, (x0, y0), (x0 + 30, y0 + bar_h), (80, 80, 80), 1)

        # Fracao 0..1 relativa a faixa calibrada (ou 0..0.6 como fallback).
        if self.cycles.is_calibrated:
            base = self.cycles._baseline or 0.0
            span = self.cycles._span or 1e-6
            frac = (opening_rel - base) / span
        else:
            frac = opening_rel / 0.6
        frac = float(np.clip(frac, 0.0, 1.0))

        fill = int(bar_h * frac)
        cv2.rectangle(frame, (x0, y0 + bar_h - fill), (x0 + 30, y0 + bar_h),
                      _C_OK, -1)
        cv2.putText(frame, "abertura", (x0 - 20, y0 - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, _C_TEXTO, 1, cv2.LINE_AA)

    # -- Loop principal ---------------------------------------------------
    def run(self) -> None:
        cap = cv2.VideoCapture(self.cfg.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.frame_height)

        if not cap.isOpened():
            raise RuntimeError(
                f"Nao foi possivel abrir a camera (indice {self.cfg.camera_index})."
            )

        win = "Reconhecimento Mandibular - Biomecanica"
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if self.cfg.flip_horizontal:
                    frame = cv2.flip(frame, 1)

                now = time.perf_counter()
                t = now - self.t0
                # Timestamp monotonicamente crescente (exigencia do modo VIDEO).
                ts_ms = max(int(t * 1000), self._last_ts_ms + 1)
                self._last_ts_ms = ts_ms
                face = self.detector.process(frame, ts_ms)

                if face is not None:
                    self._draw_landmarks(frame, face)
                    m = compute_frame_metrics(face, self.cfg.reference_distance_mm)

                    # Calibracao guiada tem prioridade sobre a deteccao de ciclos.
                    calib_result = self.calib.update(m.opening_rel, now)
                    if calib_result is not None:
                        self.cycles.calibrate(*calib_result)
                        self.last_status = "Calibracao concluida."

                    if not self.calib.active:
                        self.cycles.update(m.opening_rel, t)

                    self._draw_opening_bar(frame, m.opening_rel)
                    self._update_hud(frame, m, now)

                    if self.recording and not self.calib.active:
                        self.recorder.add(
                            Sample(
                                frame=self.frame_idx,
                                time_s=t,
                                opening_rel=m.opening_rel,
                                lateral_rel=m.lateral_rel,
                                opening_mm=m.opening_mm,
                                lateral_mm=m.lateral_mm,
                                state=self.cycles.state,
                                repetitions=self.cycles.repetitions,
                            )
                        )
                else:
                    self._draw_panel(frame, [("Nenhuma face detectada", _C_ALERTA)])

                self.frame_idx += 1
                cv2.imshow(win, frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):  # q ou ESC
                    break
                elif key == ord("c"):
                    self.calib.start()
                    self.last_status = "Iniciando calibracao..."
                elif key == ord("r"):
                    self.recording = not self.recording
                    self.last_status = (
                        "Gravacao iniciada." if self.recording else "Gravacao pausada."
                    )
                elif key == ord("e"):
                    self._export()
                elif key == ord("z"):
                    self._reset()
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.detector.close()

    def _update_hud(self, frame, m, now: float) -> None:
        state = self.cycles.state
        state_color = {
            MovementState.FECHADO: _C_TEXTO,
            MovementState.ABRINDO: _C_OK,
            MovementState.ABERTO: _C_OK,
            MovementState.FECHANDO: _C_ALERTA,
        }[state]

        if m.opening_mm is not None:
            abertura_txt = f"Abertura: {m.opening_rel:.3f} rel  ({m.opening_mm:.1f} mm)"
            lateral_txt = f"Desvio lat.: {m.lateral_rel:+.3f} rel  ({m.lateral_mm:+.1f} mm)"
        else:
            abertura_txt = f"Abertura: {m.opening_rel:.3f} (rel. larg. facial)"
            lateral_txt = f"Desvio lateral: {m.lateral_rel:+.3f}"

        lines = [
            (abertura_txt, _C_TEXTO),
            (lateral_txt, _C_TEXTO),
            (f"Estado: {state.value.upper()}", state_color),
            (f"Repeticoes: {self.cycles.repetitions}", _C_TEXTO),
            (
                "Calibrado: sim" if self.cycles.is_calibrated else "Calibrado: nao (tecle C)",
                _C_OK if self.cycles.is_calibrated else _C_ALERTA,
            ),
            (
                "REC" if self.recording else "[C]alibrar [R]ec [E]xport [Z]erar [Q]sair",
                _C_REC if self.recording else _C_TEXTO,
            ),
        ]
        if self.calib.active:
            lines = [(self.calib.instruction(now), _C_ALERTA)] + lines
        if self.last_status:
            lines.append((self.last_status, _C_OK))
        self._draw_panel(frame, lines)

    # -- Acoes ------------------------------------------------------------
    def _export(self) -> None:
        if self.recorder.is_empty:
            self.last_status = "Nada gravado para exportar (tecle R primeiro)."
            return
        os.makedirs(self.cfg.output_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(self.cfg.output_dir, f"sessao_{stamp}.csv")
        png_path = os.path.join(self.cfg.output_dir, f"sessao_{stamp}.png")
        self.recorder.to_csv(csv_path)
        use_mm = self.cfg.reference_distance_mm is not None
        try:
            plot_session(self.recorder, png_path, use_mm=use_mm)
        except ValueError:
            png_path = "(sem grafico)"

        rep = self.cycles.repeatability()
        rep_txt = ""
        if rep:
            rep_txt = (
                f" | ciclos={int(rep['n_ciclos'])}"
                f" ampl.CV={rep['amplitude_cv']:.2f}"
                f" dur.CV={rep['duracao_cv']:.2f}"
            )
        self.last_status = f"Exportado: {os.path.basename(csv_path)}{rep_txt}"
        print(f"[export] CSV: {csv_path}")
        print(f"[export] PNG: {png_path}")
        if rep:
            print(f"[export] repetibilidade: {rep}")

    def _reset(self) -> None:
        self.recorder.clear()
        self.cycles = CycleDetector(self.cfg.cycle)
        self.frame_idx = 0
        self.t0 = time.perf_counter()
        self._last_ts_ms = -1
        self.recording = False
        self.last_status = "Sessao zerada."
