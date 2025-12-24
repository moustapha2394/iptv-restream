# Utilise une image officielle Python
FROM python:3.11-slim

WORKDIR /app

# Copie les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Applique les migrations Django
RUN python manage.py migrate --noinput || true

# Collecte les fichiers statiques Django
RUN python manage.py collectstatic --noinput || true

# Expose le port
EXPOSE 8001

# Commande de démarrage
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
