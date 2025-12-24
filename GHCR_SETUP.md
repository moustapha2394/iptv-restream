# 🐳 GitHub Container Registry (GHCR) - Guide Complet

Ce guide explique comment utiliser les images Docker depuis GitHub Container Registry pour un déploiement ultra-rapide.

## 🎯 Avantages des images GHCR

✅ **Déploiement instantané** : Pas besoin de builder sur Proxmox  
✅ **Automatique** : Chaque push sur GitHub build les images  
✅ **Rapide** : Pull en quelques secondes au lieu de minutes de build  
✅ **Fiable** : Images testées et validées  
✅ **Économie ressources** : Pas de build sur le serveur  

## 📋 Configuration initiale (une seule fois)

### Étape 1 : Push le projet sur GitHub

```powershell
# Sur Windows
cd "c:\Users\mndiaye\OneDrive - PG Construction\Bureau\iptv"
git init
git add .
git commit -m "Initial commit - IPTV Restream Platform with Docker images"

# Créer le repo sur github.com puis :
git remote add origin https://github.com/VOTRE_USERNAME/iptv-restream.git
git branch -M main
git push -u origin main
```

### Étape 2 : GitHub Actions build automatiquement

Après le push, GitHub Actions va :
1. Détecter le workflow `.github/workflows/docker-publish.yml`
2. Builder les 2 images Docker (backend + frontend)
3. Les publier sur GitHub Container Registry

Tu peux suivre le build sur : `https://github.com/VOTRE_USERNAME/iptv-restream/actions`

### Étape 3 : Rendre les images publiques (optionnel)

Pour que tout le monde puisse pull sans login :

1. Va sur `https://github.com/VOTRE_USERNAME?tab=packages`
2. Clique sur `iptv-restream-backend`
3. **Package settings** (en bas à droite)
4. **Change visibility** → **Public**
5. Répète pour `iptv-restream-frontend`

**Note** : Si tu gardes les images privées, tu devras login avec un token sur Proxmox.

## 🚀 Déploiement sur Proxmox

### Option A : Images publiques (pas de login)

```bash
# 1. Créer le dossier
cd /opt
mkdir iptv-restream
cd iptv-restream

# 2. Télécharger juste le docker-compose.yml
curl -o docker-compose.yml \
  https://raw.githubusercontent.com/VOTRE_USERNAME/iptv-restream/main/docker-compose.yml

# 3. Éditer pour mettre ton username GitHub
nano docker-compose.yml
# Remplacer VOTRE_USERNAME par ton vrai username GitHub

# 4. Éditer les credentials Xtream
# Modifier XTREAM_API_URL, XTREAM_USERNAME, XTREAM_PASSWORD

# 5. Pull et lancer
docker compose pull
docker compose up -d
```

### Option B : Images privées (avec token)

```bash
# 1. Créer un Personal Access Token
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# → Generate new token → Cocher "read:packages" → Generate

# 2. Login sur Proxmox
echo VOTRE_TOKEN | docker login ghcr.io -u VOTRE_USERNAME --password-stdin

# 3. Créer le dossier et télécharger
cd /opt
mkdir iptv-restream
cd iptv-restream
curl -H "Authorization: token VOTRE_TOKEN" \
  -o docker-compose.yml \
  https://raw.githubusercontent.com/VOTRE_USERNAME/iptv-restream/main/docker-compose.yml

# 4. Éditer docker-compose.yml
nano docker-compose.yml
# Remplacer VOTRE_USERNAME par ton username GitHub
# Modifier XTREAM_API_URL, XTREAM_USERNAME, XTREAM_PASSWORD

# 5. Pull et lancer
docker compose pull
docker compose up -d
```

## 🔄 Mise à jour du système

Quand tu modifies le code et push sur GitHub :

```bash
# Sur Proxmox
cd /opt/iptv-restream
docker compose pull    # Pull les nouvelles images
docker compose up -d   # Redémarre avec les nouvelles images
```

C'est tout ! Pas besoin de rebuild, de git pull, etc.

## 🏷️ Tags disponibles

Les images sont buildées avec plusieurs tags :

- `main` : Dernière version de la branche main (recommandé)
- `latest` : Alias de main
- `sha-XXXXXX` : Version spécifique par commit

Exemples :
```yaml
# Toujours la dernière version
image: ghcr.io/VOTRE_USERNAME/iptv-restream/backend:main

# Version spécifique (si besoin de rollback)
image: ghcr.io/VOTRE_USERNAME/iptv-restream/backend:sha-a1b2c3d
```

