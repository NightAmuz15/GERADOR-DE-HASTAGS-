#!/usr/bin/env python3
"""
🎬 TikTok Video Analyzer
Analisa vídeos e gera hashtags + descrições automaticamente.

Uso:
    python3 analisar.py                    # Analisa todos os vídeos
    python3 analisar.py "video.mp4"        # Analisa um vídeo específico
    python3 analisar.py --intervalo 3      # Extrai frames a cada 3 segundos
"""

import os
import sys
import glob
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

from tiktok_analyzer.video_processor import extract_frames, extract_audio
from tiktok_analyzer.ocr_extractor import extract_text_from_frames, texts_to_string
from tiktok_analyzer.audio_transcriber import transcribe_audio, cleanup_audio
from tiktok_analyzer.context_analyzer import analyze_content
from tiktok_analyzer.report_generator import generate_reports

console = Console()

# Diretório deste script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "resultados")


def show_banner():
    """Mostra o banner do programa."""
    banner = """
[bold cyan]  ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗
  ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝
     ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝ 
     ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗ 
     ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗
     ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝[/bold cyan]

[bold white]  🎬 Video Analyzer — Gerador de # e Descrições[/bold white]
    """
    console.print(Panel(banner, border_style="cyan", padding=(0, 2)))


def find_videos(specific_video: str = None) -> list:
    """
    Encontra os vídeos MP4 para processar.
    
    Args:
        specific_video: Nome de um vídeo específico (opcional)
    
    Returns:
        Lista de caminhos completos dos vídeos
    """
    if specific_video:
        path = os.path.join(SCRIPT_DIR, specific_video)
        if os.path.exists(path):
            return [path]
        else:
            console.print(f"[red]❌ Vídeo não encontrado: {specific_video}[/red]")
            sys.exit(1)
    
    # Busca todos os MP4 no diretório
    videos = glob.glob(os.path.join(SCRIPT_DIR, "*.mp4"))
    videos += glob.glob(os.path.join(SCRIPT_DIR, "*.MP4"))
    
    # Remove duplicatas (case insensitive)
    seen = set()
    unique_videos = []
    for v in videos:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            unique_videos.append(v)
    
    unique_videos.sort()
    return unique_videos


def process_single_video(video_path: str, frame_interval: float = 2.0) -> dict:
    """
    Processa um único vídeo: extrai texto, transcreve áudio, gera hashtags.
    
    Args:
        video_path: Caminho completo do vídeo
        frame_interval: Intervalo entre frames para OCR (segundos)
    
    Returns:
        Dict com todos os resultados da análise
    """
    video_name = os.path.basename(video_path)
    
    console.print(f"\n[bold cyan]{'─' * 60}[/bold cyan]")
    console.print(f"[bold white]  📹 Processando: {video_name}[/bold white]")
    console.print(f"[bold cyan]{'─' * 60}[/bold cyan]")
    
    # 1. Extrai frames para OCR
    console.print("\n[dim]  Etapa 1/4: Extraindo frames...[/dim]")
    frames = extract_frames(video_path, interval_seconds=frame_interval)
    
    # 2. OCR nos frames
    console.print("[dim]  Etapa 2/4: Detectando texto (OCR)...[/dim]")
    ocr_texts = extract_text_from_frames(frames)
    ocr_text_combined = texts_to_string(ocr_texts)
    
    # Libera memória dos frames
    del frames
    
    # 3. Extrai e transcreve áudio
    console.print("[dim]  Etapa 3/4: Transcrevendo áudio...[/dim]")
    audio_path = extract_audio(video_path)
    transcription_result = transcribe_audio(audio_path)
    cleanup_audio(audio_path)
    
    # 4. Analisa contexto e gera hashtags/descrição
    console.print("[dim]  Etapa 4/4: Gerando hashtags e descrição...[/dim]")
    analysis = analyze_content(ocr_texts, transcription_result)
    
    # Resultado completo
    result = {
        'video': video_name,
        'ocr_text': ocr_text_combined,
        'transcription': transcription_result.get('text', ''),
        'language': transcription_result.get('language', 'unknown'),
        'hashtags': analysis['hashtags'],
        'description': analysis['description'],
        'keywords': analysis['keywords'],
        'categories': analysis['categories'],
    }
    
    # Mostra preview
    _show_preview(result)
    
    return result


