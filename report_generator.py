"""
Módulo de geração de relatórios.
Salva os resultados em TXT (legível) e JSON (programático).
"""

import os
import json
from datetime import datetime
from rich.console import Console

console = Console()


def generate_reports(results: list, output_dir: str) -> dict:
    """
    Gera relatórios TXT e JSON com os resultados da análise.
    
    Args:
        results: Lista de dicts com resultados por vídeo
        output_dir: Pasta para salvar os relatórios
    
    Returns:
        Dict com caminhos dos relatórios gerados
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # --- Relatório TXT ---
    txt_path = os.path.join(output_dir, f"resultados_{timestamp}.txt")
    _generate_txt_report(results, txt_path)
    
    # --- Relatório JSON ---
    json_path = os.path.join(output_dir, f"resultados_{timestamp}.json")
    _generate_json_report(results, json_path)
    
    # --- Arquivo para copiar/colar (hashtags + descrições prontas) ---
    ready_path = os.path.join(output_dir, f"pronto_para_postar_{timestamp}.txt")
    _generate_ready_to_post(results, ready_path)
    
    console.print(f"\n[green]✅ Relatórios salvos em: {output_dir}/[/green]")
    console.print(f"   📄 {os.path.basename(txt_path)}")
    console.print(f"   📊 {os.path.basename(json_path)}")
    console.print(f"   📋 {os.path.basename(ready_path)} (copiar e colar!)")
    
    return {
        'txt': txt_path,
        'json': json_path,
        'ready': ready_path,
    }


def _generate_txt_report(results: list, filepath: str):
    """Gera relatório legível em TXT."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("   🎬 TikTok Video Analyzer — Relatório de Análise\n")
        f.write(f"   📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"   📹 Total de vídeos analisados: {len(results)}\n")
        f.write("=" * 70 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{'─' * 70}\n")
            f.write(f"  📹 VÍDEO {i}: {result['video']}\n")
            f.write(f"{'─' * 70}\n\n")
            
            # Texto OCR
            ocr_text = result.get('ocr_text', '')
            if ocr_text:
                f.write(f"  🔤 TEXTO DETECTADO (OCR):\n")
                f.write(f"     {ocr_text[:500]}\n\n")
            else:
                f.write(f"  🔤 TEXTO DETECTADO (OCR): Nenhum texto encontrado\n\n")
            
            # Transcrição
            transcription = result.get('transcription', '')
            if transcription:
                f.write(f"  🎤 TRANSCRIÇÃO DO ÁUDIO:\n")
                f.write(f"     {transcription[:500]}\n\n")
            else:
                f.write(f"  🎤 TRANSCRIÇÃO DO ÁUDIO: Nenhuma fala detectada\n\n")
            
            # Categorias
            categories = result.get('categories', [])
            if categories:
                cats_str = ", ".join([f"{cat} ({score}pts)" for cat, score in categories[:3]])
                f.write(f"  📂 CATEGORIAS: {cats_str}\n\n")
            
            # Palavras-chave
            keywords = result.get('keywords', [])
            if keywords:
                kw_str = ", ".join([kw for kw, score in keywords[:8]])
                f.write(f"  🔑 PALAVRAS-CHAVE: {kw_str}\n\n")
            
            # Hashtags
            hashtags = result.get('hashtags', [])
            f.write(f"  🏷️ HASHTAGS:\n")
            f.write(f"     {' '.join(hashtags)}\n\n")
            
            # Descrição
            description = result.get('description', '')
            f.write(f"  📝 DESCRIÇÃO SUGERIDA:\n")
            f.write(f"     {description}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("   Gerado por TikTok Video Analyzer 🚀\n")
        f.write("=" * 70 + "\n")


def _generate_json_report(results: list, filepath: str):
    """Gera relatório em JSON."""
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_videos': len(results),
        'videos': []
    }
    
    for result in results:
        video_data = {
            'filename': result['video'],
            'ocr_text': result.get('ocr_text', ''),
            'transcription': result.get('transcription', ''),
            'language': result.get('language', 'unknown'),
            'hashtags': result.get('hashtags', []),
            'description': result.get('description', ''),
            'keywords': [{'word': kw, 'score': round(score, 4)} 
                        for kw, score in result.get('keywords', [])],
            'categories': [{'name': cat, 'score': score} 
                          for cat, score in result.get('categories', [])],
        }
        report['videos'].append(video_data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def _generate_ready_to_post(results: list, filepath: str):
    """Gera arquivo com hashtags e descrições prontas para copiar e colar."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("📋 PRONTO PARA POSTAR NO TIKTOK\n")
        f.write(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write("Copie a descrição + hashtags abaixo para cada vídeo:\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{'━' * 50}\n")
            f.write(f"📹 {result['video']}\n")
            f.write(f"{'━' * 50}\n\n")
            
            description = result.get('description', '')
            hashtags = result.get('hashtags', [])
            
            # Texto pronto para copiar
            f.write(f"{description}\n\n")
            f.write(f"{' '.join(hashtags)}\n\n\n")
