import httpx
from config import config
from services.base_auth import BaseAuthService

class DiscordAuthService(BaseAuthService):

    def get_authorization_url(self) -> str:
        return (
            f"https://discord.com/api/oauth2/authorize"
            f"?client_id={config.DISCORD_CLIENT_ID}"
            f"&redirect_uri={config.DISCORD_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope={config.DISCORD_SCOPE}"
        )

    async def get_access_token(self, code: str) -> str:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.DISCORD_REDIRECT_URI
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                config.DISCORD_TOKEN_URL,
                data=data,
                headers=headers,
                auth=(config.DISCORD_CLIENT_ID, config.DISCORD_CLIENT_SECRET)
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    async def get_user_info(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://discord.com/api/v10/users/@me", headers=headers)
            resp.raise_for_status()
            user = resp.json()
            user["avatar"] = (
                f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=1024"
                if user.get("avatar") else "https://cdn.discordapp.com/embed/avatars/0.png"
            )
            return user
