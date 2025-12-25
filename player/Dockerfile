FROM python:3.11-slim

WORKDIR /app

# Installer Django
RUN pip install --no-cache-dir Django==5.2

# Copier les fichiers
COPY . .

# Créer les migrations
RUN python manage.py migrate --noinput || true

# Expose le port
EXPOSE 8003

# Commande de démarrage
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]
