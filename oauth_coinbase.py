import os
from dotenv import load_dotenv

# Carica le variabili dal file .env
load_dotenv()

CLIENT_ID = os.getenv("COINBASE_CLIENT_ID")
CLIENT_SECRET = os.getenv("COINBASE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("COINBASE_REDIRECT_URI")
AUTH_URL = os.getenv("COINBASE_AUTH_URL")

print("🔍 Debug variabili ambiente:")
print(f"CLIENT_ID: {CLIENT_ID}")
print(f"CLIENT_SECRET: {CLIENT_SECRET}")
print(f"REDIRECT_URI: {REDIRECT_URI}")
print(f"AUTH_URL: {AUTH_URL}")

def get_coinbase_auth_url():
    """
    Genera l'URL per autenticarsi su Coinbase con OAuth.
    """
    if not CLIENT_ID or not REDIRECT_URI or not AUTH_URL:
        print("❌ ERRORE: Alcune variabili di ambiente mancanti nel file .env!")
        return

    url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=wallet:accounts:read,wallet:buys:read,wallet:transactions:read"
    print(f"\n🔗 Apri questo link nel browser per autorizzare l'app:\n{url}")

import requests

TOKEN_URL = "https://api.coinbase.com/oauth/token"

def refresh_access_token():
    """
    Usa il refresh token per ottenere un nuovo access token.
    """
    REFRESH_TOKEN = os.getenv("COINBASE_REFRESH_TOKEN")
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        new_access_token = token_data['access_token']
        new_refresh_token = token_data.get('refresh_token', REFRESH_TOKEN)

        # Aggiorna il file .env con il nuovo token
        with open(".env", "w") as env_file:
            env_file.write(f"COINBASE_ACCESS_TOKEN={new_access_token}\n")
            env_file.write(f"COINBASE_REFRESH_TOKEN={new_refresh_token}\n")

        print("✅ Access Token aggiornato con successo!")
        return new_access_token
    else:
        print(f"❌ Errore nel rinnovo del token: {token_data}")
        return None


def get_access_token(auth_code):
    """
    Scambia il codice di autorizzazione per un Access Token.
    """
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(TOKEN_URL, data=data)
    token_data = response.json()
    
    if "access_token" in token_data and "refresh_token" in token_data:
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']

        print(f"✅ Access Token ottenuto: {access_token}")
        print(f"🔄 Refresh Token ottenuto: {refresh_token}")

        # Salviamo il nuovo token nel file .env
        with open(".env", "a") as env_file:
            env_file.write(f"\nCOINBASE_ACCESS_TOKEN={access_token}\n")
            env_file.write(f"\nCOINBASE_REFRESH_TOKEN={refresh_token}\n")

        print("✅ Token e Refresh Token salvati nel file .env!")
        return access_token
    else:
        print(f"❌ Errore nell'ottenere il token: {token_data}")
        return None

if __name__ == "__main__":
    get_coinbase_auth_url()
