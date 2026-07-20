"""
Sistema de reconhecimento mandibular digital.

Ferramenta de apoio a analise medica/odontologica que utiliza visao
computacional (MediaPipe Face Mesh + OpenCV) para acompanhar o movimento
mandibular por meio de uma camera comum.

Metricas estimadas:
    - Abertura bucal relativa (normalizada por referencia facial estavel);
    - Desvio lateral da mandibula em relacao a linha media facial;
    - Repetibilidade do movimento (ciclos de abertura/fechamento).

Uso apenas como apoio; nao substitui a avaliacao profissional.
"""

__version__ = "0.1.0"
