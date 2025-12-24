# 🚀 Mise à jour Proxmox - Correction Locale + Réseau

## 📋 Problème résolu

✅ **Backend écoute maintenant sur 0.0.0.0** (accepte connexions réseau)  
✅ **Frontend détecte automatiquement l'IP** (127.0.0.1 local, 192.168.1.12 Proxmox)  
✅ **Compatible développement local ET production Proxmox**

---

## 🔄 Mise à jour sur Proxmox (192.168.1.12)

### Étape 1 : Se connecter en SSH

```bash
ssh moustapha2394@192.168.1.12
sudo su -
cd /opt/iptv-restream
```

### Étape 2 : Mettre à jour le code

```bash
git pull origin main
```

### Étape 3 : Reconstruire les images Docker

```bash
# Reconstruire le backend (nouvelles modifications)
docker compose build backend

# Reconstruire le frontend (détection automatique de l'hôte)
docker compose build frontend
```

### Étape 4 : Redémarrer les conteneurs

```bash
docker compose down
docker compose up -d
```

### Étape 5 : Vérifier le statut

```bash
docker compose ps
docker compose logs -f backend --tail=50
docker compose logs -f frontend --tail=50
```

---

## ✅ Test de vérification

### 1. Tester le backend depuis le navigateur :

Ouvrir dans un navigateur (sur un autre PC du réseau) :

```
http://192.168.1.12:8002/docs
```

Vous devriez voir la documentation Swagger de l'API.

### 2. Tester l'authentification :

```bash
curl -X POST http://192.168.1.12:8002/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Résultat attendu : un token JWT valide.

### 3. Tester le frontend :

Ouvrir dans un navigateur :

```
http://192.168.1.12:8001
```

- Se connecter avec : **admin** / **admin123**
- Sélectionner une chaîne
- Vérifier que le streaming fonctionne

---

## 🔍 Modifications techniques effectuées

### Backend (main.py)

**Avant :**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)  # ❌ Accessible uniquement en local
```

**Après :**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # ✅ Accessible sur le réseau
```

### Frontend (templates/*.html)

**Avant :**
```javascript
const API_URL = 'http://127.0.0.1:8002';  // ❌ Hardcodé
```

**Après :**
```javascript
const API_URL = `http://${window.location.hostname}:8002`;  // ✅ Détection automatique
```

### FFmpeg Path

**Avant :**
```python
FFMPEG_PATH = r"C:\Users\mndiaye\...\ffmpeg.exe"  # ❌ Windows seulement
```

**Après :**
```python
import platform
if platform.system() == "Windows":
    FFMPEG_PATH = r"C:\Users\mndiaye\...\ffmpeg.exe"
else:
    FFMPEG_PATH = "ffmpeg"  # ✅ Linux/Docker
```

---

## 🐳 Alternatives de déploiement

### Option 1 : Build local (actuelle) ⚡ Plus rapide

```bash
docker compose build backend frontend
docker compose up -d
```

### Option 2 : Pull depuis GHCR 🌐 Sans rebuild

Attendre que GitHub Actions construise les images (5-10 min), puis :

```bash
docker compose pull
docker compose up -d
```

---

## 📝 Troubleshooting

### Problème : Backend inaccessible depuis le réseau

**Vérifier que le backend écoute sur 0.0.0.0 :**

```bash
docker compose logs backend | grep "Uvicorn running"
```

Résultat attendu : `Uvicorn running on http://0.0.0.0:8002`

### Problème : Frontend ne trouve pas le backend

**Vérifier dans la console du navigateur (F12) :**

- Chercher les requêtes vers `http://192.168.1.12:8002`
- Vérifier qu'il n'y a pas de requêtes vers `127.0.0.1`

### Problème : CORS errors

**Vérifier les logs du backend :**

```bash
docker compose logs backend | grep CORS
```

Le backend devrait déjà accepter toutes les origines (`allow_origins=["*"]`).

---

## 🎯 Résumé des changements

| Fichier | Modification | Impact |
|---------|-------------|--------|
| `backend/main.py` | `host="0.0.0.0"` | Backend accessible réseau |
| `frontend/templates/login.html` | `window.location.hostname` | Détection auto IP |
| `frontend/templates/restream_list.html` | `window.location.hostname` | Détection auto IP |
| `frontend/templates/watch.html` | `window.location.hostname` | Détection auto IP |
| `frontend/restream/views.py` | `os.environ.get('BACKEND_URL')` | Config flexible |

---

## 🔐 Sécurité post-déploiement

Après validation du fonctionnement, pensez à :

1. **Changer le mot de passe admin**
2. **Configurer ALLOWED_HOSTS** dans Django (au lieu de `['*']`)
3. **Générer une nouvelle JWT_SECRET_KEY**
4. **Ajouter un reverse proxy nginx** pour SSL/TLS

---

✅ **La plateforme IPTV est maintenant compatible local + Proxmox !**
