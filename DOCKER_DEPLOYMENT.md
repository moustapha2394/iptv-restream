# 🐳 Guide de Déploiement Docker - IPTV Restream Platform

## 📋 Prérequis

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- Ports disponibles : 8001, 8002

## 🚀 Déploiement Rapide

### 1. Cloner ou préparer le projet

```bash
cd /path/to/iptv
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```bash
cp .env.example .env
```

Modifier les valeurs dans `.env` :

```env
# Configuration Xtream Codes
XTREAM_API_URL=http://your-xtream-server.com:port
XTREAM_USERNAME=your_username
XTREAM_PASSWORD=your_password

# JWT Secret Key (générer avec: openssl rand -hex 32)
JWT_SECRET_KEY=your-generated-secret-key

# Admin Password Hash
ADMIN_PASSWORD_HASH=$2b$12$...
```

### 3. Générer un nouveau hash de mot de passe admin (optionnel)

```bash
# Dans le backend
cd backend
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('VotreNouveauMotDePasse'))"
```

Copier le hash généré dans `.env` sous `ADMIN_PASSWORD_HASH`.

### 4. Builder les images Docker

```bash
docker-compose build
```

### 5. Lancer les conteneurs

```bash
docker-compose up -d
```

### 6. Vérifier le statut

```bash
docker-compose ps
docker-compose logs -f
```

## 🌐 Accéder à l'application

- **Frontend (Interface Admin)** : http://localhost:8001
- **Backend (API)** : http://localhost:8002
- **Documentation API** : http://localhost:8002/docs

### Identifiants par défaut

- **Username** : `admin`
- **Password** : Le mot de passe par défaut est configuré dans docker-compose.yml (changez-le en production !)

## 🛠️ Commandes utiles

### Arrêter les conteneurs

```bash
docker-compose down
```

### Redémarrer un service

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Voir les logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Supprimer tout (attention : données perdues)

```bash
docker-compose down -v
docker system prune -a
```

## 📦 Architecture

```
iptv/
├── backend/
│   ├── Dockerfile          # Image Python + FFmpeg
│   ├── main.py             # FastAPI application
│   ├── auth.py             # JWT authentication
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile          # Image Python + Django
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml      # Orchestration
├── .env                    # Variables d'environnement
└── .env.example            # Template
```

## 🔒 Sécurité en Production

### 1. Générer des secrets forts

```bash
# Secret JWT
openssl rand -hex 32

# Nouveau mot de passe admin
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('MotDePasseTresComplexe123!'))"
```

### 2. Configurer le pare-feu

```bash
# Sur Proxmox/Linux
ufw allow 8001/tcp  # Frontend
ufw allow 8002/tcp  # Backend (ou fermer si proxy inverse)
```

### 3. Utiliser un proxy inverse (Recommandé)

Exemple avec Nginx :

```nginx
# /etc/nginx/sites-available/iptv
server {
    listen 80;
    server_name restream.senbaye.me;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
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
}
```

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier FFmpeg
docker-compose exec backend ffmpeg -version
```

### Le frontend ne peut pas contacter le backend

```bash
# Vérifier la connectivité réseau
docker-compose exec frontend ping backend

# Vérifier les variables d'environnement
docker-compose exec frontend env | grep BACKEND_URL
```

### Problèmes de streaming

```bash
# Vérifier les segments HLS
docker-compose exec backend ls -lah hls_output/

# Tester l'URL Xtream
docker-compose exec backend curl -I "http://your-xtream-server.com:port"
```

## 🚀 Déploiement sur Proxmox

### 1. Créer un conteneur LXC Ubuntu 22.04

```bash
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iptv-restream \
  --memory 2048 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --rootfs 20
```

### 2. Démarrer et entrer dans le conteneur

```bash
pct start 100
pct enter 100
```

### 3. Installer Docker

```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker
```

### 4. Cloner le projet et déployer

```bash
cd /opt
git clone https://github.com/your-repo/iptv.git
cd iptv
nano .env  # Configurer les variables
docker-compose up -d
```

### 5. Configurer Cloudflare DNS

- **A Record** : `restream.senbaye.me` → IP du Proxmox
- **CNAME** : `watch.senbaye.me` → `restream.senbaye.me`

## 📊 Monitoring

### Vérifier l'utilisation des ressources

```bash
docker stats
```

### Logs en temps réel

```bash
docker-compose logs -f --tail=100
```

## 🆘 Support

- Documentation API : http://localhost:8002/docs
- Logs backend : `docker-compose logs backend`
- Logs frontend : `docker-compose logs frontend`

---

**Version** : 2.0.0 (Docker)  
**Dernière mise à jour** : 2025
