#!/bin/bash
# Script Bash pour déployer l'application IPTV avec Docker (Linux/Proxmox)

echo "=================================="
echo " IPTV Restream - Déploiement Docker"
echo "=================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Vérifier Docker
echo -e "${YELLOW}Vérification de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker n'est pas installé!${NC}"
    echo -e "${YELLOW}Installation de Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo systemctl enable docker
    sudo systemctl start docker
    rm get-docker.sh
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓ Docker trouvé : $DOCKER_VERSION${NC}"

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose n'est pas installé!${NC}"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version 2>/dev/null || docker-compose --version)
echo -e "${GREEN}✓ Docker Compose trouvé : $COMPOSE_VERSION${NC}"
echo ""

# Vérifier le fichier .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Fichier .env non trouvé!${NC}"
    echo -e "${YELLOW}Création depuis .env.example...${NC}"
    cp .env.example .env
    echo ""
    echo -e "${RED}⚠ IMPORTANT : Éditez le fichier .env avant de continuer!${NC}"
    echo -e "${YELLOW}Fichier : $(pwd)/.env${NC}"
    echo ""
    read -p "Voulez-vous continuer avec les valeurs par défaut ? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        echo -e "${YELLOW}Déploiement annulé. Configurez .env et relancez le script.${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}Building Docker images...${NC}"

# Utiliser docker compose (v2) ou docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erreur lors du build!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Images buildées avec succès!${NC}"
echo ""

echo -e "${YELLOW}Démarrage des conteneurs...${NC}"
$COMPOSE_CMD up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erreur lors du démarrage!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Conteneurs démarrés!${NC}"
echo ""

# Attendre que les services soient prêts
echo -e "${YELLOW}Attente du démarrage des services...${NC}"
sleep 5

# Afficher les conteneurs
echo ""
echo -e "${CYAN}État des conteneurs :${NC}"
$COMPOSE_CMD ps

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN} ✓ Déploiement terminé!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${CYAN}Accès à l'application :${NC}"
echo -e "  Frontend (Admin)  : http://localhost:8001"
echo -e "  Backend (API)     : http://localhost:8002"
echo -e "  API Docs          : http://localhost:8002/docs"
echo ""
echo -e "${CYAN}Identifiants par défaut :${NC}"
echo -e "  Username : admin"
echo -e "  Password : admin123"
echo ""
echo -e "${YELLOW}Commandes utiles :${NC}"
echo -e "  Voir les logs      : $COMPOSE_CMD logs -f"
echo -e "  Arrêter            : $COMPOSE_CMD down"
echo -e "  Redémarrer         : $COMPOSE_CMD restart"
echo ""
