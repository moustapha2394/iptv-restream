# 📺 IPTV Restream Platform

Plateforme de restream IPTV avec interface web moderne, streaming HLS via FFmpeg, et authentification JWT.

## 🚀 Déploiement rapide

### Sur Proxmox LXC

```bash
# 1. Créer un conteneur Ubuntu 22.04
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname iptv-restream \
  --memory 2048 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --rootfs 20

pct start 100
pct enter 100

# 2. Installer Docker
apt update && apt upgrade -y
apt install -y docker.io git
systemctl enable docker
systemctl start docker

# 3. Cloner le projet
cd /opt
git clone https://github.com/VOTRE_USERNAME/iptv-restream.git
cd iptv-restream

# 4. Configurer vos identifiants
nano docker-compose.yml
# Modifier les lignes XTREAM_API_URL, XTREAM_USERNAME, XTREAM_PASSWORD

# 5. Lancer
docker compose up -d

# 6. Vérifier
docker compose logs -f
```

## 📋 Configuration

Éditer le fichier `docker-compose.yml` et modifier ces variables :

```yaml
environment:
  # VOS IDENTIFIANTS XTREAM CODES
  - XTREAM_API_URL=http://votre-serveur:port
  - XTREAM_USERNAME=votre_username
  - XTREAM_PASSWORD=votre_password
  
  # Optionnel: Changer le mot de passe admin
  - ADMIN_PASSWORD_HASH=$$2b$$12$$...
```

### Changer le mot de passe admin

Par défaut : Configuré dans `docker-compose.yml` (le hash bcrypt correspond à un mot de passe que vous devez changer)

Pour changer :

```bash
# Dans le conteneur backend
docker compose exec backend python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('VotreNouveauMotDePasse'))"

# Copier le hash dans docker-compose.yml (doubler les $)
# Exemple: $2b$12$xxx devient $$2b$$12$$xxx
```

## 🌐 Accès

- **Interface Admin** : `http://localhost:8001` ou `http://IP:8001`
- **API Backend** : `http://localhost:8002` ou `http://IP:8002`
- **API Docs** : `http://localhost:8002/docs`

## 🎯 Fonctionnalités

- ✅ Interface web moderne (Bootstrap 5)
- ✅ Authentification JWT sécurisée
- ✅ Streaming HLS avec FFmpeg
- ✅ Gestion des catégories et chaînes Xtream
- ✅ Système de favoris (localStorage)
- ✅ Page de visionnage publique (`/watch`)
- ✅ Auto-refresh du player
- ✅ Recherche en temps réel
- ✅ Génération de liens de streaming

## 📂 Structure

```
iptv-restream/
├── backend/              # FastAPI + FFmpeg
│   ├── main.py          # API REST
│   ├── auth.py          # Authentification JWT
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Django + Bootstrap
│   ├── templates/       # Pages web
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml   # Configuration Docker
└── deploy.sh           # Script de déploiement
```

## 🔧 Commandes utiles

```bash
# Démarrer
docker compose up -d

# Arrêter
docker compose down

# Voir les logs
docker compose logs -f

# Redémarrer un service
docker compose restart backend
docker compose restart frontend

# Reconstruire les images
docker compose build
docker compose up -d --force-recreate
```

## 🌍 Configuration DNS Cloudflare

1. Ajouter un enregistrement A : `restream.votredomaine.com` → IP_PROXMOX
2. Ajouter un CNAME : `watch.votredomaine.com` → `restream.votredomaine.com`

### Nginx Reverse Proxy (Optionnel)

```bash
apt install -y nginx certbot python3-certbot-nginx

nano /etc/nginx/sites-available/iptv
```

```nginx
server {
    listen 80;
    server_name restream.votredomaine.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
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
    }

    location /internal_stream.m3u8 {
        proxy_pass http://localhost:8002/internal_stream.m3u8;
        proxy_buffering off;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/iptv /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# SSL avec Let's Encrypt
certbot --nginx -d restream.votredomaine.com -d watch.votredomaine.com
```

## 🐛 Dépannage

### Les conteneurs ne démarrent pas
```bash
docker compose logs backend
docker compose logs frontend
```

### FFmpeg ne fonctionne pas
```bash
docker compose exec backend ffmpeg -version
docker compose exec backend ls -lah hls_output/
```

### Problème de connexion backend/frontend
```bash
docker compose exec frontend ping backend
```

## 📦 Technologies

- **Backend** : FastAPI 2.0, Python 3.11, FFmpeg 8.0
- **Frontend** : Django 5.2, Bootstrap 5.3
- **Auth** : JWT (python-jose), bcrypt
- **Streaming** : HLS (HTTP Live Streaming)
- **Container** : Docker, Docker Compose

## 📄 Licence

MIT License - Libre d'utilisation

## 🙏 Support

Pour toute question ou problème, ouvrir une issue sur GitHub.

---

**Déployé avec ❤️ sur Proxmox**
   - Stockage : 20 Go
   - Réseau : Bridge (accès internet requis)

2. Démarrer et se connecter au container :
   ```bash
   pct start <container_id>
   pct enter <container_id>
   ```

### Étape 2 : Installer Docker

```bash
apt update && apt upgrade -y
apt install -y curl git
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
```

### Étape 3 : Déployer l'application

```bash
# Cloner ou copier le projet
cd /opt
git clone <ton_repo> iptv-restream
cd iptv-restream

# Configurer les identifiants Xtream
nano docker-compose.yml

# Lancer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Étape 4 : Configuration du pare-feu (optionnel)

```bash
apt install -y ufw
ufw allow 8080/tcp
ufw allow 8000/tcp
ufw enable
```

### Étape 5 : Accès

- Frontend : http://<IP_CONTAINER>:8080
- API Backend : http://<IP_CONTAINER>:8000/docs
   docker-compose up -d --build
   ```

3. Accède à http://localhost:8080

## Utilisation
- Accède à l'interface web sur http://localhost:8080
- Sélectionne une catégorie puis une chaîne
- Clique sur "Générer le lien de restream"
- Utilise le lien généré pour regarder la chaîne depuis n'importe où

## Sécurité
- Les liens générés sont uniques, mais non protégés par défaut (voir TODO pour sécurisation)
- Pour usage personnel uniquement

## TODO
- Authentification utilisateur
- Expiration automatique des liens
- Amélioration de l'UI
- Logs et monitoring

---

Développé avec FastAPI (backend) et HTML/JS (frontend)
