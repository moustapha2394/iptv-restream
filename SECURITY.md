# 🛡️ SECURITY.md

## Sécurité et Credentials

### ⚠️ IMPORTANT

Ce projet nécessite des credentials sensibles qui **NE DOIVENT JAMAIS** être committés dans Git :

1. **Identifiants Xtream Codes API**
2. **Clé secrète JWT**
3. **Hash du mot de passe admin**

### 🔐 Configuration Sécurisée

#### 1. Copier le fichier d'exemple

```bash
cp .env.example .env
```

#### 2. Éditer `docker-compose.yml`

Remplacez les placeholders par vos vraies valeurs :

```yaml
environment:
  # Vos identifiants Xtream
  - XTREAM_API_URL=http://your-xtream-server.com:port
  - XTREAM_USERNAME=your_xtream_username
  - XTREAM_PASSWORD=your_xtream_password
  
  # Générer avec: openssl rand -hex 32
  - JWT_SECRET_KEY=votre_cle_secrete_unique_ici
  
  # Générer avec: python backend/auth.py VotreMotDePasse
  - ADMIN_PASSWORD_HASH=$2b$12$...
```

### 🔑 Génération des Credentials

#### Clé JWT Sécurisée

```bash
openssl rand -hex 32
```

#### Hash du Mot de Passe Admin

```bash
cd backend
python auth.py VotreNouveauMotDePasse
```

Copiez le hash généré dans `docker-compose.yml`.

### 🚫 Ce qui ne doit JAMAIS être dans Git

- Vrais identifiants Xtream
- Vraie clé JWT
- Mots de passe en clair
- Adresses IP spécifiques de production
- Noms d'utilisateur personnels
- Fichiers `.env` avec des vraies valeurs

### ✅ Ce qui PEUT être dans Git

- `.env.example` avec des placeholders
- `docker-compose.yml` avec des placeholders
- Documentation sans credentials réels
- Code avec `os.environ.get()` et valeurs par défaut génériques

### 🔍 Vérification Avant Commit

Avant de pusher du code, vérifiez :

```bash
# Rechercher des patterns sensibles
git grep -i "admin123\|password\|secret\|token" -- "*.py" "*.yml" "*.md"

# Vérifier le .gitignore
cat .gitignore
```

### 📢 Signalement de Vulnérabilités

Si vous découvrez une faille de sécurité, **ne créez PAS d'issue publique**.

Contactez le mainteneur en privé.
