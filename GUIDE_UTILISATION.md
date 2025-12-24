# 📺 Guide d'Utilisation - IPTV Restream Platform

## 🎯 Vue d'ensemble

Votre plateforme IPTV permet de :
- **Contrôler** quelle chaîne est diffusée depuis une interface web
- **Regarder** le stream directement dans le navigateur (page `/watch`)
- **Partager** une URL fixe pour Jellyfin/VLC (`/live.m3u8`)
- **Générer** des liens temporaires VLC (24h d'expiration)

---

## 🚀 Démarrage rapide

### 1. Démarrer les serveurs

**Backend (API + FFmpeg):**
```powershell
cd "c:\Users\mndiaye\OneDrive - PG Construction\Bureau\iptv\backend"
.\.venv\Scripts\activate
python main.py
```
✅ Serveur backend: http://127.0.0.1:8002

**Frontend (Interface Web):**
```powershell
cd "c:\Users\mndiaye\OneDrive - PG Construction\Bureau\iptv\frontend"
.\.venv\Scripts\activate
python manage.py runserver 127.0.0.1:8001
```
✅ Serveur frontend: http://127.0.0.1:8001

---

## 📖 Utilisation de la plateforme

### Interface Admin (http://127.0.0.1:8001/)

#### 🟢 Indicateur de Stream Actif
En haut de la page, vous verrez :
- **Nom de la chaîne** en cours de diffusion
- **URL pour Jellyfin/VLC**: `http://127.0.0.1:8002/live.m3u8`
- **Bouton "🛑 Arrêter le stream"**: pour stopper la diffusion

#### 📡 Démarrer un Stream
1. Sélectionnez une **catégorie** dans la liste de gauche
2. Trouvez la **chaîne** que vous voulez diffuser
3. Cliquez sur **"📡 Diffuser"**
4. FFmpeg démarre automatiquement la conversion en HLS
5. Le stream est maintenant accessible !

#### ▶ Générer un Lien VLC Temporaire
1. Sélectionnez une chaîne
2. Cliquez sur **"▶ Restream"**
3. Copiez le lien généré (expire dans 24h)
4. Utilisez-le dans VLC ou tout autre lecteur

---

## 🎬 Regarder le Stream

### Option 1: Page Web `/watch` (Recommandé)
**URL fixe**: http://127.0.0.1:8001/watch/

**Avantages:**
- ✅ Lecture directe dans le navigateur (HLS.js)
- ✅ Interface full-screen moderne
- ✅ **L'URL du M3U8 n'est PAS visible** dans le navigateur
- ✅ Contrôles vidéo intégrés
- ✅ Pas besoin de VLC

**Comment ça marche:**
1. Démarrez un stream depuis l'admin (📡 Diffuser)
2. Ouvrez http://127.0.0.1:8001/watch/
3. Cliquez sur "▶ Lire"
4. Profitez du stream !

### Option 2: Jellyfin / Kodi / Autres Apps
**URL M3U8**: http://127.0.0.1:8002/live.m3u8

**Configuration Jellyfin:**
1. Allez dans **Tableau de bord → Live TV**
2. Ajoutez une source **M3U Tuner**
3. Collez l'URL: `http://127.0.0.1:8002/live.m3u8`
4. Sauvegardez

**Le contenu change automatiquement** selon la chaîne que vous sélectionnez dans l'admin !

### Option 3: VLC Media Player
**URL M3U8**: http://127.0.0.1:8002/live.m3u8

1. Ouvrez VLC
2. **Média → Ouvrir un flux réseau** (Ctrl+N)
3. Collez: `http://127.0.0.1:8002/live.m3u8`
4. Cliquez sur **Lire**

---

## 🔧 Architecture Technique

### URLs Disponibles

| URL | Description | Visible? |
|-----|-------------|----------|
| `http://127.0.0.1:8002/live.m3u8` | Stream HLS public (Jellyfin/VLC) | ✅ Oui |
| `http://127.0.0.1:8002/internal_stream.m3u8` | Stream HLS interne (page /watch) | ❌ Non visible dans le navigateur |
| `http://127.0.0.1:8001/watch/` | Page de lecture web | Interface graphique |
| `http://127.0.0.1:8001/` | Interface admin | Interface graphique |
| `http://127.0.0.1:8002/stream_status` | API statut (JSON) | Données brutes |

### Endpoints API

#### POST `/set_active_stream`
Démarre le stream FFmpeg pour une chaîne
```json
{
  "channel_id": 123456
}
```

#### POST `/stop_stream`
Arrête le stream FFmpeg actif

#### GET `/stream_status`
Retourne le statut du stream actif
```json
{
  "active": true,
  "channel_id": 123456,
  "channel_name": "TF1 HD",
  "started_at": "2025-12-24T10:30:00"
}
```

#### GET `/live.m3u8`
Playlist HLS publique (pour Jellyfin/VLC)

#### GET `/internal_stream.m3u8`
Playlist HLS interne (pour page /watch)

---

## 🛠️ Fonctionnalités Avancées

### Conversion FFmpeg en Temps Réel
- Convertit les streams `.ts` (MPEG-TS) en format HLS `.m3u8`
- Segments de 2 secondes pour faible latence
- Pas de réencodage (copie directe) → performance maximale
- Nettoie automatiquement les anciens segments

### Gestion du Stream Actif
- **Un seul stream à la fois** pour économiser les ressources
- Arrêt automatique du stream précédent avant d'en démarrer un nouveau
- Indicateur visuel dans l'admin
- Mise à jour automatique toutes les 5 secondes

### Sécurité et Isolation
- `/live.m3u8` : accessible pour Jellyfin (URL visible)
- `/internal_stream.m3u8` : accessible uniquement pour la page /watch (URL cachée)
- Même contenu, noms différents pour distinction

---

## ❓ FAQ

### Q: Le stream ne démarre pas ?
**R:** Vérifiez que :
1. FFmpeg est installé et dans le PATH
2. Le backend est lancé (`python main.py`)
3. Attendez 3-5 secondes après avoir cliqué "📡 Diffuser"

### Q: Erreur "Aucun stream actif" sur /watch ?
**R:** Vous devez d'abord démarrer un stream depuis l'admin (http://127.0.0.1:8001/)

### Q: Le M3U8 ne se charge pas dans Jellyfin ?
**R:** Assurez-vous que :
1. Un stream est actif (vérifiez l'admin)
2. L'URL est correcte: `http://127.0.0.1:8002/live.m3u8`
3. Le backend tourne bien

### Q: Puis-je regarder plusieurs chaînes en même temps ?
**R:** Non, un seul stream FFmpeg à la fois. Mais plusieurs personnes peuvent regarder le même stream simultanément.

### Q: L'URL M3U8 est-elle visible dans /watch ?
**R:** Non ! Le lecteur utilise `/internal_stream.m3u8` via JavaScript, l'URL n'apparaît pas dans la barre d'adresse.

---

## 🐛 Dépannage

### Le stream se coupe
- FFmpeg peut avoir planté → Relancez avec "📡 Diffuser"
- Vérifiez les logs du backend dans le terminal

### Qualité vidéo mauvaise
- Le stream est copié sans réencodage (qualité source)
- La qualité dépend de votre fournisseur IPTV Xtream

### Latence élevée
- Normal avec HLS (2-10 secondes de retard)
- Pour du live temps réel, utilisez un lecteur VLC direct

---

## 📊 Prochaines Étapes

- [ ] Déployer sur Proxmox avec Docker
- [ ] Ajouter authentification utilisateur
- [ ] Support multi-streams simultanés
- [ ] Enregistrement DVR
- [ ] EPG (guide des programmes)

---

## 📞 Support

Besoin d'aide ? Vérifiez les logs dans les terminaux backend/frontend.
