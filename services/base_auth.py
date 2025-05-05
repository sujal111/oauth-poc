from abc import ABC, abstractmethod

class BaseAuthService(ABC):

    @abstractmethod
    def get_authorization_url(self) -> str:
        pass

    @abstractmethod
    async def get_access_token(self, code: str) -> str:
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict:
        pass
