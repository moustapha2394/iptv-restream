# 📤 Guide de Publication sur GitHub

## 🎯 Objectif

Publier le projet sur GitHub pour pouvoir le cloner facilement depuis Proxmox.

## 📝 Étape 1 : Initialiser Git localement

Ouvrir PowerShell dans le dossier du projet :

```powershell
cd "c:\Users\mndiaye\OneDrive - PG Construction\Bureau\iptv"

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - IPTV Restream Platform v2.0"
```

## 🌐 Étape 2 : Créer un repo sur GitHub

1. Aller sur [github.com](https://github.com)
2. Se connecter à votre compte
3. Cliquer sur **"+"** en haut à droite → **"New repository"**
4. Remplir :
   - **Repository name** : `iptv-restream` (ou autre nom)
   - **Description** : `IPTV Restream Platform with FFmpeg HLS streaming and JWT auth`
   - **Visibility** : 
     - ✅ **Public** (recommandé pour faciliter le clonage)
     - ⚠️ **Private** si vous voulez garder le code privé
   - **Ne PAS cocher** "Initialize this repository with a README" (on l'a déjà)
5. Cliquer sur **"Create repository"**

## 🔗 Étape 3 : Connecter le repo local à GitHub

GitHub va afficher des instructions. Utiliser la section **"...or push an existing repository from the command line"** :

```powershell
# Ajouter l'origine GitHub (remplacer VOTRE_USERNAME et VOTRE_REPO)
git remote add origin https://github.com/VOTRE_USERNAME/iptv-restream.git

# Renommer la branche en main
git branch -M main

# Push vers GitHub
git push -u origin main
```

**Si demande d'authentification** :
- Utiliser un **Personal Access Token** (plus de mot de passe simple)
- Aller sur GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token → Cocher "repo" → Générer
- Copier le token et l'utiliser comme mot de passe

## ✅ Étape 4 : Vérifier sur GitHub

1. Rafraîchir la page de votre repo GitHub
2. Vous devriez voir tous les fichiers :
   - `backend/`
   - `frontend/`
   - `docker-compose.yml`
   - `README.md`
   - `DEPLOY_PROXMOX.md`
   - etc.

## 🚀 Étape 5 : Cloner sur Proxmox

Maintenant, depuis votre Proxmox LXC :

```bash
# Se connecter au conteneur Proxmox
pct enter 100

# Aller dans /opt
cd /opt

# Cloner le repo (remplacer VOTRE_USERNAME)
git clone https://github.com/VOTRE_USERNAME/iptv-restream.git

# Entrer dans le dossier
cd iptv-restream

# Configurer les identifiants
nano docker-compose.yml

# Lancer
docker compose up -d
```

## 🔄 Mettre à jour le code sur GitHub

Après avoir modifié le code localement :

```powershell
# Ajouter les modifications
git add .

# Commit avec message descriptif
git commit -m "Description des changements"

# Push vers GitHub
git push
```

## 📥 Mettre à jour sur Proxmox

Depuis le conteneur Proxmox :

```bash
cd /opt/iptv-restream

# Récupérer les dernières modifications
git pull

# Reconstruire et relancer
docker compose build
docker compose up -d --force-recreate
```

## 🔒 Si le repo est Private

### Sur Proxmox, utiliser un Personal Access Token

1. Sur GitHub : Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Cocher "repo"
4. Générer et copier le token

Sur Proxmox :

```bash
# Cloner avec token
git clone https://TOKEN@github.com/VOTRE_USERNAME/iptv-restream.git

# Ou configurer Git
git config --global credential.helper store
git clone https://github.com/VOTRE_USERNAME/iptv-restream.git
# Entrer username et TOKEN comme mot de passe
```

## 📋 Structure finale sur GitHub

Votre repo devrait ressembler à :

```
iptv-restream/
├── .gitignore              ✅ (exclut .venv, __pycache__, etc.)
├── README.md               ✅ (guide principal)
├── DEPLOY_PROXMOX.md       ✅ (guide de déploiement détaillé)
├── LICENSE                 ✅ (MIT License)
├── docker-compose.yml      ✅ (avec variables à configurer)
├── deploy.sh               ✅ (script Linux)
├── deploy.ps1              ✅ (script Windows)
├── backend/
│   ├── Dockerfile          ✅
│   ├── main.py             ✅
│   ├── auth.py             ✅
│   ├── requirements.txt    ✅
│   └── .dockerignore       ✅
└── frontend/
    ├── Dockerfile          ✅
    ├── manage.py           ✅
    ├── requirements.txt    ✅
    ├── .dockerignore       ✅
    └── templates/          ✅
```

## ⚠️ Fichiers à NE PAS commit

Le `.gitignore` exclut automatiquement :
- ❌ `.venv/` (environnements virtuels)
- ❌ `__pycache__/` (cache Python)
- ❌ `.env` (secrets - si vous en aviez un)
- ❌ `db.sqlite3` (base de données locale)
- ❌ `*.log` (logs)
- ❌ `backend/hls_output/*.ts` (fichiers HLS temporaires)

## 💡 Conseils

### Commit réguliers

```powershell
# Après chaque modification importante
git add .
git commit -m "Fix: Description du fix"
git push
```

### Messages de commit clairs

- ✅ `feat: Add favorites system`
- ✅ `fix: Correct FFmpeg segment deletion`
- ✅ `docs: Update README with Cloudflare setup`
- ❌ `update`
- ❌ `fix bug`

### Branches pour développement

```powershell
# Créer une branche pour tester
git checkout -b dev

# Faire des modifications
git add .
git commit -m "test: New feature"
git push -u origin dev

# Merger dans main quand c'est stable
git checkout main
git merge dev
git push
```

## 🎉 C'est fait !

Votre code est maintenant sur GitHub et peut être déployé facilement sur n'importe quel serveur Proxmox en une seule commande :

```bash
git clone https://github.com/VOTRE_USERNAME/iptv-restream.git
cd iptv-restream
nano docker-compose.yml  # Configurer identifiants
docker compose up -d
```

---

**Lien de votre repo** : `https://github.com/VOTRE_USERNAME/iptv-restream`
