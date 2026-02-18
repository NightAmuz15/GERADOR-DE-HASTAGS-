"""
Módulo de transcrição de áudio.
Usa OpenAI Whisper para transcrever a fala dos vídeos.
"""

import os
import whisper
from rich.console import Console

console = Console()

# Modelo Whisper (singleton)
_model = None


def _get_model(model_name: str = "base"):
    """Carrega o modelo Whisper (inicializa na primeira chamada)."""
    global _model
    if _model is None:
        console.print(f"  🧠 Carregando modelo Whisper '{model_name}' (primeira vez pode demorar)...")
        _model = whisper.load_model(model_name)
    return _model


def transcribe_audio(audio_path: str, model_name: str = "base") -> dict:
    """
    Transcreve um arquivo de áudio usando Whisper.
    
    Args:
        audio_path: Caminho do arquivo de áudio WAV
        model_name: Nome do modelo Whisper ('tiny', 'base', 'small', 'medium', 'large')
    
    Returns:
        Dict com 'text' (transcrição completa), 'language' (idioma detectado),
        'segments' (segmentos com timestamps)
    """
    if audio_path is None or not os.path.exists(audio_path):
        console.print("  [yellow]⚠️ Arquivo de áudio não encontrado[/yellow]")
        return {
            "text": "",
            "language": "unknown",
            "segments": []
        }
    
    try:
        model = _get_model(model_name)
        
        result = model.transcribe(
            audio_path,
            fp16=False,  # CPU-friendly
            verbose=False
        )
        
        text = result.get("text", "").strip()
        language = result.get("language", "unknown")
        segments = result.get("segments", [])
        
        word_count = len(text.split()) if text else 0
        console.print(f"  📝 Transcrição: {word_count} palavras (idioma: {language})")
        
        return {
            "text": text,
            "language": language,
            "segments": segments
        }
    
    except Exception as e:
        console.print(f"  [red]❌ Erro na transcrição: {e}[/red]")
        return {
            "text": "",
            "language": "unknown",
            "segments": []
        }


def cleanup_audio(audio_path: str):
    """Remove arquivo de áudio temporário."""
    try:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception:
        pass
