from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import json
import os

# L'URL backend est récupérée depuis la variable d'environnement ou localhost par défaut
API_URL = os.environ.get('BACKEND_URL', 'http://localhost:8002')

def login_page(request):
    """Page de login"""
    return render(request, "login.html")

def home(request):
    """Page d'accueil avec toutes les catégories et chaînes - PROTÉGÉE"""
    # Récupérer le token depuis le cookie ou query parameter
    token = request.COOKIES.get('access_token') or request.GET.get('token')
    
    if not token:
        # Pas de token, rediriger vers login
        return redirect('/login')
    
    try:
        # Appeler l'API avec le token d'authentification
        headers = {
            'Authorization': f'Bearer {token}'
        }
        res = requests.get(f"{API_URL}/all_channels", headers=headers, timeout=10)
        
        if res.status_code == 401 or res.status_code == 403:
            # Token invalide ou expiré, rediriger vers login
            response = redirect('/login')
            response.delete_cookie('access_token')
            return response
        
        if res.status_code == 200:
            categories_with_channels = res.json().get("categories", [])
        else:
            categories_with_channels = []
    except Exception as e:
        print(f"Erreur connexion backend: {e}")
        categories_with_channels = []
    
    # Convertit en JSON pour passer au template JavaScript
    categories_json = json.dumps(categories_with_channels)
    
    # Créer la response et ajouter le token en cookie si fourni via GET
    response = render(request, "restream_list.html", {
        "categories": categories_with_channels,
        "categories_json": categories_json,
        "access_token": token
    })
    
    # Si le token vient du GET, le mettre dans un cookie
    if request.GET.get('token'):
        response.set_cookie('access_token', token, max_age=86400)  # 24 heures
    
    return response

def watch(request):
    """Page de lecture du stream actif - PUBLIQUE"""
    return render(request, "watch.html")

def logout(request):
    """Déconnexion - supprime le token"""
    # Rendre la page de logout qui va supprimer le localStorage
    return render(request, "logout.html")