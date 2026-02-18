# GERADOR-DE-HASHTAGS- (TikTok Video Analyzer)

Um utilitário em Python para analisar vídeos (ex.: TikTok/Reels) e gerar automaticamente **hashtags**, **palavras-chave** e uma **descrição** otimizada.  
Ele lê **texto visível** no vídeo via OCR, transcreve o **áudio** com Whisper e usa análise de contexto (TF-IDF + categorias) pra sugerir legenda pronta pra postar.

---

## Como funciona (pipeline)

1. **Extrai frames** do vídeo em um intervalo configurável (ex.: a cada 2s).
2. **OCR (EasyOCR)** nos frames pra capturar frases/legendas aparecendo na tela.
3. **Extrai o áudio** do vídeo e **transcreve (Whisper)**.
4. Junta OCR + transcrição → faz **TF-IDF** pra achar palavras-chave → detecta **categorias** → gera **hashtags** + **descrição**.
5. Salva relatórios em `resultados/` (TXT/JSON e um arquivo “pronto pra colar”).

---

## Estrutura do projeto

- `analisar.py` — script principal (CLI) que roda o fluxo completo.
- `video_processor.py` — extrai frames (OpenCV) e áudio (MoviePy).
- `ocr_extractor.py` — OCR com EasyOCR.
- `audio_transcriber.py` — transcrição com Whisper.
- `context_analyzer.py` — keywords (TF-IDF), categorias e geração de hashtags/descrição.
- `report_generator.py` — geração de relatórios TXT/JSON e arquivo pronto pra postar.
- `iniciar_analise.sh` — script bash pra iniciar (Linux/macOS).

---

## Requisitos

- Python 3.9+ (recomendado 3.10+)
- FFmpeg instalado (pra extração de áudio)
- Dependências Python: `rich`, `opencv-python`, `moviepy`, `easyocr`, `whisper`, `scikit-learn`

> Dica: EasyOCR pode exigir libs do sistema (ex.: `libgl1` no Ubuntu/Debian).

---

## Instalação

```bash
git clone https://github.com/NightAmuz15/GERADOR-DE-HASTAGS-.git
cd GERADOR-DE-HASTAGS-

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install rich opencv-python moviepy easyocr whisper scikit-learn