def _show_preview(result: dict):
    """Mostra preview dos resultados no terminal."""
    console.print()
    
    # Hashtags
    hashtags_str = " ".join(result['hashtags'])
    console.print(f"  [bold green]🏷️ Hashtags:[/bold green] {hashtags_str}")
    
    # Descrição
    console.print(f"  [bold blue]📝 Descrição:[/bold blue] {result['description'][:150]}")
    
    # Categorias
    if result['categories']:
        cats = ", ".join([f"{cat}" for cat, _ in result['categories'][:3]])
        console.print(f"  [bold magenta]📂 Categorias:[/bold magenta] {cats}")
    
    console.print()


def show_summary(results: list):
    """Mostra tabela resumo no terminal."""
    table = Table(
        title="📊 Resumo da Análise",
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold white",
    )
    
    table.add_column("#", style="dim", width=4)
    table.add_column("Vídeo", style="white", max_width=30)
    table.add_column("Hashtags", style="green", max_width=15)
    table.add_column("Categoria Principal", style="magenta", max_width=20)
    table.add_column("Palavras no Áudio", style="blue", max_width=15)
    
    for i, result in enumerate(results, 1):
        video_name = result['video']
        if len(video_name) > 28:
            video_name = video_name[:25] + "..."
        
        n_hashtags = str(len(result['hashtags']))
        
        main_cat = result['categories'][0][0] if result['categories'] else "—"
        
        word_count = str(len(result['transcription'].split())) if result['transcription'] else "0"
        
        table.add_row(str(i), video_name, n_hashtags, main_cat, word_count)
    
    console.print()
    console.print(table)


def main():
    """Função principal."""
    show_banner()
    
    # Parse argumentos
    specific_video = None
    frame_interval = 2.0
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--intervalo' and i + 1 < len(args):
            frame_interval = float(args[i + 1])
            i += 2
        elif args[i] == '--help' or args[i] == '-h':
            console.print(__doc__)
            sys.exit(0)
        else:
            specific_video = args[i]
            i += 1
    
    # Encontra vídeos
    videos = find_videos(specific_video)
    
    if not videos:
        console.print("[red]❌ Nenhum vídeo MP4 encontrado nesta pasta![/red]")
        sys.exit(1)
    
    console.print(f"\n[bold white]  📹 {len(videos)} vídeo(s) encontrado(s)[/bold white]")
    console.print(f"[dim]  ⏱️ Intervalo de frames: {frame_interval}s[/dim]")
    console.print(f"[dim]  📁 Output: {OUTPUT_DIR}/[/dim]\n")
    
    # Processa cada vídeo
    results = []
    start_time = time.time()
    
    for idx, video_path in enumerate(videos, 1):
        console.print(f"\n[bold yellow]  ⏳ Vídeo {idx}/{len(videos)}[/bold yellow]")
        
        try:
            result = process_single_video(video_path, frame_interval)
            results.append(result)
        except Exception as e:
            console.print(f"[red]  ❌ Erro ao processar {os.path.basename(video_path)}: {e}[/red]")
            continue
    
    elapsed = time.time() - start_time
    
    if not results:
        console.print("[red]❌ Nenhum vídeo foi processado com sucesso![/red]")
        sys.exit(1)
    
    # Mostra resumo
    show_summary(results)
    
    # Gera relatórios
    console.print(f"\n[bold white]  💾 Salvando relatórios...[/bold white]")
    report_paths = generate_reports(results, OUTPUT_DIR)
    
    # Finalização
    console.print(f"\n[bold green]{'═' * 60}[/bold green]")
    console.print(f"[bold green]  ✅ CONCLUÍDO! {len(results)} vídeo(s) analisado(s)[/bold green]")
    console.print(f"[bold green]  ⏱️ Tempo total: {elapsed:.1f} segundos[/bold green]")
    console.print(f"[bold green]{'═' * 60}[/bold green]\n")
    
    console.print("[bold cyan]  💡 Dica: Abra o arquivo 'pronto_para_postar_*.txt'[/bold cyan]")
    console.print("[bold cyan]     na pasta 'resultados/' para copiar e colar no TikTok![/bold cyan]\n")


if __name__ == "__main__":
    main()
