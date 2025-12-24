# 📋 Résumé du Projet IPTV Restream Platform

## ✅ Ce qui est fait

### 1. **Backend FastAPI** (Port 8002)
- ✅ API REST complète avec tous les endpoints
- ✅ Système d'authentification JWT
- ✅ Streaming HLS avec FFmpeg 8.0.1
- ✅ Gestion des catégories et chaînes Xtream
- ✅ Protection par JWT des routes admin
- ✅ Support des variables d'environnement

### 2. **Frontend Django** (Port 8001)
- ✅ Interface admin moderne avec Bootstrap 5
- ✅ Système de login/logout
- ✅ Gestion des catégories et favoris
- ✅ Player HLS intégré
- ✅ Auto-refresh des chaînes actives
- ✅ Page de visionnage publique (`/watch`)

### 3. **Authentification & Sécurité**
- ✅ JWT avec expiration 24h
- ✅ Mots de passe hashés avec bcrypt
- ✅ Routes protégées (admin) vs publiques (streaming)
- ✅ Variables d'environnement pour les secrets

### 4. **Dockerisation**
- ✅ Dockerfile backend (Python + FFmpeg)
- ✅ Dockerfile frontend (Python + Django)
- ✅ docker-compose.yml configuré
- ✅ Variables d'environnement (.env.example)
- ✅ Fichiers .dockerignore
- ✅ Scripts de déploiement (deploy.ps1 / deploy.sh)

### 5. **Documentation**
- ✅ DOCKER_DEPLOYMENT.md (guide complet)
- ✅ README avec architecture
- ✅ Guide d'utilisation
- ✅ Documentation API (FastAPI /docs)

## 🎯 Prochaines étapes

### Sur ta machine locale (Windows)

**Tu ne peux pas tester Docker localement car :**
- Docker Desktop n'est pas installé sur ta machine
- Tu peux l'installer : https://www.docker.com/products/docker-desktop/

**Mais tu peux continuer en développement :**
```powershell
# Terminal 1 : Backend
cd backend
.venv\Scripts\Activate
uvicorn main:app --reload --port 8002

# Terminal 2 : Frontend
cd frontend
.venv\Scripts\Activate
python manage.py runserver 8001
```

### Sur Proxmox (Production)

**1. Créer un conteneur LXC Ubuntu 22.04**

```bash
# Sur Proxmox Web UI ou CLI
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iptv-restream \
  --memory 2048 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --rootfs 20

pct start 100
pct enter 100
```

**2. Installer Docker dans le LXC**

```bash
apt update && apt upgrade -y
apt install -y docker.io git curl

# Vérifier Docker
docker --version
systemctl enable docker
systemctl start docker
```

**3. Cloner ou copier le projet**

Option A : Via Git (si tu as un repo)
```bash
cd /opt
git clone https://github.com/your-repo/iptv.git
cd iptv
```

Option B : Copier depuis ta machine
```powershell
# Sur ta machine Windows
scp -r "c:\Users\mndiaye\OneDrive - PG Construction\Bureau\iptv" root@IP_PROXMOX:/opt/
```

**4. Configurer les variables d'environnement**

```bash
cd /opt/iptv
cp .env.example .env
nano .env
```

Modifier :
```env
XTREAM_API_URL=http://line.dino.ws:80
XTREAM_USERNAME=8c8e6d773d
XTREAM_PASSWORD=2ff8d53b8f8c

# Générer un nouveau secret
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Générer un nouveau hash de mot de passe
# (ou garder le hash existant pour admin123)
ADMIN_PASSWORD_HASH=$2b$12$Swx6tdNWLUJ8Q9yec8TnceVbeCrp7JP.bpbhZSXjagS8zt1Bhupyi
```

**5. Lancer le déploiement**

```bash
chmod +x deploy.sh
./deploy.sh
```

Ou manuellement :
```bash
docker compose build
docker compose up -d
```

**6. Vérifier le fonctionnement**

```bash
# Voir les conteneurs
docker compose ps

# Voir les logs
docker compose logs -f

# Tester l'API
curl http://localhost:8002/
curl http://localhost:8001/
```

**7. Configurer Cloudflare**

