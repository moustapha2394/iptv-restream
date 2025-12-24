from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse, RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import httpx
import uuid
import os
import subprocess
import asyncio
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Import du système d'authentification
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user, 
    Token, 
    User,
    ACCESS_TOKEN_EXPIRE_HOURS
)

app = FastAPI(title="IPTV Restream API", version="2.0.0")

# CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Xtream depuis les variables d'environnement
XTREAM_API_URL = os.environ.get("XTREAM_API_URL", "http://line.dino.ws:80")
XTREAM_USERNAME = os.environ.get("XTREAM_USERNAME", "8c8e6d773d")
XTREAM_PASSWORD = os.environ.get("XTREAM_PASSWORD", "2ff8d53b8f8c")

# Configuration FFmpeg
FFMPEG_PATH = r"C:\Users\mndiaye\AppData\Local\Temp\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
HLS_OUTPUT_DIR = Path("hls_output")
HLS_OUTPUT_DIR.mkdir(exist_ok=True)

# Modèle de requête
class ChannelRequest(BaseModel):
    channel_id: int

# Stockage temporaire des liens générés avec expiration
restream_links = {}

# Gestion du stream FFmpeg actif
ffmpeg_process = None
current_stream = {
    "active": False,
    "channel_id": None,
    "channel_name": None,
    "stream_url": None,
    "started_at": None,
    "m3u8_path": None
}

# Cache des catégories et chaînes
categories_cache = []
channels_cache = []
cache_updated_at = None

def refresh_cache():
    """Récupère et met en cache les catégories et chaînes Xtream"""
    global categories_cache, channels_cache, cache_updated_at
    try:
        url_cat = f"{XTREAM_API_URL}/player_api.php?username={XTREAM_USERNAME}&password={XTREAM_PASSWORD}&action=get_live_categories"
        url_ch = f"{XTREAM_API_URL}/player_api.php?username={XTREAM_USERNAME}&password={XTREAM_PASSWORD}&action=get_live_streams"
        with httpx.Client(timeout=30.0) as client:
            r_cat = client.get(url_cat)
            r_ch = client.get(url_ch)
            if r_cat.status_code == 200:
                categories_cache = r_cat.json()
            if r_ch.status_code == 200:
                channels_cache = r_ch.json()
        cache_updated_at = datetime.now()
        print(f"✓ Cache refreshed: {len(categories_cache)} categories, {len(channels_cache)} channels")
    except Exception as e:
        print(f"✗ Erreur cache IPTV: {e}")

# Rafraîchit le cache au démarrage
print("Initialisation du cache IPTV...")
refresh_cache()

def stop_ffmpeg_stream():
    """Arrête le processus FFmpeg en cours"""
    global ffmpeg_process, current_stream
    if ffmpeg_process and ffmpeg_process.poll() is None:
        try:
            ffmpeg_process.terminate()
            ffmpeg_process.wait(timeout=5)
            print("✓ Stream FFmpeg arrêté")
        except:
            ffmpeg_process.kill()
            print("✗ Stream FFmpeg forcé à s'arrêter")
    
    # Nettoyer les fichiers HLS
    for file in HLS_OUTPUT_DIR.glob("*"):
        try:
            file.unlink()
        except:
            pass
    
    ffmpeg_process = None
    current_stream = {
        "active": False,
        "channel_id": None,
        "channel_name": None,
        "stream_url": None,
        "started_at": None,
        "m3u8_path": None
    }

