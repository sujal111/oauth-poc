import os

class config:
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
    DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
    DISCORD_SCOPE = "identify email"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"