Sur cloudflare.com :
- Ajouter un enregistrement A : `restream.senbaye.me` → IP_PROXMOX
- Ajouter un enregistrement CNAME : `watch.senbaye.me` → `restream.senbaye.me`

**8. Configurer un proxy inverse (optionnel mais recommandé)**

Installer Nginx dans le LXC :
```bash
apt install -y nginx

# Créer la config
nano /etc/nginx/sites-available/iptv
```

Contenu :
```nginx
server {
    listen 80;
    server_name restream.senbaye.me;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

server {
    listen 80;
    server_name watch.senbaye.me;

    location / {
        proxy_pass http://localhost:8001/watch;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /hls/ {
        proxy_pass http://localhost:8002/hls/;
        proxy_buffering off;
    }

    location /internal_stream.m3u8 {
        proxy_pass http://localhost:8002/internal_stream.m3u8;
        proxy_buffering off;
    }
}
```

Activer :
```bash
ln -s /etc/nginx/sites-available/iptv /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**9. Configurer SSL avec Certbot (optionnel)**

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d restream.senbaye.me -d watch.senbaye.me
```

## 📊 Architecture finale

```
Internet
    ↓
Cloudflare DNS (restream.senbaye.me, watch.senbaye.me)
    ↓
Proxmox LXC (IP publique)
    ↓
Nginx (80/443) ← Proxy inverse
    ↓
    ├─→ Frontend (localhost:8001) - Interface admin
    └─→ Backend (localhost:8002) - API + Streaming FFmpeg
            ↓
        Xtream Codes API (line.dino.ws:80)
```

## 🔐 Identifiants par défaut

- **Admin Panel** : `admin` / `admin123`
- **À changer en production** via la variable `ADMIN_PASSWORD_HASH`

## 📝 Fichiers importants

```
iptv/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── auth.py              # Authentification JWT
│   ├── Dockerfile           # Image Docker backend
│   └── requirements.txt
├── frontend/
│   ├── manage.py            # Django
│   ├── Dockerfile           # Image Docker frontend
│   └── requirements.txt
├── docker-compose.yml       # Orchestration
├── .env.example             # Template variables
├── deploy.sh                # Script déploiement Linux
├── deploy.ps1               # Script déploiement Windows
├── DOCKER_DEPLOYMENT.md     # Guide Docker complet
└── SUMMARY.md               # Ce fichier
```

## 🆘 Dépannage

### Problème : Les conteneurs ne démarrent pas
```bash
docker compose logs backend
docker compose logs frontend
```

### Problème : FFmpeg ne fonctionne pas
```bash
docker compose exec backend ffmpeg -version
docker compose exec backend ls -lah hls_output/
```

### Problème : Frontend ne peut pas contacter backend
```bash
docker compose exec frontend ping backend
docker compose exec frontend env | grep BACKEND_URL
```

### Problème : Erreur d'authentification
- Vérifier le hash du mot de passe dans `.env`
- Tester le login avec admin/admin123
- Vérifier les logs : `docker compose logs backend | grep JWT`

## ✅ Checklist finale

- [ ] Docker installé sur Proxmox LXC
- [ ] Projet copié dans `/opt/iptv`
- [ ] Fichier `.env` configuré avec tes identifiants Xtream
- [ ] Images Docker buildées : `docker compose build`
- [ ] Conteneurs lancés : `docker compose up -d`
- [ ] Services accessibles : http://IP_PROXMOX:8001 et :8002
- [ ] DNS Cloudflare configuré
- [ ] Nginx configuré (optionnel)
- [ ] SSL Certbot configuré (optionnel)
- [ ] Mot de passe admin changé (production)

## 🎉 Résultat attendu

Une fois tout déployé, tu auras :

1. **Interface admin** : https://restream.senbaye.me
   - Login avec admin/ton_mot_de_passe
   - Choix de la chaîne à diffuser
   - Génération de liens de streaming

2. **Page de visionnage** : https://watch.senbaye.me
   - URL à partager (pas de login requis)
   - Lecteur vidéo HLS intégré
   - Auto-refresh quand tu changes de chaîne

---

**Prêt pour le déploiement sur Proxmox !** 🚀
