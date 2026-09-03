#!/bin/bash

# Pega a pasta atual onde o script está salvo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "Iniciando o Compressor de PNG..."
echo "=========================================="

# Ativa o ambiente virtual
source venv/bin/activate

# Abre o navegador padrão no endereço do app (damos um segundinho pro servidor ligar)
echo "Abrindo o navegador..."
sleep 1
open http://localhost:5001 &

# Roda o servidor Python
echo "Servidor rodando! Para desligar, basta fechar esta janela ou apertar CTRL+C."
python app.py
