# Architecture 3 Services - IPTV Restream Platform

## 📐 Architecture

L'application est maintenant séparée en **3 services indépendants** :

### 1. **Backend API** (Port 8002)
- **Rôle** : API FastAPI, gestion des streams FFmpeg, authentification JWT
- **Technologies** : FastAPI, FFmpeg, Python
- **Accès** : 
  - Local : `http://localhost:8002`
  - Production : `https://api.senbaye.me`
- **Endpoints** :
  - `/auth/login` - Authentification
  - `/categories` - Liste des catégories
  - `/channels` - Liste des chaînes
  - `/start_stream` - Démarrer un stream
  - `/stop_stream` - Arrêter le stream
  - `/stream_status` - Statut du stream actif
  - `/internal_stream.m3u8` - Playlist HLS
  - `/live.m3u8` - Playlist publique

### 2. **Frontend Admin** (Port 8001)
- **Rôle** : Interface d'administration pour choisir et gérer les streams
- **Technologies** : Django, Bootstrap
- **Accès** : 
  - Local : `http://localhost:8001`
  - Production : `https://iptv-restream.senbaye.me` (privé, pas exposé sur Cloudflare)
- **Pages** :
  - `/` - Dashboard avec sélection de chaînes
  - `/login` - Page de connexion (admin / admin123)
  - `/logout` - Déconnexion

### 3. **Player Public** (Port 8003)
- **Rôle** : Lecteur vidéo public pour regarder le stream actif
- **Technologies** : Django minimal, HLS.js
- **Accès** : 
  - Local : `http://localhost:8003`
  - Production : `https://restream.senbaye.me`
- **Pages** :
  - `/` - Lecteur vidéo avec détection automatique du stream

---

## 🚀 Déploiement

### Configuration Cloudflare Tunnel

Fichier `/etc/cloudflared/config.yml` :

```yaml
tunnel: 2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d
credentials-file: /root/.cloudflared/2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.json

ingress:
  # API Backend (accessible publiquement)
  - hostname: api.senbaye.me
    service: http://localhost:8002
  
  # Player Public (accessible publiquement)
  - hostname: restream.senbaye.me
    service: http://localhost:8003
  
  # Frontend Admin (optionnel - peut rester privé sur LAN uniquement)
  # - hostname: admin.senbaye.me
  #   service: http://localhost:8001
  
  # Catch-all
  - service: http_status:404
```

### DNS Cloudflare

Ajouter ces enregistrements CNAME dans Cloudflare Dashboard :

1. **api.senbaye.me** → `2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com`
2. **restream.senbaye.me** → `2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com`
3. (Optionnel) **admin.senbaye.me** → `2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com`

### Commandes de Déploiement

```bash
# 1. Cloner le repository
cd /opt
git clone https://github.com/moustapha2394/iptv-restream.git
cd iptv-restream

# 2. Configurer les variables d'environnement
nano docker-compose.yml
# Modifier :
# - XTREAM_API_URL
# - XTREAM_USERNAME
# - XTREAM_PASSWORD
# - JWT_SECRET_KEY
# - ADMIN_PASSWORD_HASH

# 3. Démarrer les containers
docker compose pull
docker compose up -d

# 4. Vérifier les logs
docker compose logs -f

# 5. Configurer Cloudflare Tunnel
nano /etc/cloudflared/config.yml
# Copier la configuration ci-dessus

# 6. Redémarrer cloudflared
systemctl restart cloudflared
systemctl status cloudflared
```

---

## 🔐 Sécurité

### Exposition des Services

| Service | Port | Exposé sur Cloudflare | Authentification |
|---------|------|----------------------|------------------|
| Backend API | 8002 | ✅ api.senbaye.me | JWT Bearer Token |
| Frontend Admin | 8001 | ❌ (LAN uniquement) | Session Cookie |
| Player Public | 8003 | ✅ restream.senbaye.me | Aucune |

### Avantages de cette Architecture

1. **Sécurité** : L'interface admin (8001) reste privée sur le LAN
2. **Simplicité** : Le player public (8003) est accessible sans authentification
3. **Flexibilité** : L'API (8002) peut être utilisée par d'autres clients
4. **Scalabilité** : Chaque service peut être scalé indépendamment

---

## 📊 Flux d'Utilisation

### Pour l'Administrateur (LAN)

1. Accéder à `http://192.168.X.X:8001` (IP locale du LXC)
2. Se connecter avec `admin` / `admin123`
3. Choisir une catégorie et une chaîne
4. Cliquer sur "Démarrer le stream"
5. Le système affiche : `https://restream.senbaye.me/`

### Pour les Spectateurs (Internet)

1. Accéder à `https://restream.senbaye.me/`
2. Le player détecte automatiquement le stream actif
3. La vidéo démarre automatiquement après 6 secondes
4. Si aucun stream → Message "Aucun stream actif"

### Pour Jellyfin/Plex/VLC

URL du stream HLS : `https://api.senbaye.me/live.m3u8`

---

## 🧪 Tests en Local

```bash
# Démarrer tous les services
docker compose up -d

# Accéder aux différents services
# - Admin : http://localhost:8001
# - API : http://localhost:8002/docs
# - Player : http://localhost:8003

# Logs en temps réel
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f player
```

---

## 📝 Notes

- Le frontend admin (8001) **ne doit PAS** être exposé sur internet
- Le player (8003) est accessible sans authentification pour le public
- L'API (8002) nécessite un JWT pour les endpoints d'administration
- Le stream HLS (`/live.m3u8`) est public pour permettre l'intégration dans Jellyfin/Plex

---

## 🔧 Maintenance

### Mettre à jour les images

```bash
docker compose pull
docker compose up -d
```

### Voir les containers actifs

```bash
docker compose ps
```

### Redémarrer un service spécifique

```bash
docker compose restart backend
docker compose restart frontend
docker compose restart player
```

### Arrêter tous les services

```bash
docker compose down
```
