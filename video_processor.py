"""
Módulo de processamento de vídeo.
Extrai frames (para OCR) e áudio (para transcrição) dos vídeos.
"""

import os
import tempfile
import cv2
from moviepy import VideoFileClip
from rich.console import Console

console = Console()


def extract_frames(video_path: str, interval_seconds: float = 2.0) -> list:
    """
    Extrai frames do vídeo a cada N segundos.
    
    Args:
        video_path: Caminho do arquivo de vídeo
        interval_seconds: Intervalo entre frames extraídos (padrão: 2s)
    
    Returns:
        Lista de frames (imagens numpy array)
    """
    frames = []
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        console.print(f"[red]❌ Não foi possível abrir o vídeo: {video_path}[/red]")
        return frames
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    frame_interval = int(fps * interval_seconds)
    if frame_interval < 1:
        frame_interval = 1
    
    frame_count = 0
    extracted = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            frames.append(frame)
            extracted += 1
        
        frame_count += 1
    
    cap.release()
    console.print(f"  📸 {extracted} frames extraídos ({duration:.1f}s de vídeo)")
    
    return frames


def extract_audio(video_path: str, output_dir: str = None) -> str:
    """
    Extrai o áudio do vídeo como arquivo WAV.
    
    Args:
        video_path: Caminho do arquivo de vídeo
        output_dir: Pasta para salvar o áudio (padrão: temp)
    
    Returns:
        Caminho do arquivo WAV extraído, ou None se falhar
    """
    try:
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(output_dir, f"{video_name}_audio.wav")
        
        clip = VideoFileClip(video_path)
        
        if clip.audio is None:
            console.print("  🔇 Vídeo sem áudio")
            clip.close()
            return None
        
        clip.audio.write_audiofile(
            audio_path,
            fps=16000,  # 16kHz para Whisper
            nbytes=2,
            codec='pcm_s16le',
            logger=None
        )
        clip.close()
        
        console.print(f"  🎵 Áudio extraído com sucesso")
        return audio_path
    
    except Exception as e:
        console.print(f"  [yellow]⚠️ Erro ao extrair áudio: {e}[/yellow]")
        return None
