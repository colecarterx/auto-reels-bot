import requests
import json
import schedule
import time

# ---- CONFIGURACIÓN ----
BUNNY_STORAGE_ZONE = "reelszone"
BUNNY_API_KEY = "TU_PASSWORD_DE_BUNNY"  # Pon tu password FTP/API de Bunny
STORAGE_URL = f"https://storage.bunnycdn.com/{BUNNY_STORAGE_ZONE}/"

# Lista de tokens de todas tus cuentas/páginas Meta
META_TOKENS = [
    "TOKEN_CUENTA1",
    "TOKEN_CUENTA2",
    # agrega todos tus tokens
]

PUBLISHED_FILE = "published.json"  # Registro de reels publicados

# ---- FUNCIONES ----
def listar_reels():
    """Obtiene la lista de reels desde Bunny Storage"""
    r = requests.get(STORAGE_URL, auth=(BUNNY_STORAGE_ZONE, BUNNY_API_KEY))
    if r.status_code != 200:
        print("Error listando archivos:", r.text)
        return []
    archivos = r.json()
    urls = [f"https://{BUNNY_STORAGE_ZONE}.b-cdn.net/{a['ObjectName']}" for a in archivos]
    return urls

def cargar_publicados():
    """Carga el registro de reels publicados"""
    try:
        with open(PUBLISHED_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_publicados(publicados):
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(publicados, f)

def publicar_en_meta(url):
    """Publica el reel en todas las cuentas conectadas"""
    for token in META_TOKENS:
        api_url = f"https://graph.facebook.com/v17.0/me/videos?access_token={token}"
        data = {
            "file_url": url,
            "title": "Reel automático",
            "description": "Publicado automáticamente con Auto-Reels Bot"
        }
        try:
            resp = requests.post(api_url, data=data)
            if resp.status_code == 200:
                print(f"Publicado correctamente en token {token}")
            else:
                print(f"Error publicando en token {token}: {resp.text}")
        except Exception as e:
            print(f"Excepción publicando en token {token}: {e}")

def publicar_reel():
    urls = listar_reels()
    publicados = cargar_publicados()
    
    for url in urls:
        if url not in publicados:
            print(f"Publicando reel: {url}")
            publicar_en_meta(url)
            publicados.append(url)
            guardar_publicados(publicados)
            break  # Publica solo 1 reel por ejecución
    else:
        print("Todos los reels ya fueron publicados.")

# ---- SCHEDULER: 4 veces al día ----
schedule.every().day.at("09:00").do(publicar_reel)
schedule.every().day.at("12:00").do(publicar_reel)
schedule.every().day.at("15:00").do(publicar_reel)
schedule.every().day.at("18:00").do(publicar_reel)

# ---- LOOP INFINITO ----
print("Bot de Auto-Reels iniciado 🚀")
while True:
    schedule.run_pending()
    time.sleep(60)
