from fastapi import FastAPI, Request
import httpx

app = FastAPI()

CLIENT_ID = "5bb733cbaa7e427eaff9df6ee42fa2ca"
CLIENT_SECRET = "936020118acd491e88122f4daf9dd3ef"
BOT_TOKEN = "7692757705:AAEIb8qW2n3l0W-_VNYc4t-OXAyyrdyKYOs"

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
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": state,
                    "text": "✅ Доступ к Яндексу получен! Токен сохранён."
                }
            )
            return {"status": "ok", "access_token": access_token}
        else:
            return {"error": "Failed to get token", "response": token_data}