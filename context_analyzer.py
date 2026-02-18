"""
Módulo de análise de contexto e geração de hashtags/descrições.
Usa TF-IDF para extrair palavras-chave e gera conteúdo otimizado para TikTok.
"""

import re
import string
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from rich.console import Console

console = Console()

# Stop words em português e inglês comuns
STOP_WORDS_PT = {
    'a', 'o', 'e', 'é', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na',
    'nos', 'nas', 'um', 'uma', 'uns', 'umas', 'para', 'por', 'com', 'sem',
    'que', 'se', 'não', 'mais', 'mas', 'como', 'ou', 'eu', 'tu', 'ele',
    'ela', 'nós', 'vós', 'eles', 'elas', 'esse', 'essa', 'este', 'esta',
    'isso', 'isto', 'aquele', 'aquela', 'seu', 'sua', 'meu', 'minha',
    'ter', 'ser', 'estar', 'ir', 'fazer', 'poder', 'dizer', 'dar', 'ver',
    'saber', 'querer', 'já', 'só', 'bem', 'muito', 'também', 'então',
    'quando', 'onde', 'porque', 'pois', 'assim', 'aqui', 'ali', 'lá',
    'foi', 'vai', 'tem', 'são', 'está', 'era', 'pode', 'há', 'até',
    'ao', 'aos', 'à', 'às', 'pelo', 'pela', 'pelos', 'pelas', 'num',
    'numa', 'nesse', 'nessa', 'neste', 'nesta', 'nisso', 'nisto',
    'dele', 'dela', 'deles', 'delas', 'entre', 'sobre', 'todo', 'toda',
    'todos', 'todas', 'cada', 'outro', 'outra', 'outros', 'outras',
    'mesmo', 'mesma', 'mesmos', 'mesmas', 'ainda', 'depois', 'antes',
    'agora', 'sempre', 'nunca', 'coisa', 'coisas', 'gente', 'tipo',
    'aí', 'né', 'tá', 'tô', 'pra', 'pro', 'vc', 'voce', 'você',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
    'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
    'his', 'our', 'their', 'what', 'which', 'who', 'whom', 'and', 'but',
    'or', 'not', 'no', 'if', 'so', 'than', 'too', 'very', 'just',
}

# Categorias de conteúdo TikTok com suas hashtags associadas
TIKTOK_CATEGORIES = {
    'motivacao': {
        'keywords': ['motivação', 'motivacao', 'sucesso', 'foco', 'disciplina', 'objetivo',
                     'meta', 'determinação', 'força', 'coragem', 'atitude', 'mentalidade',
                     'mindset', 'superação', 'vitória', 'conquista', 'persistência',
                     'nunca desistir', 'acreditar', 'sonho', 'sonhos', 'grandeza',
                     'motivation', 'success', 'focus', 'discipline', 'hustle', 'grind'],
        'hashtags': ['#motivação', '#sucesso', '#foco', '#disciplina', '#mindset',
                     '#motivacao', '#inspiration', '#hustle', '#nevergiveup', '#goals'],
    },
    'empreendedorismo': {
        'keywords': ['empreendedor', 'negócio', 'negocio', 'empresa', 'dinheiro', 'renda',
                     'investir', 'investimento', 'lucro', 'vendas', 'marketing', 'digital',
                     'financeiro', 'riqueza', 'rico', 'milionário', 'bilionário',
                     'entrepreneur', 'business', 'money', 'wealth', 'startup'],
        'hashtags': ['#empreendedorismo', '#negocios', '#dinheiro', '#investimento',
                     '#marketingdigital', '#rendaextra', '#entrepreneur', '#business'],
    },
    'fitness': {
        'keywords': ['treino', 'exercício', 'academia', 'musculação', 'dieta', 'saúde',
                     'corpo', 'shape', 'fitness', 'workout', 'gym', 'muscle', 'bodybuilding',
                     'maromba', 'hipertrofia', 'emagrecer', 'gordura', 'proteína'],
        'hashtags': ['#fitness', '#treino', '#academia', '#workout', '#gym', '#saude',
                     '#maromba', '#bodybuilding', '#fitnessmotivation', '#lifestyle'],
    },
    'desenvolvimento_pessoal': {
        'keywords': ['hábito', 'habito', 'rotina', 'produtividade', 'leitura', 'livro',
                     'aprender', 'conhecimento', 'inteligência', 'sabedoria', 'mente',
                     'cerebro', 'cérebro', 'psicologia', 'autoconhecimento', 'evolução',
                     'crescimento', 'pessoal', 'desenvolvimento', 'stoic', 'estoicismo',
                     'self improvement', 'growth', 'habits', 'productivity', 'reading'],
        'hashtags': ['#desenvolvimentopessoal', '#autoconhecimento', '#habitos',
                     '#produtividade', '#crescimento', '#selfimprovement', '#growthmindset'],
    },
    'relacionamento': {
        'keywords': ['amor', 'relacionamento', 'namoro', 'casal', 'mulher', 'homem',
                     'masculinidade', 'feminilidade', 'sedução', 'atração', 'conquista',
                     'red pill', 'alpha', 'sigma', 'dating', 'relationship', 'love'],
        'hashtags': ['#relacionamento', '#amor', '#dating', '#masculinidade',
                     '#redpill', '#sigmamale', '#alphamale', '#lifestyle'],
    },
    'financas': {
        'keywords': ['investir', 'ações', 'cripto', 'bitcoin', 'renda', 'passiva',
                     'finanças', 'financas', 'economizar', 'poupança', 'bolsa', 'trading',
                     'trader', 'mercado', 'financeiro', 'liberdade financeira',
                     'invest', 'crypto', 'stocks', 'trading', 'financial freedom'],
        'hashtags': ['#financas', '#investimentos', '#rendapassiva', '#bitcoin',
                     '#crypto', '#trading', '#liberdadefinanceira', '#educacaofinanceira'],
    },
    'lifestyle': {
        'keywords': ['vida', 'estilo', 'luxo', 'carro', 'viagem', 'casa', 'moda',
                     'roupa', 'comida', 'dia', 'noite', 'rotina', 'manhã',
                     'lifestyle', 'luxury', 'travel', 'fashion', 'food', 'routine'],
        'hashtags': ['#lifestyle', '#luxury', '#vibes', '#aesthetic', '#dailyroutine',
                     '#viral', '#fyp', '#foryou', '#parati', '#fy'],
    },
}

