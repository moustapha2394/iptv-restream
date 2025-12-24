import requests

XTREAM_URL = "http://line.dino.ws:80"
XTREAM_USER = "8c8e6d773d"
XTREAM_PASS = "2ff8d53b8f8c"

print("Test de connexion Xtream...")
print(f"URL: {XTREAM_URL}")
print(f"User: {XTREAM_USER}")

try:
    # Test API
    response = requests.get(
        f"{XTREAM_URL}/player_api.php",
        params={"username": XTREAM_USER, "password": XTREAM_PASS},
        timeout=10
    )
    print(f"\nRéponse API (status {response.status_code}):")
    data = response.json()
    
    if "user_info" in data:
        user_info = data["user_info"]
        print(f"✓ Authentification réussie")
        print(f"  - Statut: {user_info.get('status')}")
        print(f"  - Expire: {user_info.get('exp_date')}")
        print(f"  - Actif: {user_info.get('is_trial')}")
    else:
        print("✗ Pas d'info utilisateur dans la réponse")
        print(f"Réponse: {data}")
    
    # Test d'un stream direct
    print("\nTest d'un stream vidéo...")
    stream_url = f"{XTREAM_URL}/live/{XTREAM_USER}/{XTREAM_PASS}/21894.ts"
    print(f"URL: {stream_url}")
    
    stream_response = requests.head(stream_url, timeout=10)
    print(f"Status: {stream_response.status_code}")
    print(f"Headers: {dict(stream_response.headers)}")
    
except Exception as e:
    print(f"✗ Erreur: {e}")
