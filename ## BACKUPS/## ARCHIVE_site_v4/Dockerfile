# Usa uma imagem oficial do Python, leve (slim)
FROM python:3.11-slim

# Instala o pngquant direto dos repositórios oficiais do Linux
RUN apt-get update && apt-get install -y pngquant && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements primeiro (para otimizar o cache do Docker)
COPY requirements.txt .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do projeto para dentro do container
COPY . .

# O Render usa a porta 10000 por padrão, então vamos expor ela
EXPOSE 10000

# Comando para iniciar o servidor em produção usando gunicorn
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --timeout 120 --workers 1 --threads 4
