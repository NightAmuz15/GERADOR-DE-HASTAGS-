#!/bin/bash

# Script de inicialização do Video Analyzer

# Define cores
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}==============================================${NC}"
echo -e "${CYAN}   🎬 TIKTOK VIDEO ANALYZER - INICIANDO   ${NC}"
echo -e "${CYAN}==============================================${NC}\n"

# Verifica python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    exit 1
fi

# Navega para o diretório
cd "$(dirname "$0")"

# Executa o analisador
echo -e "${GREEN}▶️ Iniciando análise...${NC}\n"
python3 analisar.py "$@"

# Mantém a janela aberta se houver erro
if [ $? -ne 0 ]; then
    echo -e "\n⚠️ Pressione ENTER para sair..."
    read
fi