def start_ffmpeg_stream(channel_id: int, channel_name: str, source_url: str):
    """Démarre FFmpeg pour convertir le stream TS en HLS"""
    global ffmpeg_process, current_stream
    
    # Arrêter le stream précédent si actif
    stop_ffmpeg_stream()
    
    # Chemin de sortie
    output_playlist = HLS_OUTPUT_DIR / "live.m3u8"
    
    # Commande FFmpeg optimisée pour HLS - live streaming IPTV
    ffmpeg_cmd = [
        FFMPEG_PATH,
        "-fflags", "+genpts+discardcorrupt",  # Générer les timestamps et ignorer les paquets corrompus
        "-i", source_url,
        "-c", "copy",  # Copie directe sans réencodage (le plus rapide)
        "-f", "hls",
        "-hls_time", "4",  # Segments de 4 secondes
        "-hls_list_size", "20",  # Garde 20 segments dans le M3U8 (80 secondes de buffer)
        "-hls_flags", "omit_endlist+delete_segments",  # Streaming infini + suppression auto des vieux segments
        "-hls_delete_threshold", "5",  # Garde 5 segments de plus que hls_list_size avant suppression
        "-hls_segment_filename", str(HLS_OUTPUT_DIR / "segment_%d.ts"),  # %d au lieu de %03d
        "-hls_base_url", "/hls/",
        "-reconnect", "1",  # Reconnexion auto si source déconnecte
        "-reconnect_at_eof", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",
        "-y",
        str(output_playlist)
    ]
    
    try:
        # Démarrer FFmpeg en arrière-plan
        ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combiner stderr dans stdout
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            text=True,
            bufsize=1
        )
        
        # Thread pour monitorer FFmpeg en temps réel
        def monitor_ffmpeg():
            for line in ffmpeg_process.stdout:
                print(f"[FFmpeg] {line.strip()}")
        
        import threading
        monitor_thread = threading.Thread(target=monitor_ffmpeg, daemon=True)
        monitor_thread.start()
        
        current_stream = {
            "active": True,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "stream_url": source_url,
            "started_at": datetime.now().isoformat(),
            "m3u8_path": str(output_playlist)
        }
        
        print(f"✓ Stream FFmpeg démarré: {channel_name}")
        return True
    except Exception as e:
        print(f"✗ Erreur démarrage FFmpeg: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.get("/")
def root():
    return {
        "status": "IPTV Restream with HLS",
        "version": "2.0.0",
        "categories": len(categories_cache),
        "channels": len(channels_cache),
        "stream_active": current_stream["active"],
        "current_channel": current_stream.get("channel_name", None)
    }

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Route de connexion - retourne un token JWT
    Credentials par défaut: admin / admin123
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/stats")
def stats():
    """Statistiques de l'API"""
    return {
        "categories_count": len(categories_cache),
        "channels_count": len(channels_cache),
        "cache_updated_at": cache_updated_at.isoformat() if cache_updated_at else None,
        "active_restream_links": len(restream_links)
    }

@app.post("/generate_link")
def generate_link(req: ChannelRequest, current_user: User = Depends(get_current_active_user)):
    """Génère un lien unique pour restreamer une chaîne (expire après 24h) - PROTÉGÉ"""
    link_id = str(uuid.uuid4())
    expiration = datetime.now() + timedelta(hours=24)
    restream_links[link_id] = {
        "url": f"{XTREAM_API_URL}/live/{XTREAM_USERNAME}/{XTREAM_PASSWORD}/{req.channel_id}.ts",
        "expires_at": expiration,
        "channel_id": req.channel_id
    }
    return {
        "restream_url": f"/restream/{link_id}.ts",
        "expires_at": expiration.isoformat()
    }

@app.get("/all_channels")
def all_channels(current_user: User = Depends(get_current_active_user)):
    """Retourne toutes les catégories avec leurs chaînes - PROTÉGÉ"""
    cat_dict = {str(cat['category_id']): {"category": cat, "channels": []} for cat in categories_cache}
    for ch in channels_cache:
        cat_id = str(ch.get("category_id"))
        if cat_id in cat_dict:
            cat_dict[cat_id]["channels"].append(ch)
    return {"categories": list(cat_dict.values())}

@app.get("/restream/{link_id}.ts")
@app.get("/restream/{link_id}")
async def restream(link_id: str):
    """Redirige vers le stream Xtream original"""
    link_id = link_id.replace(".ts", "")
    
    link_data = restream_links.get(link_id)
    if not link_data:
        raise HTTPException(404, "Lien invalide ou expiré")
    
    if datetime.now() > link_data["expires_at"]:
        del restream_links[link_id]
        raise HTTPException(410, "Lien expiré")
    
    return RedirectResponse(url=link_data["url"])

@app.post("/set_active_stream")
def set_active_stream(req: ChannelRequest, current_user: User = Depends(get_current_active_user)):
    """Démarre le stream FFmpeg pour la chaîne sélectionnée - PROTÉGÉ"""
    # Trouver les infos de la chaîne
    channel = next((ch for ch in channels_cache if ch.get('stream_id') == req.channel_id), None)
    if not channel:
        raise HTTPException(404, "Chaîne introuvable")
    
    channel_name = channel.get('name', 'Chaîne inconnue')
    stream_url = f"{XTREAM_API_URL}/live/{XTREAM_USERNAME}/{XTREAM_PASSWORD}/{req.channel_id}.ts"
    
    # Démarrer le stream FFmpeg
    success = start_ffmpeg_stream(req.channel_id, channel_name, stream_url)
    
    if not success:
        raise HTTPException(500, "Impossible de démarrer le stream")
    
    return {
        "status": "success",
        "message": f"Stream démarré: {channel_name}",
        "channel_name": channel_name,
        "m3u8_url": "/live.m3u8",
        "watch_url": "/watch"
    }

@app.post("/stop_stream")
def stop_stream(current_user: User = Depends(get_current_active_user)):
    """Arrête le stream FFmpeg actif - PROTÉGÉ"""
    if not current_stream["active"]:
        raise HTTPException(400, "Aucun stream actif")
    
    channel_name = current_stream.get("channel_name")
    stop_ffmpeg_stream()
    
    return {
        "status": "success",
        "message": f"Stream arrêté: {channel_name}"
    }

@app.get("/stream_status")
def stream_status():
    """Retourne le statut du stream actif"""
    return current_stream

@app.get("/active_stream")
def get_active_stream():
    """Retourne le stream actif (compatibilité)"""
    return {
        "active": current_stream["active"],
        "channel_id": current_stream.get("channel_id"),
        "channel_name": current_stream.get("channel_name"),
        "stream_url": current_stream.get("stream_url"),
        "started_at": current_stream.get("started_at")
    }

@app.get("/live.m3u8")
async def live_m3u8():
    """Endpoint public pour Jellyfin/VLC - retourne la playlist M3U8"""
    if not current_stream["active"]:
        raise HTTPException(404, "Aucun stream actif")
    
    m3u8_path = Path(current_stream["m3u8_path"])
    
    # Attendre jusqu'à 10 secondes que FFmpeg génère le M3U8
    import asyncio
    max_wait = 10  # secondes
    wait_interval = 0.5  # secondes
    elapsed = 0
    
    while not m3u8_path.exists() and elapsed < max_wait:
        await asyncio.sleep(wait_interval)
        elapsed += wait_interval
    
    if not m3u8_path.exists():
        raise HTTPException(503, "Stream en cours de démarrage, réessayez dans quelques secondes")
    
    try:
        content = m3u8_path.read_text()
        return Response(content=content, media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        raise HTTPException(500, f"Erreur lecture playlist: {e}")

@app.get("/segment_{num}.ts")
async def segment_file(num: str):
    """Sert les segments TS à la racine pour HLS.js"""
    filename = f"segment_{num}.ts"
    file_path = HLS_OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, f"Segment {filename} introuvable")
    
    try:
        content = file_path.read_bytes()
        return Response(content=content, media_type="video/MP2T")
    except Exception as e:
        raise HTTPException(500, f"Erreur lecture segment: {e}")

@app.get("/hls/{filename}")
async def hls_segment(filename: str):
    """Sert les segments HLS depuis /hls/"""
    file_path = HLS_OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "Segment introuvable")
    
    try:
        content = file_path.read_bytes()
        media_type = "application/vnd.apple.mpegurl" if filename.endswith(".m3u8") else "video/MP2T"
        return Response(content=content, media_type=media_type)
    except Exception as e:
        raise HTTPException(500, f"Erreur lecture segment: {e}")

@app.get("/internal_stream.m3u8")
async def internal_stream():
    """Endpoint interne pour la page /watch - même contenu que /live.m3u8 mais nom différent"""
    return await live_m3u8()

@app.get("/proxy_stream")
async def proxy_stream():
    """Redirige vers le stream HLS interne"""
    if not current_stream["active"]:
        raise HTTPException(404, "Aucun stream actif")
    return RedirectResponse(url="/internal_stream.m3u8")

@app.on_event("shutdown")
def shutdown_event():
    """Nettoie les ressources au shutdown"""
    stop_ffmpeg_stream()
    print("✓ Ressources nettoyées")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
