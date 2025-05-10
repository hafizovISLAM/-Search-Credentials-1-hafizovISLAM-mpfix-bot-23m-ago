from fastapi import FastAPI, Request
import httpx
import json
import os
from datetime import datetime

app = FastAPI()

CLIENT_ID = "5bb733cbaa7e427eaff9df6ee42fa2ca"
CLIENT_SECRET = "936020118acd491e88122f4daf9dd3ef"
BOT_TOKEN = "7692757705:AAEIb8qW2n3l0W-_VNYc4t-OXAyyrdyKYOs"

TOKEN_FILE = "tokens.json"

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # telegram_user_id

    if not code or not state:
        return {"error": "Missing code or state"}

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

        if access_token:
            # Отправка уведомления в Telegram
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": state,
                    "text": "✅ Доступ к Яндексу получен! Токен сохранён."
                }
            )

            # Сохраняем токен в файл
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "r") as f:
                    token_store = json.load(f)
            else:
                token_store = {}

            token_store[state] = {
                "access_token": access_token,
                "created_at": datetime.utcnow().isoformat()
            }

            with open(TOKEN_FILE, "w") as f:
                json.dump(token_store, f, indent=2)

            return {"status": "ok", "access_token": access_token}
        else:
            return {"error": "Failed to get token", "response": token_data}

@app.get("/token")
async def get_token(telegram_id: str):
    if not os.path.exists(TOKEN_FILE):
        return {"error": "not_found"}

    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)

    if telegram_id not in tokens:
        return {"error": "not_found"}

    return {"access_token": tokens[telegram_id]["access_token"]}
