"""
Módulo de extração de texto via OCR.
Usa EasyOCR para ler textos que aparecem nos frames dos vídeos.
"""

import easyocr
from rich.console import Console

console = Console()

# Inicializa o leitor OCR uma vez (singleton)
_reader = None


def _get_reader():
    """Retorna o leitor EasyOCR (inicializa na primeira chamada)."""
    global _reader
    if _reader is None:
        console.print("  🔤 Inicializando modelo OCR (primeira vez pode demorar)...")
        _reader = easyocr.Reader(
            ['pt', 'en'],
            gpu=False,
            verbose=False
        )
    return _reader


def extract_text_from_frames(frames: list, confidence_threshold: float = 0.3) -> list:
    """
    Extrai texto de uma lista de frames usando OCR.
    
    Args:
        frames: Lista de frames (imagens numpy array)
        confidence_threshold: Confiança mínima para aceitar texto (0-1)
    
    Returns:
        Lista de textos únicos encontrados
    """
    reader = _get_reader()
    all_texts = []
    seen_texts = set()
    
    for i, frame in enumerate(frames):
        try:
            results = reader.readtext(frame)
            
            for (bbox, text, confidence) in results:
                if confidence >= confidence_threshold:
                    # Normaliza o texto para deduplicação
                    normalized = text.strip().lower()
                    
                    # Ignora textos muito curtos (provavelmente ruído)
                    if len(normalized) < 2:
                        continue
                    
                    if normalized not in seen_texts:
                        seen_texts.add(normalized)
                        all_texts.append(text.strip())
        
        except Exception as e:
            # Silencia erros de frames individuais
            continue
    
    console.print(f"  🔍 {len(all_texts)} textos únicos encontrados via OCR")
    return all_texts


def texts_to_string(texts: list) -> str:
    """
    Converte lista de textos em uma string consolidada.
    
    Args:
        texts: Lista de textos extraídos
    
    Returns:
        String com todos os textos unidos
    """
    return " ".join(texts)
