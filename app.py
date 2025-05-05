from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from services.provider_factory import get_auth_service

app = FastAPI()

@app.get("/auth/{provider}/login")
async def auth_login(provider: str):
    try:
        auth_service = get_auth_service(provider)
        auth_url = auth_service.get_authorization_url()
        return RedirectResponse(url=auth_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/{provider}/callback")
async def auth_callback(provider: str, code: str = None):
    try:
        auth_service = get_auth_service(provider)
        access_token = await auth_service.get_access_token(code)
        user_info = await auth_service.get_user_info(access_token)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth failed: {str(e)}")
