# Configuration Cloudflare Tunnel pour IPTV Restream

## Tunnel ID
**Tunnel ID:** `2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d`

## Architecture des sous-domaines

### 1. Backend API - api.senbaye.me
- **Service:** Backend FastAPI
- **Port local:** 8002
- **IP:** 192.168.1.88:8002
- **Usage:** API REST pour gestion des streams

### 2. Player Public - restream.senbaye.me
- **Service:** Player Django
- **Port local:** 8003
- **IP:** 192.168.1.88:8003
- **Usage:** Interface publique de visionnage

### 3. Interface Admin - admin.senbaye.me
- **Service:** Frontend Django
- **Port local:** 8001
- **IP:** 192.168.1.88:8001
- **Usage:** Panneau d'administration

## Configuration DNS Cloudflare

Dans votre tableau de bord Cloudflare (senbaye.me), créez ces enregistrements DNS:

| Type  | Nom              | Contenu                            | Proxy | TTL  |
|-------|------------------|------------------------------------|-------|------|
| CNAME | api              | 2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com | ✅ | Auto |
| CNAME | restream         | 2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com | ✅ | Auto |
| CNAME | admin            | 2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.cfargotunnel.com | ✅ | Auto |

## Installation sur Proxmox

### 1. Télécharger cloudflared
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### 2. Créer le répertoire de configuration
```bash
sudo mkdir -p /root/.cloudflared
```

### 3. Copier le fichier de credentials
**IMPORTANT:** Le fichier `2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.json` doit être créé avec vos credentials Cloudflare.

Pour obtenir ce fichier, utilisez une de ces méthodes:

#### Méthode A: Depuis votre dashboard Cloudflare
1. Allez sur https://dash.cloudflare.com/
2. Accédez à votre tunnel existant
3. Téléchargez le fichier de credentials JSON

#### Méthode B: Recréer le tunnel (si credentials perdu)
```bash
cloudflared tunnel login
cloudflared tunnel create iptv-restream
# Cela créera un nouveau tunnel et générera le fichier JSON
```

### 4. Placer les fichiers de configuration
```bash
# Copier le fichier cloudflared-config.yml
sudo cp cloudflared-config.yml /root/.cloudflared/config.yml

# Copier le fichier de credentials (à adapter selon votre fichier)
sudo cp 2f2c9539-9d34-4b79-a9c1-2cb0c4477c3d.json /root/.cloudflared/
```

### 5. Tester la configuration
```bash
sudo cloudflared tunnel --config /root/.cloudflared/config.yml run
```

Si tout fonctionne, vous devriez voir:
```
INF Connection established connIndex=0
INF Connection established connIndex=1
INF Connection established connIndex=2
INF Connection established connIndex=3
```

### 6. Créer le service systemd
```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### 7. Vérifier le statut
```bash
sudo systemctl status cloudflared
```

## Vérification des URLs

Après configuration, testez chaque service:

### Backend API
```bash
curl https://api.senbaye.me/health
# Devrait retourner: {"status":"ok"}
```

### Player Public
```bash
curl -I https://restream.senbaye.me
# Devrait retourner: HTTP/2 200
```

### Interface Admin
```bash
curl -I https://admin.senbaye.me
# Devrait retourner: HTTP/2 200
```

## Détection automatique Frontend/Player

Avec cette configuration, vos templates HTML détectent automatiquement l'environnement:

**Accès local (192.168.1.88):**
- Frontend → Backend: `http://192.168.1.88:8002`
- Player → Backend: `http://192.168.1.88:8002`

**Accès production (Cloudflare):**
- Frontend → Backend: `https://api.senbaye.me`
- Player → Backend: `https://api.senbaye.me`

## Logs et Debugging

### Voir les logs en temps réel
```bash
sudo journalctl -u cloudflared -f
```

### Voir les dernières erreurs
```bash
sudo journalctl -u cloudflared -n 50 --no-pager
```

### Redémarrer le tunnel
```bash
sudo systemctl restart cloudflared
```

## Sécurité

- ✅ HTTPS automatique via Cloudflare
- ✅ Protection DDoS Cloudflare
- ✅ Backend non exposé directement
- ✅ Credentials JWT pour authentification admin
- ✅ CORS configuré pour domaines spécifiques

## Architecture Réseau

```
Internet
    ↓
Cloudflare Edge (HTTPS)
    ↓
Cloudflare Tunnel (encrypted)
    ↓
Proxmox Server (192.168.1.88)
    ↓
┌─────────────────────────────────┐
│ admin.senbaye.me → :8001        │
│ api.senbaye.me → :8002          │
│ restream.senbaye.me → :8003     │
└─────────────────────────────────┘
```

## Notes Importantes

1. **Credentials File:** Le fichier `.json` contient les credentials secrets du tunnel. Ne le commitez JAMAIS dans Git.

2. **IP Locale:** La configuration utilise `192.168.1.88` car c'est l'IP de votre serveur Proxmox. Cloudflared s'exécute sur le même serveur et accède aux services via localhost.

3. **NoTLSVerify:** Activé car les services locaux n'ont pas de certificats SSL (communication interne).

4. **HTTP Host Header:** Configuré pour que chaque service reçoive le bon hostname.

5. **Connecté en permanence:** Le tunnel maintient 4 connexions permanentes avec Cloudflare pour la haute disponibilité.
