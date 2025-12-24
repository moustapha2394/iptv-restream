# 🚀 Guide de Déploiement sur Proxmox

## 📋 Prérequis

- Proxmox VE installé
- Accès SSH au serveur Proxmox
- Template Ubuntu 22.04 LXC disponible

## 🔧 Étape 1 : Créer le conteneur LXC

### Via l'interface Web Proxmox

1. Cliquer sur **Create CT**
2. Configurer :
   - **Hostname** : `iptv-restream`
   - **Template** : Ubuntu 22.04
   - **RAM** : 2048 MB
   - **CPU** : 2 cores
   - **Disk** : 20 GB
   - **Network** : Bridge (avec DHCP ou IP fixe)
3. Démarrer le conteneur

### Via CLI Proxmox

```bash
# Se connecter à Proxmox en SSH
ssh root@IP_PROXMOX

# Créer le conteneur (ajuster l'ID si 100 est utilisé)
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iptv-restream \
  --memory 2048 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --rootfs 20 \
  --unprivileged 1

# Démarrer le conteneur
pct start 100

# Entrer dans le conteneur
pct enter 100
```

## 🐳 Étape 2 : Installer Docker dans le LXC

```bash
# Mise à jour du système
apt update && apt upgrade -y

# Installer les paquets nécessaires
apt install -y docker.io git curl nano

# Activer et démarrer Docker
systemctl enable docker
systemctl start docker

# Vérifier l'installation
docker --version
docker compose version
```

## 📦 Étape 3 : Cloner le projet

```bash
# Aller dans /opt
cd /opt

# Cloner depuis GitHub
git clone https://github.com/VOTRE_USERNAME/iptv-restream.git

# Entrer dans le dossier
cd iptv-restream

# Vérifier les fichiers
ls -la
```

## ⚙️ Étape 4 : Configurer vos identifiants

```bash
# Éditer le docker-compose.yml
nano docker-compose.yml
```

**Modifier ces lignes** dans la section `backend -> environment` :

```yaml
# Configuration Xtream Codes - À MODIFIER AVEC TES IDENTIFIANTS
- XTREAM_API_URL=http://VOTRE_SERVEUR:PORT
- XTREAM_USERNAME=votre_username
- XTREAM_PASSWORD=votre_password
```

**Optionnel** : Changer le mot de passe admin

```bash
# Générer un nouveau hash
docker run --rm -it python:3.11-slim bash -c \
  "pip install passlib[bcrypt]==1.7.4 bcrypt==4.0.1 && python -c \"from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('VotreNouveauMotDePasse'))\""

# Copier le hash et le mettre dans docker-compose.yml
# IMPORTANT: Doubler les $ (exemple: $2b$12$xxx devient $$2b$$12$$xxx)
```

Sauvegarder avec `Ctrl+O`, `Enter`, puis quitter avec `Ctrl+X`.

## 🚀 Étape 5 : Lancer l'application

```bash
# Option 1: Utiliser le script de déploiement
chmod +x deploy.sh
./deploy.sh

# Option 2: Manuellement
docker compose build
docker compose up -d
```

## ✅ Étape 6 : Vérifier le déploiement

```bash
# Voir l'état des conteneurs
docker compose ps

# Voir les logs en temps réel
docker compose logs -f

# Vérifier que les ports sont ouverts
ss -tlnp | grep -E '8001|8002'

# Tester l'API backend
curl http://localhost:8002/

# Tester le frontend
curl http://localhost:8001/
```

## 🌐 Étape 7 : Accéder depuis l'extérieur

### Récupérer l'IP du conteneur

```bash
# Dans Proxmox
pct exec 100 -- ip addr show eth0 | grep inet

# Ou dans le conteneur
hostname -I
```

### Tester depuis votre navigateur

```
http://IP_CONTAINER:8001        # Interface admin
http://IP_CONTAINER:8001/login  # Page de connexion
http://IP_CONTAINER:8002/docs   # Documentation API
```

**Identifiants par défaut** : `admin` / `admin123`

## 🔐 Étape 8 : Configuration Cloudflare (Optionnel)

### 8.1 Configurer les DNS

