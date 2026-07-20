# Pesquisa — Biomecânica da ATM e do movimento mandibular

**Projeto:** Sistema de reconhecimento mandibular digital para apoio à análise médica
**Disciplina:** Biomecânica — Engenharia Biomédica
**Integrantes:** Livia Santelli Pegoraro e Maria Luisa Gonçalves Ferreira
**Entregável:** Semana 1 — Revisão de ATM, movimento mandibular e ferramentas de visão computacional

> **Nota de fundamentação.** Os valores anatômicos e as amplitudes de referência
> deste documento foram extraídos de *Biomecânica Funcional* (Dufour & Pillu),
> Capítulo 16 — "Cabeça (crânio e face)", nas páginas indicadas entre parênteses
> (numeração impressa do livro). Onde há estimativa, derivação ou aproximação, isso
> está sinalizado no texto. Este material é de **apoio e uso didático**; não
> constitui protocolo diagnóstico.

---

## 1. Objetivo da revisão

Fundamentar biomecanicamente as métricas que o software calcula a partir de
vídeo — **abertura bucal**, **desvio lateral (didução)** e **repetibilidade** —,
relacionando cada uma ao movimento fisiológico da articulação temporomandibular
(ATM) e às faixas de amplitude consideradas normais na literatura da disciplina.

---

## 2. Anatomia funcional da ATM

A ATM é **a única articulação da cabeça com mobilidade visível e importante**
(p. 546). Anatomicamente é classificada como **bicondilar**: existem duas
articulações, uma direita e uma esquerda, fisicamente separadas mas
funcionalmente acopladas (p. 546). Cada côndilo mandibular é um ovoide cujo
grande eixo forma um ângulo de cerca de **160°** com o contralateral (p. 546).

Componentes relevantes para o movimento:

- **Superfícies articulares** — no crânio, o tubérculo articular do temporal
  (convexo) e a fossa mandibular (côncava); na mandíbula, o côndilo mandibular
  (p. 545–546).
- **Disco articular** — menisco móvel que recobre o côndilo "como uma boina",
  dividindo a cavidade em compartimentos superior e inferior; é tracionado para
  a frente pelo pterigóideo lateral durante a abertura da boca (p. 548).
- **Cápsula e ligamentos** — cápsula frouxa com sinovial fibrosa; ligamentos
  colaterais medial e lateral de cada lado (p. 548).

A posição estável passiva é o **fechamento da boca com os dentes engrenados**;
a abertura máxima é estabilizada ativamente pela musculatura. As **posições
intermediárias** são as de maior risco mecânico, quando a propulsão se soma ao
abaixamento (p. 554).

---

## 3. Movimentos mandibulares e amplitudes de referência

O livro organiza a mobilidade da ATM em movimentos **analíticos** (elementares)
e a mobilidade **funcional** (a abertura da boca real, que combina os
analíticos). Os movimentos da ATM servem a três funções: **mastigação, fonação
e deglutição** (p. 551).

### 3.1 Abaixamento–elevação
Movimento **sagital**, em torno de um eixo transversal que passa pelo centro das
cabeças condilares (p. 551). É a "abertura angular" pura (visível em um esqueleto
montado), que difere da abertura da boca real do ser humano.

### 3.2 Propulsão–retropulsão
Deslizamento da mandíbula para a frente e para trás, em **plano horizontal**.
Amplitude normal da propulsão: **6 a 8 mm** (medida entre os incisivos superiores
e inferiores); a retropulsão tem amplitude semelhante, em sentido inverso (p. 551).

### 3.3 Didução (lateralização) — base do "desvio lateral"
Movimento de **lateralização da ponta do queixo** para a direita ou esquerda,
produzido pelo avanço unilateral de um côndilo enquanto o outro permanece na
fossa. Amplitude média: **9 a 12 mm** (p. 553). É um teste clínico importante da
propulsão unilateral.

### 3.4 Abertura da boca (mobilidade funcional) — base da "abertura"
É um movimento **combinado**: primeiro um abaixamento angular (até ~20 mm de
afastamento dos dentes), ao qual se associa, em seguida, uma propulsão (p. 553).
Amplitude normal: **em média 40 a 60 mm** — equivalente a intercalar três dedos
sobrepostos entre os dentes superiores e inferiores (p. 553).

