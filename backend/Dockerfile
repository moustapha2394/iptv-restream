# Utilise une image officielle Python
FROM python:3.11-slim

WORKDIR /app

# Installe FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copie les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Crée le répertoire pour HLS
RUN mkdir -p hls_output

# Expose le port
EXPOSE 8002

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
