## 🎯 Utilisation

### Interface Web

1. **Rechercher une catégorie** :
   - Utilise la barre de recherche en haut à gauche
   - Clique sur une catégorie pour voir ses chaînes

2. **Rechercher une chaîne** :
   - Utilise la barre de recherche en haut à droite
   - Le filtrage est instantané

3. **Générer un lien de restream** :
   - Clique sur le bouton "▶ Restream" à côté d'une chaîne
   - Le lien est généré et affiché en bas
   - Clique sur "📋 Copier" pour copier le lien dans le presse-papier

4. **Utiliser le lien** :
   - Ouvre le lien dans VLC, IPTV Player, ou tout autre lecteur compatible
   - Le lien expire après 24h pour des raisons de sécurité

### API REST

L'API est accessible sur `http://localhost:8000` :

- `GET /` - Informations sur l'API et statistiques
- `GET /all_channels` - Liste toutes les catégories et chaînes
- `POST /generate_link` - Génère un lien de restream
  ```json
  {
    "channel_id": 12345
  }
  ```
- `GET /restream/{link_id}` - Stream proxy pour une chaîne
- `GET /stats` - Statistiques détaillées
- `POST /refresh` - Force le rafraîchissement du cache

Documentation interactive : http://localhost:8000/docs

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `XTREAM_URL` | URL du serveur Xtream | http://your-server.com:port |
| `XTREAM_USER` | Nom d'utilisateur Xtream | - |
| `XTREAM_PASS` | Mot de passe Xtream | - |

### Fichiers de configuration

- `backend/main.py` : Configuration du backend FastAPI
- `frontend/iptv_frontend/settings.py` : Configuration Django
- `docker-compose.yml` : Configuration des services Docker

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Redémarrer le service
docker-compose restart backend
```

### Erreur de connexion Xtream

- Vérifie que les identifiants Xtream sont corrects
- Vérifie que le serveur Xtream est accessible
- Test manuel : `curl "http://serveur:port/player_api.php?username=user&password=pass&action=get_live_categories"`

### Le cache ne se rafraîchit pas

```bash
# Forcer le rafraîchissement
curl -X POST http://localhost:8000/refresh
```

## 📊 Monitoring

### Vérifier l'état des services

```bash
docker-compose ps
docker-compose logs -f
```

### Statistiques de l'API

```bash
curl http://localhost:8000/stats
```

## 🔒 Sécurité

- ⚠️ **Pas d'authentification par défaut** : À ajouter pour un usage public
- ✅ **Expiration des liens** : Les liens expirent après 24h
- ✅ **CORS configuré** : Pour permettre l'accès depuis le frontend
- ⚠️ **Usage personnel** : Ne pas partager publiquement sans mesures de sécurité

## 📝 TODO / Améliorations futures

- [ ] Authentification utilisateur (JWT)
- [ ] Rate limiting sur les endpoints
- [ ] Logs persistants (fichiers ou base de données)
- [ ] Statistiques avancées (chaînes les plus regardées, etc.)
- [ ] Support de plusieurs codes Xtream
- [ ] Mode sombre / clair pour l'interface
- [ ] Application mobile (React Native / Flutter)
- [ ] Notifications push pour les chaînes favorites
- [ ] Enregistrement des streams (DVR)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésite pas à ouvrir une issue ou une pull request.

## 📄 Licence

Ce projet est à usage personnel uniquement. Respecte les conditions d'utilisation de ton fournisseur IPTV.

---

**Développé avec ❤️ par [Ton Nom]**  
Backend : FastAPI • Frontend : Django + Bootstrap • Déploiement : Docker