### 3.5 Caminho de abertura e simetria — base da "assimetria/desvio"
A estabilidade dinâmica se traduz pelo **domínio da simetria na abertura**,
formando um **"caminho de abertura sagital"** (p. 554). A simetria posicional é
avaliada pelo **alinhamento entre a junção dos incisivos superiores e inferiores**
(p. 554). Perturbações do caminho de abertura (mau alinhamento no início ou ao
longo do movimento) são medidas **em milímetros com paquímetro**, entre a linha
de separação dos incisivos (p. 553).

### Tabela-resumo (valores de referência)

| Movimento | Amplitude normal | Fonte (pág.) |
|---|---|---|
| Abertura da boca | **40–60 mm** | p. 553 |
| Didução (lateral) | **9–12 mm** | p. 553 |
| Propulsão / retropulsão | **6–8 mm** | p. 551 |
| Início da propulsão na abertura | a partir de ~20 mm | p. 553 |

---

## 4. Musculatura

Os músculos mastigadores são classificados pela função — levantadores,
abaixadores, propulsores ou retropropulsores (p. 548, Quadro 16.1):

| Músculo | Abaix. | Elev. | Prop. | Retrop. |
|---|:--:|:--:|:--:|:--:|
| Masseter | – | +++ | P | – |
| Temporal | – | +++ | – | R |
| Pterigóideo lateral | – | – | +++ | – |
| Pterigóideo medial | – | E | P | – |
| Milo-hióideo | A | – | – | R |
| Digástrico | A | – | – | R |
| Gênio-hióideo | A | – | – | R |

Todos os mastigadores são inervados pelo **trigêmeo (nervo mandibular, V3)**; os
músculos da face (inervados pelo nervo facial, VII) funcionam como músculos de
substituição (p. 548).

---

## 5. Disfunções temporomandibulares (contexto clínico)

Alterações do movimento se manifestam como perturbações do caminho de abertura,
estalidos/ressaltos na propulsão, assimetrias e dor. O livro agrupa essas
condições sob **"síndromes algo-disfuncionais do aparelho mandibular" (SADAM)**
— na literatura mais recente, **disfunção temporomandibular (DTM)** (p. 553). A
reeducação recorre à cinesioterapia, ortofonia e ortodontia (p. 551).

Isso justifica o valor de um **registro objetivo e repetível** entre sessões —
exatamente o que o software oferece como complemento à observação clínica.

---

## 6. Ferramentas de visão computacional

### 6.1 MediaPipe Face Landmarker (Tasks API)
Modelo de malha facial do Google que estima **478 landmarks 3D** da face a partir
de imagem 2D (468 do modelo base + 10 refinamentos de íris). Roda em CPU em tempo
real, sem hardware especializado — adequado ao requisito de **baixo custo** do
projeto. Fornece coordenadas normalizadas `(x, y, z)` por landmark, com índices
estáveis correspondentes a pontos anatômicos conhecidos.

> **Observação técnica de ambiente.** A versão instalada expõe apenas a *Tasks
> API* (`FaceLandmarker`), não a antiga `mediapipe.solutions.face_mesh`. O modelo
> `.task` é obtido via `download_model.py`. Os índices de landmark permanecem os
> mesmos do Face Mesh canônico.

### 6.2 OpenCV
Captura de vídeo (webcam ou arquivo), conversão de espaço de cor, desenho da
sobreposição (landmarks, linhas, painel, barra de biofeedback) e a janela
interativa.

### 6.3 Pontos anatômicos utilizados (índices Face Mesh)

| Ponto | Índice | Uso na métrica |
|---|---|---|
| Canto externo do olho esq./dir. | 33 / 263 | Referência facial (escala) + eixo horizontal |
| Raiz do nariz (nasion) | 168 | Referência da linha média |
| Ponta do nariz | 1 | Linha média (apoio visual) |
| Lábio interno superior/inferior | 13 / 14 | Abertura bucal |
| Cantos da boca | 61 / 291 | Extremidades da boca |
| Queixo (menton) | 152 | Desvio lateral |

---

## 7. Mapeamento biomecânica → métricas do software

Esta é a ponte entre a revisão e o código (`src/mandibular/metrics.py`).

