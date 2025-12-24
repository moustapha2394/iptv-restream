# 🔒 Déploiement avec Repo GitHub Privé

## 🎯 Méthodes pour utiliser un repo privé

### ✅ Méthode 1 : Cloner puis Docker Compose (Recommandé)

C'est la méthode la plus simple et fiable :

```bash
# 1. Générer un Personal Access Token sur GitHub
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# → Generate new token → Cocher "repo" → Generate

# 2. Sur Proxmox, cloner avec le token
cd /opt
git clone https://TOKEN@github.com/VOTRE_USERNAME/iptv-restream.git

# 3. Configurer Git pour stocker les credentials
cd iptv-restream
git config --global credential.helper store

# 4. Configurer et lancer
nano docker-compose.yml
docker compose up -d
```

**Avantages** :
- ✅ Fonctionne à 100%
- ✅ Facile à mettre à jour (`git pull`)
- ✅ Pas besoin de modifier docker-compose.yml

### 🔧 Méthode 2 : Build directement depuis GitHub

Utiliser `docker-compose.github.yml` avec token intégré :

```bash
# 1. Récupérer juste le docker-compose.yml
cd /opt
curl -H "Authorization: token TOKEN" \
  -o docker-compose.yml \
  https://raw.githubusercontent.com/VOTRE_USERNAME/iptv-restream/main/docker-compose.github.yml

# 2. Éditer pour ajouter votre token
nano docker-compose.yml
# Décommenter les lignes avec TOKEN et remplacer TOKEN par votre vrai token

# 3. Lancer
docker compose up -d
```

**Avantages** :
- ✅ Pas besoin de cloner tout le repo
- ✅ Docker pull directement depuis GitHub

**Inconvénients** :
- ⚠️ Token visible dans docker-compose.yml
- ⚠️ Plus complexe pour les mises à jour

### 🐳 Méthode 3 : Utiliser GitHub Container Registry (GHCR)

Créer des images Docker sur GitHub et les pull :

#### Étape 1 : Créer `.github/workflows/docker-publish.yml` dans votre repo

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (backend)
        id: meta-backend
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend

      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}

      - name: Extract metadata (frontend)
        id: meta-frontend
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend

      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
```

#### Étape 2 : Créer `docker-compose.ghcr.yml`

```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/VOTRE_USERNAME/iptv-restream/backend:main
    container_name: iptv_backend
    ports:
      - "8002:8002"
    environment:
      - XTREAM_API_URL=http://line.dino.ws:80
      - XTREAM_USERNAME=8c8e6d773d
      - XTREAM_PASSWORD=2ff8d53b8f8c
      - JWT_SECRET_KEY=votre-secret-key
      - ADMIN_PASSWORD_HASH=$$2b$$12$$...
    restart: unless-stopped
    networks:
      - iptv_network

  frontend:
    image: ghcr.io/VOTRE_USERNAME/iptv-restream/frontend:main
    container_name: iptv_frontend
    ports:
      - "8001:8001"
    environment:
      - BACKEND_URL=http://backend:8002
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - iptv_network

networks:
  iptv_network:
    driver: bridge
```

#### Étape 3 : Déployer sur Proxmox

```bash
# 1. Login au GitHub Container Registry
echo TOKEN | docker login ghcr.io -u VOTRE_USERNAME --password-stdin

# 2. Récupérer le docker-compose.yml
cd /opt
curl -o docker-compose.yml https://raw.githubusercontent.com/VOTRE_USERNAME/iptv-restream/main/docker-compose.ghcr.yml

# 3. Éditer et lancer
nano docker-compose.yml
docker compose pull
docker compose up -d
```

**Avantages** :
- ✅ Images pré-buildées (déploiement ultra-rapide)
- ✅ Pas besoin de builder sur Proxmox
- ✅ Idéal pour production

## 🔑 Créer un Personal Access Token GitHub

1. Aller sur GitHub → Settings
2. Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Donner un nom : `Proxmox IPTV Deployment`
5. Cocher les permissions :
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:packages` (si vous utilisez GHCR)
   - ✅ `write:packages` (si vous pushez des images)
6. Generate token
7. **Copier le token** (vous ne le reverrez plus !)

## 📋 Comparaison des méthodes

| Méthode | Difficulté | Sécurité | Rapidité | Mise à jour |
|---------|-----------|----------|----------|-------------|
| **Clone + Build** | ⭐ Facile | ⭐⭐⭐ Bonne | ⭐⭐ Moyenne | ⭐⭐⭐ `git pull` |
| **Build depuis GitHub** | ⭐⭐ Moyenne | ⭐⭐ Token exposé | ⭐⭐ Moyenne | ⭐ Complexe |
| **GHCR Images** | ⭐⭐⭐ Avancé | ⭐⭐⭐ Excellente | ⭐⭐⭐ Rapide | ⭐⭐⭐ `docker pull` |

## 🎯 Recommandation

Pour ton cas (déploiement unique sur Proxmox) :

**👉 Utilise la Méthode 1 : Clone + Build**

```bash
# Configuration initiale (une seule fois)
cd /opt
git clone https://TOKEN@github.com/VOTRE_USERNAME/iptv-restream.git
cd iptv-restream
git config credential.helper store
nano docker-compose.yml
docker compose up -d

# Mise à jour (quand tu modifies le code)
cd /opt/iptv-restream
git pull
docker compose build
docker compose up -d --force-recreate
```

C'est la méthode la plus simple et fiable ! 🚀

## 🔒 Sécurité des tokens

### Ne jamais commiter un token dans le repo !

Si tu utilises des tokens dans docker-compose.yml :

```bash
# Ajouter au .gitignore
echo "docker-compose.override.yml" >> .gitignore

# Créer un fichier override avec les secrets
nano docker-compose.override.yml
```

### Utiliser des secrets Docker (Production)

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    environment:
      - XTREAM_API_URL
      - XTREAM_USERNAME
      - XTREAM_PASSWORD
    env_file:
      - .env.secrets  # Ne jamais commiter ce fichier !
```

```bash
# .env.secrets (ne jamais push sur GitHub !)
XTREAM_API_URL=http://real-server:port
XTREAM_USERNAME=real_username
XTREAM_PASSWORD=real_password
```

---

**Besoin d'aide ?** Choisis la Méthode 1 pour commencer ! 🎉
