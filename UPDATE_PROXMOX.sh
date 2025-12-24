#!/bin/bash
# Script de mise à jour IPTV sur Proxmox

echo "🔄 Mise à jour IPTV Restream sur Proxmox..."

# Se placer dans le bon répertoire
cd /opt/iptv-restream

# Récupérer les dernières modifications
echo "📥 Récupération du code depuis GitHub..."
git pull origin main

# Reconstruire les images Docker avec les nouvelles modifications
echo "🔨 Reconstruction des images Docker..."
docker compose build backend frontend

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs..."
docker compose down

# Redémarrer avec les nouvelles images
echo "🚀 Démarrage des conteneurs..."
docker compose up -d

# Attendre que les services démarrent
echo "⏳ Attente du démarrage des services..."
sleep 5

# Vérifier le statut
echo ""
echo "✅ Statut des conteneurs:"
docker compose ps

echo ""
echo "📋 Logs du backend (10 dernières lignes):"
docker compose logs backend --tail=10

echo ""
echo "📋 Logs du frontend (10 dernières lignes):"
docker compose logs frontend --tail=10

echo ""
echo "✅ Mise à jour terminée!"
echo ""
echo "🌐 Services disponibles:"
echo "   Frontend: http://192.168.1.12:8001"
echo "   Backend API: http://192.168.1.12:8002/docs"
echo "   Login: admin / admin123"