## 📦 Structure des images

Après le premier push, tu auras :

```
https://github.com/VOTRE_USERNAME/iptv-restream
├── Code (repo principal)
└── Packages (GHCR)
    ├── iptv-restream/backend:main
    └── iptv-restream/frontend:main
```

Voir tes packages : `https://github.com/VOTRE_USERNAME?tab=packages`

## 🛠️ Développement local vs Production

### Développement (sur Windows)

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend  # Build local
```

```powershell
docker compose up -d --build
```

### Production (sur Proxmox)

```yaml
# docker-compose.yml
services:
  backend:
    image: ghcr.io/VOTRE_USERNAME/iptv-restream/backend:main  # Pull depuis GHCR
```

```bash
docker compose pull && docker compose up -d
```

## 🔍 Vérifier les images

```bash
# Lister les images locales
docker images | grep iptv

# Voir les détails d'une image
docker image inspect ghcr.io/VOTRE_USERNAME/iptv-restream/backend:main

# Voir les logs du build sur GitHub
# https://github.com/VOTRE_USERNAME/iptv-restream/actions
```

## 🚨 Troubleshooting

### Erreur : "authentication required"

```bash
# Login au registry
echo VOTRE_TOKEN | docker login ghcr.io -u VOTRE_USERNAME --password-stdin
```

### Erreur : "manifest unknown"

L'image n'existe pas encore. Vérifie :
1. GitHub Actions a bien buildé : `https://github.com/VOTRE_USERNAME/iptv-restream/actions`
2. Le nom de l'image est correct dans docker-compose.yml
3. Le tag existe (main, latest, sha-xxx)

### Les changements ne sont pas appliqués

```bash
# Forcer le pull des nouvelles images
docker compose pull
docker compose up -d --force-recreate
```

### Build GitHub Actions échoue

Vérifie les logs : `https://github.com/VOTRE_USERNAME/iptv-restream/actions`

Causes fréquentes :
- Dockerfile mal configuré
- Dépendances manquantes
- Syntaxe workflow invalide

## 📊 Taille des images

Après build sur GHCR :
- Backend : ~800 MB (Python + FFmpeg)
- Frontend : ~400 MB (Python + Django)

Premier pull : ~1.2 GB  
Pull suivants : Quelques MB (layers en cache)

## 🎯 Workflow complet

```
┌─────────────┐
│   Windows   │  git push
│ Développeur │ ────────► GitHub
└─────────────┘
                    │
                    ├─► GitHub Actions
                    │   • Build backend
                    │   • Build frontend
                    │   • Push vers GHCR
                    │
                    ▼
              ┌──────────┐
              │   GHCR   │
              │  Images  │
              └──────────┘
                    │
                    │ docker compose pull
                    ▼
              ┌──────────┐
              │ Proxmox  │
              │   LXC    │
              └──────────┘
```

## 🔐 Sécurité

### Images publiques
- ✅ Accessibles sans authentification
- ⚠️ Visible par tout le monde
- 🎯 Idéal pour : Open source, partage facile

### Images privées
- ✅ Accessibles uniquement avec token
- ✅ Contrôle d'accès complet
- 🎯 Idéal pour : Production, propriétaire

**Important** : Les credentials Xtream sont dans docker-compose.yml, pas dans les images !

## 📈 Avantages pour Proxmox

| Méthode | Build time | Pull time | Espace | CPU |
|---------|-----------|-----------|--------|-----|
| **Build local** | ~5-10 min | - | ~2 GB | 100% |
| **GHCR pull** | - | ~30 sec | ~1.2 GB | 5% |

Avec GHCR, ton LXC Proxmox peut avoir :
- 2 GB RAM (au lieu de 4 GB pour build)
- 10 GB disque (au lieu de 20 GB)
- Déploiement en 30 secondes

## 🎉 Prêt pour la production !

Tu peux maintenant :
1. Push ton code sur GitHub
2. GitHub build automatiquement les images
3. Pull en 30 secondes sur Proxmox
4. Mises à jour instantanées

**Workflow final** :
```bash
# Windows : Développement
git add .
git commit -m "Nouvelle feature"
git push

# GitHub : Build automatique (2-3 min)

# Proxmox : Mise à jour
docker compose pull && docker compose up -d
```

C'est le workflow le plus professionnel et rapide ! 🚀
