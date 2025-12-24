# Script PowerShell pour déployer l'application IPTV avec Docker
# Prérequis : Docker Desktop for Windows installé

Write-Host "==================================" -ForegroundColor Cyan
Write-Host " IPTV Restream - Déploiement Docker" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Docker
Write-Host "Vérification de Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker trouvé : $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker n'est pas installé!" -ForegroundColor Red
    Write-Host "Téléchargez Docker Desktop : https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Vérifier Docker Compose
try {
    $composeVersion = docker compose version
    Write-Host "✓ Docker Compose trouvé : $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose n'est pas disponible!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Vérifier le fichier .env
if (-Not (Test-Path ".env")) {
    Write-Host "⚠ Fichier .env non trouvé!" -ForegroundColor Yellow
    Write-Host "Création depuis .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠ IMPORTANT : Éditez le fichier .env avant de continuer!" -ForegroundColor Red
    Write-Host "Fichier : $PWD\.env" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Voulez-vous continuer avec les valeurs par défaut ? (o/N)"
    if ($continue -ne "o" -and $continue -ne "O") {
        Write-Host "Déploiement annulé. Configurez .env et relancez le script." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Building Docker images..." -ForegroundColor Yellow
docker compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Erreur lors du build!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Images buildées avec succès!" -ForegroundColor Green
Write-Host ""

Write-Host "Démarrage des conteneurs..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Erreur lors du démarrage!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Conteneurs démarrés!" -ForegroundColor Green
Write-Host ""

# Attendre que les services soient prêts
Write-Host "Attente du démarrage des services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Afficher les conteneurs
Write-Host ""
Write-Host "État des conteneurs :" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host " ✓ Déploiement terminé!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Accès à l'application :" -ForegroundColor Cyan
Write-Host "  Frontend (Admin)  : http://localhost:8001" -ForegroundColor White
Write-Host "  Backend (API)     : http://localhost:8002" -ForegroundColor White
Write-Host "  API Docs          : http://localhost:8002/docs" -ForegroundColor White
Write-Host ""
Write-Host "Identifiants par défaut :" -ForegroundColor Cyan
Write-Host "  Username : admin" -ForegroundColor White
Write-Host "  Password : admin123" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles :" -ForegroundColor Yellow
Write-Host "  Voir les logs      : docker compose logs -f" -ForegroundColor White
Write-Host "  Arrêter            : docker compose down" -ForegroundColor White
Write-Host "  Redémarrer         : docker compose restart" -ForegroundColor White
Write-Host ""