### 7.1 Abertura bucal
- **Biomecânica:** abertura funcional da boca (abaixamento + propulsão), normal 40–60 mm (p. 553).
- **No software:** componente vertical da distância entre os lábios internos (13–14), **normalizada pela largura facial** (distância entre os cantos externos dos olhos, 33–263). A normalização torna a medida invariante à distância da câmera. Com calibração `--ref-mm`, converte-se para milímetros e pode-se comparar com a faixa 40–60 mm.

### 7.2 Desvio lateral (didução)
- **Biomecânica:** lateralização da ponta do queixo, normal 9–12 mm; e a avaliação de simetria pelo alinhamento dos incisivos / caminho de abertura sagital (p. 553–554).
- **No software:** componente **horizontal** da posição do queixo (152) em relação à raiz do nariz (168), projetada sobre o eixo inter-ocular e normalizada pela largura facial. O sinal indica o lado do desvio; a média ao longo da abertura estima a **assimetria do caminho**.

### 7.3 Repetibilidade
- **Biomecânica:** o movimento fisiológico requer harmonia e simetria repetíveis; disfunções aparecem como inconsistência entre repetições (p. 553).
- **No software:** máquina de estados com histerese detecta ciclos abre/fecha; calcula-se amplitude e duração por ciclo e o **coeficiente de variação (CV)** entre ciclos. CV baixo = movimento mais consistente.

### 7.4 Robustez (escolhas de projeto)
Como as medidas são projetadas no referencial definido pelo **eixo inter-ocular**,
elas são aproximadamente invariantes à **inclinação da cabeça no plano (roll)** e
à **distância da câmera** — propriedades verificadas por testes automatizados
(`tests/test_metrics.py`: `test_roll_invariance`, `test_scale_invariance`).

---

## 8. Protocolo de captura proposto (rascunho — Semana 1/3)

1. Iluminação frontal difusa; fundo neutro; rosto totalmente enquadrado.
2. Cabeça estável e frontal à câmera (limitação assumida do método 2D).
3. Calibração: 1,5 s de boca fechada, depois abertura máxima (tecla `C`).
4. (Opcional) informar `--ref-mm` com a distância real entre os cantos externos
   dos olhos, para leitura em milímetros.
5. Movimentos padronizados: N aberturas/fechamentos completos; N lateralizações
   para cada lado.
6. Exportar CSV + gráfico (tecla `E`) e registrar por sessão para comparação.

---

## 9. Limitações

- **Método 2D:** rotações da cabeça fora do plano (yaw/pitch) reduzem a precisão,
  sobretudo do desvio lateral. A literatura mede a didução em 3D (avanço condilar);
  a estimativa por câmera única é uma **aproximação projetiva**.
- **Calibração mm:** depende de uma medida real informada; sem ela, as medidas são
  relativas (adimensionais) e servem para comparação intrasujeito.
- **Referência facial:** assume que a distância inter-ocular não varia — válido
  para o mesmo sujeito, mas não comparável entre sujeitos diferentes sem calibração.
- **Não é dispositivo médico:** ferramenta de **apoio e ensino**; não substitui
  exame clínico, palpação do trago, paquímetro nem imagem (RM/TC) da ATM.

---

## 10. Referências

- **Dufour, M.; Pillu, M.** *Biomecânica Funcional.* Cap. 16 — "Cabeça (crânio e
  face)": pp. 545–557 (material da disciplina). Fonte das amplitudes e da anatomia
  funcional da ATM citadas acima.
  - Referências internas do capítulo para claims específicos: Catic & Naeije
    (1999) — eixo do abaixamento; Naeije & Hofman (2003), Rantala et al. (2003) —
    abertura da boca; Hiraba et al. (2000) — didução; Itoh et al. (1996), Javaux
    et al. (1999) — geometria condilar; Gillies et al. (2003) — simetria dos
    incisivos.
- **Google MediaPipe** — Face Landmarker (Tasks API), 478 landmarks faciais.
  Documentação técnica do modelo `face_landmarker.task`.
- **OpenCV** — biblioteca de visão computacional (captura, processamento e
  exibição de vídeo).

> Os valores clínicos (40–60 mm, 9–12 mm, 6–8 mm) provêm da fonte impressa citada
> e devem ser confirmados com a bibliografia clínica de referência antes de uso
> fora do contexto didático.
