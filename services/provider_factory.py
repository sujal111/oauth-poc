from services.discord_auth import DiscordAuthService

provider_mapping = {
    "discord": DiscordAuthService,
    # "google": GoogleAuthService,
    # "github": GithubAuthService
}

def get_auth_service(provider: str):
    provider = provider.lower()
    if provider not in provider_mapping:
        raise ValueError(f"Unsupported provider: {provider}")
    return provider_mapping[provider]()
