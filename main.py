from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

# Константы (подставим реальные данные)
CLIENT_ID = "5bb733cbaa7e427eaff9df6ee42fa2ca"
CLIENT_SECRET = "936020118acd491e88122f4daf9dd3ef"
BOT_TOKEN = "7692757705:AAEIb8qW2n3l0W-_VNYc4t-OXAyyrdyKYOs"  # токен Telegram-бота

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "code not provided"}

    # Обмениваем code на access_token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Отправим сообщение в Telegram (заглушка: просто админу)
    if access_token:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": "7692757705",  # временно — твой Telegram ID
                "text": "✅ Доступ к Яндексу получен! Токен сохранён."
            }
        )
        return {"status": "ok", "access_token": access_token}
    else:
        return {"error": "Failed to get token", "response": token_data}
