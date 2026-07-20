"""
Baixa o modelo Face Landmarker (.task) exigido pela Tasks API do MediaPipe.

Modelo oficial do Google (MediaPipe Models):
    https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
    (~3,8 MB)

O arquivo e salvo em models/face_landmarker.task.
"""

import os
import sys
import urllib.request

URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
DEST = os.path.join("models", "face_landmarker.task")


def main() -> None:
    os.makedirs("models", exist_ok=True)
    if os.path.exists(DEST):
        size = os.path.getsize(DEST)
        print(f"Modelo ja existe: {DEST} ({size/1e6:.1f} MB)")
        return
    print(f"Baixando modelo de:\n  {URL}")
    try:
        urllib.request.urlretrieve(URL, DEST)
    except Exception as exc:  # noqa: BLE001
        print(f"Falha no download: {exc}", file=sys.stderr)
        sys.exit(1)
    size = os.path.getsize(DEST)
    print(f"Modelo salvo em: {DEST} ({size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
