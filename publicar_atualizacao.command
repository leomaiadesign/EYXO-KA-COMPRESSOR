#!/bin/bash

# Pega a pasta atual onde o script está salvo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "Subindo o App para o GitHub / Render..."
echo "=========================================="

# 1. Adiciona todas as modificações
git add .

# 2. Registra a atualização com a hora atual
DATA=$(date +"%d/%m/%Y %H:%M")
git commit -m "Atualização - $DATA"

# Pequena pausa para o Google Drive não bloquear o arquivo
sleep 3

# 3. Envia para o GitHub (Sem --force agora, pois já corrigimos o repositório)
git push origin main

echo "=========================================="
echo "✅ SUCESSO! O código foi para o GitHub."
echo "O Render já deve estar atualizando o site."
echo "=========================================="
echo ""
echo "Você pode fechar esta janela."