Sur [cloudflare.com](https://dash.cloudflare.com) :

1. **Enregistrement A** :
   - Type : `A`
   - Name : `restream` (ou `@` pour domaine racine)
   - IPv4 : `IP_DE_VOTRE_PROXMOX`
   - Proxy status : ☁️ Proxied (recommandé)

2. **Enregistrement CNAME** :
   - Type : `CNAME`
   - Name : `watch`
   - Target : `restream.votredomaine.com`
   - Proxy status : ☁️ Proxied

### 8.2 Installer Nginx comme reverse proxy

```bash
# Dans le conteneur LXC
apt install -y nginx

# Créer la configuration
nano /etc/nginx/sites-available/iptv
```

**Contenu** :

```nginx
server {
    listen 80;
    server_name restream.votredomaine.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name watch.votredomaine.com;

    location / {
        proxy_pass http://localhost:8001/watch;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /hls/ {
        proxy_pass http://localhost:8002/hls/;
        proxy_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    location /internal_stream.m3u8 {
        proxy_pass http://localhost:8002/internal_stream.m3u8;
        proxy_buffering off;
    }

    location /stream_status {
        proxy_pass http://localhost:8002/stream_status;
    }
}
```

**Activer et tester** :

```bash
# Activer le site
ln -s /etc/nginx/sites-available/iptv /etc/nginx/sites-enabled/

# Tester la configuration
nginx -t

# Recharger Nginx
systemctl reload nginx
```

### 8.3 SSL avec Let's Encrypt (si pas de proxy Cloudflare)

```bash
# Installer Certbot
apt install -y certbot python3-certbot-nginx

# Obtenir les certificats SSL
certbot --nginx -d restream.votredomaine.com -d watch.votredomaine.com

# Le renouvellement automatique est configuré via systemd
```

## 🔄 Étape 9 : Automatiser le démarrage

```bash
# Créer un service systemd pour auto-start
nano /etc/systemd/system/iptv-restream.service
```

**Contenu** :

```ini
[Unit]
Description=IPTV Restream Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/iptv-restream
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Activer** :

```bash
systemctl daemon-reload
systemctl enable iptv-restream.service
systemctl start iptv-restream.service

# Vérifier
systemctl status iptv-restream.service
```

## 🛠️ Maintenance

### Mettre à jour le code

```bash
cd /opt/iptv-restream
git pull
docker compose build
docker compose up -d --force-recreate
```

### Voir les logs

```bash
# Tous les services
docker compose logs -f

# Backend uniquement
docker compose logs -f backend

# Frontend uniquement
docker compose logs -f frontend

# Dernières 100 lignes
docker compose logs --tail=100
```

### Redémarrer les services

```bash
# Tout redémarrer
docker compose restart

# Un service spécifique
docker compose restart backend
docker compose restart frontend
```

### Sauvegarder la configuration

```bash
# Sauvegarder docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup

# Ou via snapshot Proxmox
# Dans Proxmox Web UI : Conteneur → Backup → Backup now
```

## 🐛 Dépannage courant

### Problème : Les conteneurs ne démarrent pas

```bash
# Voir les erreurs détaillées
docker compose logs

# Vérifier les images
docker images

# Reconstruire
docker compose build --no-cache
docker compose up -d
```

### Problème : Pas d'accès depuis l'extérieur

```bash
# Vérifier le firewall (si activé)
ufw status
ufw allow 8001/tcp
ufw allow 8002/tcp

# Vérifier les ports
ss -tlnp | grep -E '8001|8002'

# Vérifier la connectivité réseau
ping -c 3 8.8.8.8
```

### Problème : FFmpeg ne fonctionne pas

```bash
# Entrer dans le conteneur backend
docker compose exec backend bash

# Vérifier FFmpeg
ffmpeg -version

# Vérifier les segments HLS
ls -lah /app/hls_output/
```

### Problème : Erreur d'authentification

```bash
# Vérifier les variables d'environnement
docker compose exec backend env | grep -E 'ADMIN|JWT'

# Tester le login via curl
curl -X POST http://localhost:8002/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## 📊 Monitoring

### Utilisation des ressources

```bash
# Stats en temps réel
docker stats

# Utilisation disque
du -sh /opt/iptv-restream
df -h
```

### Vérifier la santé

```bash
# Backend
curl http://localhost:8002/

# Frontend
curl http://localhost:8001/

# Status du stream
curl http://localhost:8002/stream_status
```

---

## 🎉 Félicitations !

Votre plateforme IPTV Restream est maintenant déployée et accessible :

- 🌐 **Interface Admin** : https://restream.votredomaine.com
- 📺 **Page de visionnage** : https://watch.votredomaine.com

**Identifiants** : `admin` / `admin123` (à changer en production)

---

**Besoin d'aide ?** Ouvrez une issue sur GitHub !
