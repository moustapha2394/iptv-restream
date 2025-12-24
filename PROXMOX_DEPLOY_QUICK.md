# 🚀 Déploiement rapide sur Proxmox - IPTV Restream

## ⚡ Installation en 5 minutes

### 1️⃣ Login Docker et Git (avec ton token)

```bash
# Login Docker GHCR
echo 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 | docker login ghcr.io -u moustapha2394 --password-stdin

# Cloner le repo
cd /opt
git clone https://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@github.com/moustapha2394/iptv-restream.git
cd iptv-restream
```

### 2️⃣ Configuration

```bash
# Éditer le docker-compose.yml
nano docker-compose.yml
```

**Modifier ces 3 lignes :**
```yaml
- XTREAM_API_URL=http://TON_SERVEUR:PORT
- XTREAM_USERNAME=TON_USERNAME
- XTREAM_PASSWORD=TON_PASSWORD
```

### 3️⃣ Démarrage

```bash
# Pull et lancer
docker compose pull
docker compose up -d

# Vérifier
docker compose ps
docker compose logs -f
```

### 4️⃣ Accès

- **Frontend (interface web)** : http://IP_PROXMOX:8001
- **Backend (API)** : http://IP_PROXMOX:8002
- **Login** : admin / (voir docker-compose.yml pour le mot de passe)

---

## 🔄 Mise à jour

```bash
cd /opt/iptv-restream
docker compose pull
docker compose up -d
```

## 🛑 Arrêt/Redémarrage

```bash
# Arrêter
docker compose down

# Redémarrer
docker compose restart

# Voir les logs
docker compose logs -f backend
docker compose logs -f frontend
```

## 🔒 Sécurité - Changer le mot de passe admin

```bash
# Générer un nouveau hash (remplacer NouveauMotDePasse)
docker exec -it iptv_backend python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('NouveauMotDePasse'))"

# Copier le hash, puis éditer docker-compose.yml
nano docker-compose.yml
# Remplacer ADMIN_PASSWORD_HASH=$$2b$$12$$... par le nouveau hash
# ATTENTION : Doubler les $ dans docker-compose.yml ($$2b au lieu de $2b)

# Redémarrer
docker compose up -d --force-recreate backend
```

## 📊 Monitoring

```bash
# Ressources utilisées
docker stats

# Espace disque
df -h

# Vérifier les processus
htop
```

## 🌐 Configuration DNS (optionnel)

### Avec Cloudflare + Nginx

```bash
# Installer Nginx
apt update
apt install nginx certbot python3-certbot-nginx -y

# Créer config Nginx
nano /etc/nginx/sites-available/iptv
```

**Contenu du fichier :**
```nginx
server {
    listen 80;
    server_name restream.ton-domaine.com;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name watch.ton-domaine.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Activer et SSL :**
```bash
ln -s /etc/nginx/sites-available/iptv /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# SSL avec Let's Encrypt
certbot --nginx -d restream.ton-domaine.com -d watch.ton-domaine.com
```

## 🔧 Troubleshooting

### Port déjà utilisé
```bash
# Vérifier les ports
netstat -tlnp | grep -E '8001|8002'

# Changer les ports dans docker-compose.yml
nano docker-compose.yml
# Modifier "8001:8001" en "9001:8001" par exemple
```

### Images ne se téléchargent pas
```bash
# Re-login Docker
echo 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 | docker login ghcr.io -u moustapha2394 --password-stdin

# Vérifier le token sur GitHub
# https://github.com/settings/tokens
```

### Erreur FFmpeg
```bash
# Vérifier les logs
docker compose logs backend | grep ffmpeg

# Redémarrer le backend
docker compose restart backend
```

### Container ne démarre pas
```bash
# Voir les erreurs
docker compose logs

# Recréer les containers
docker compose down
docker compose up -d
```

## 💾 Backup

```bash
# Backup de la configuration
cp docker-compose.yml docker-compose.yml.backup

# Export des containers
docker save ghcr.io/moustapha2394/iptv-restream/backend:main -o backend.tar
docker save ghcr.io/moustapha2394/iptv-restream/frontend:main -o frontend.tar
```

## 📝 Notes importantes

- **Token GitHub** : Valable jusqu'à expiration (vérifie sur https://github.com/settings/tokens)
- **Credentials Xtream** : À configurer dans docker-compose.yml
- **Firewall** : Ouvrir les ports 8001 et 8002 si nécessaire
- **RAM recommandée** : 2 GB minimum
- **CPU recommandé** : 2 cores minimum
- **Stockage** : 10 GB minimum

## 🎯 Configuration LXC Proxmox recommandée

```bash
# Créer le LXC
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iptv-restream \
  --memory 2048 \
  --cores 2 \
  --rootfs local-lvm:10 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1

# Démarrer
pct start 100

# Entrer dans le container
pct enter 100

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Suivre les étapes 1-3 ci-dessus
```

---

**Prêt à déployer ! 🚀**
