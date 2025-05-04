from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import httpx
from config import config  

load_dotenv()

app = FastAPI()


provider_config = {
    "discord": {
        "client_id": config.DISCORD_CLIENT_ID,
        "client_secret": config.DISCORD_CLIENT_SECRET,
        "auth_url": "https://discord.com/api/oauth2/authorize",
        "token_url": config.DISCORD_TOKEN_URL,
        "redirect_uri": config.DISCORD_REDIRECT_URI,
        "scope": config.DISCORD_SCOPE,
        "user_info_url": "https://discord.com/api/v10/users/@me",
        "get_user_avatar": lambda user: f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=1024"
        if user.get("avatar") else "https://cdn.discordapp.com/embed/avatars/0.png"
    },
   
}

@app.get("/auth/{provider}/login")
async def auth_login(provider: str):
    """Redirect user to OAuth provider authorization URL"""
    provider_data = provider_config.get(provider.lower())
    if not provider_data:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    auth_url = (
        f"{provider_data['auth_url']}?client_id={provider_data['client_id']}"
        f"&redirect_uri={provider_data['redirect_uri']}"
        f"&response_type=code"
        f"&scope={provider_data['scope']}"
    )
    return RedirectResponse(url=auth_url)


@app.get("/auth/{provider}/callback")
async def auth_callback(provider: str, request: Request, code: str = None, state: str = None):
    """Handle callback from OAuth provider and exchange code for access token"""
    provider_data = provider_config.get(provider.lower())
    if not provider_data:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    try:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": provider_data["redirect_uri"],
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                provider_data["token_url"],
                data=data,
                headers=headers,
                auth=(provider_data["client_id"], provider_data["client_secret"])
            )
            token_response.raise_for_status()
            access_token = token_response.json().get("access_token")
            return await fetch_user_info(provider, access_token)
    except httpx.HTTPStatusError as e:
        return {"error": f"Token exchange failed: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}


async def fetch_user_info(provider: str, access_token: str):
    """Fetch user information from the OAuth provider"""
    provider_data = provider_config.get(provider.lower())
    if not provider_data:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient() as client:
            user_response = await client.get(provider_data["user_info_url"], headers=headers)
            user_response.raise_for_status()
            user = user_response.json()
            if "get_user_avatar" in provider_data:
                user["avatar"] = provider_data["get_user_avatar"](user)
            return user
    except Exception as e:
        return {"error": f"Failed to fetch user info: {str(e)}"}