# Hashtags universais do TikTok
UNIVERSAL_HASHTAGS = ['#fyp', '#foryou', '#viral', '#tiktok', '#parati', '#fy']


def _clean_text(text: str) -> str:
    """Remove caracteres especiais e normaliza o texto."""
    text = text.lower()
    text = re.sub(r'[^\w\sáàâãéèêíìîóòôõúùûçñ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _extract_keywords_tfidf(text: str, top_n: int = 20) -> list:
    """
    Extrai palavras-chave usando TF-IDF.
    
    Args:
        text: Texto para analisar
        top_n: Número de palavras-chave a retornar
    
    Returns:
        Lista de (palavra, score) ordenada por relevância
    """
    if not text or len(text.split()) < 3:
        return []
    
    # Divide o texto em "documentos" (sentenças) para melhor TF-IDF
    sentences = re.split(r'[.!?\n]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    
    if len(sentences) < 2:
        # Se há poucas sentenças, divide por palavras
        sentences = [text]
    
    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words=list(STOP_WORDS_PT),
            min_df=1,
            max_df=0.95,
            token_pattern=r'(?u)\b[a-záàâãéèêíìîóòôõúùûçñ]{3,}\b'
        )
        
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        
        # Score médio de cada palavra em todas as sentenças
        scores = tfidf_matrix.mean(axis=0).A1
        word_scores = list(zip(feature_names, scores))
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        return word_scores[:top_n]
    
    except Exception:
        # Fallback: usa contagem de frequência simples
        words = _clean_text(text).split()
        words = [w for w in words if w not in STOP_WORDS_PT and len(w) > 2]
        counter = Counter(words)
        return counter.most_common(top_n)


def _detect_categories(text: str, keywords: list) -> list:
    """
    Detecta categorias de conteúdo baseado no texto e palavras-chave.
    
    Returns:
        Lista de (categoria, score) ordenada por relevância
    """
    text_lower = text.lower()
    keyword_words = {kw[0].lower() for kw in keywords}
    
    category_scores = []
    
    for cat_name, cat_data in TIKTOK_CATEGORIES.items():
        score = 0
        for kw in cat_data['keywords']:
            kw_lower = kw.lower()
            if kw_lower in text_lower:
                score += 2
            if kw_lower in keyword_words:
                score += 3
        
        if score > 0:
            category_scores.append((cat_name, score))
    
    category_scores.sort(key=lambda x: x[1], reverse=True)
    return category_scores


def _generate_hashtags_from_keywords(keywords: list, max_hashtags: int = 8) -> list:
    """Gera hashtags a partir das palavras-chave extraídas."""
    hashtags = []
    
    for word, score in keywords:
        word_clean = re.sub(r'[^a-záàâãéèêíìîóòôõúùûçña-z0-9]', '', word.lower())
        if len(word_clean) >= 3 and word_clean not in STOP_WORDS_PT:
            tag = f"#{word_clean}"
            if tag not in hashtags:
                hashtags.append(tag)
        
        if len(hashtags) >= max_hashtags:
            break
    
    return hashtags


def _generate_description(ocr_text: str, transcription: str, keywords: list, categories: list) -> str:
    """
    Gera uma descrição envolvente para o TikTok.
    
    Usa templates baseados na categoria detectada + palavras-chave.
    """
    # Pega as top 5 palavras-chave
    top_words = [kw[0] for kw in keywords[:5]]
    
    # Determina a categoria principal
    main_category = categories[0][0] if categories else 'lifestyle'
    
    # Templates por categoria
    templates = {
        'motivacao': [
            "💪 {words} — Assista até o final! 🔥",
            "🚀 A mensagem que você precisava ouvir hoje: {words} 💯",
            "⚡ {words} — Levanta e vai! Não espere o momento perfeito 🏆",
        ],
        'empreendedorismo': [
            "💰 {words} — O segredo que ninguém te conta 📈",
            "🧠 {words} — Mentalidade de milionário 💎",
            "🔥 {words} — Transforme sua vida agora 🚀",
        ],
        'fitness': [
            "💪 {words} — Sem desculpas, só resultados! 🏋️",
            "🔥 {words} — O treino que vai mudar seu shape 💯",
            "⚡ {words} — Disciplina é liberdade 🏆",
        ],
        'desenvolvimento_pessoal': [
            "🧠 {words} — Conhecimento que transforma 📚",
            "💡 {words} — Evolua todos os dias ⬆️",
            "🎯 {words} — A mudança começa agora 🔑",
        ],
        'relacionamento': [
            "❤️ {words} — A verdade que você precisa ouvir 💯",
            "🔥 {words} — Entenda o jogo! 🎯",
            "💎 {words} — Valor próprio acima de tudo 👑",
        ],
        'financas': [
            "💰 {words} — Domine seu dinheiro 📊",
            "📈 {words} — O caminho para a liberdade financeira 🔑",
            "🧠 {words} — Inteligência financeira na prática 💎",
        ],
        'lifestyle': [
            "✨ {words} — Vibe do dia 🎬",
            "🔥 {words} — Lifestyle that hits different 💯",
            "⚡ {words} — Assista e se inspire! 🚀",
        ],
    }
    
    # Escolhe o melhor template
    category_templates = templates.get(main_category, templates['lifestyle'])
    
    # Usa o primeiro template com as palavras mais relevantes
    words_str = ", ".join(top_words[:3]).capitalize() if top_words else "Conteúdo incrível"
    
    # Seleciona template baseado no tamanho do conteúdo
    idx = min(len(transcription) % len(category_templates), len(category_templates) - 1)
    description = category_templates[idx].format(words=words_str)
    
    # Se temos transcrição, adiciona um trecho relevante
    if transcription and len(transcription) > 30:
        # Pega a primeira frase significativa da transcrição
        sentences = re.split(r'[.!?]+', transcription)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 15 and len(sent) < 100:
                description = f'"{sent}" — {description}'
                break
    
    return description


def analyze_content(ocr_texts: list, transcription_result: dict) -> dict:
    """
    Analisa o conteúdo extraído e gera hashtags + descrição.
    
    Args:
        ocr_texts: Lista de textos extraídos via OCR
        transcription_result: Dict com resultado da transcrição Whisper
    
    Returns:
        Dict com 'hashtags', 'description', 'keywords', 'categories'
    """
    # Combina todo o texto disponível
    ocr_text = " ".join(ocr_texts) if ocr_texts else ""
    transcription = transcription_result.get("text", "")
    
    combined_text = f"{ocr_text} {transcription}".strip()
    
    if not combined_text:
        console.print("  [yellow]⚠️ Nenhum texto encontrado para análise[/yellow]")
        return {
            'hashtags': UNIVERSAL_HASHTAGS[:5],
            'description': '✨ Confira esse conteúdo incrível! 🔥 #fyp #viral #tiktok',
            'keywords': [],
            'categories': [],
        }
    
    # 1. Extrai palavras-chave via TF-IDF
    cleaned_text = _clean_text(combined_text)
    keywords = _extract_keywords_tfidf(cleaned_text)
    
    # 2. Detecta categorias
    categories = _detect_categories(combined_text, keywords)
    
    # 3. Gera hashtags
    # Hashtags da categoria detectada
    category_hashtags = []
    for cat_name, score in categories[:2]:
        cat_data = TIKTOK_CATEGORIES.get(cat_name, {})
        cat_tags = cat_data.get('hashtags', [])
        category_hashtags.extend(cat_tags[:3])
    
    # Hashtags das palavras-chave
    keyword_hashtags = _generate_hashtags_from_keywords(keywords, max_hashtags=5)
    
    # Combina: categoria + keywords + universais (sem duplicatas)
    all_hashtags = []
    seen = set()
    for tag in category_hashtags + keyword_hashtags + UNIVERSAL_HASHTAGS[:3]:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            all_hashtags.append(tag)
    
    # Limita a 15 hashtags
    all_hashtags = all_hashtags[:15]
    
    # 4. Gera descrição
    description = _generate_description(ocr_text, transcription, keywords, categories)
    
    console.print(f"  🏷️ {len(all_hashtags)} hashtags geradas")
    console.print(f"  📄 Descrição gerada com sucesso")
    
    return {
        'hashtags': all_hashtags,
        'description': description,
        'keywords': [(kw, float(score)) for kw, score in keywords[:10]],
        'categories': [(cat, score) for cat, score in categories],
    }
