# Made by ZV800
# https://github.com/zv8001/discord_webhook_proxy/tree/main

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Union
import httpx

app = FastAPI()

DISCORD_API_URL = 'https://discord.com/api/webhooks/{webhook_id}/{webhook_token}'

class Embed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    author: Optional[Dict[str, Union[str, HttpUrl]]] = None
    fields: Optional[List[Dict[str, Union[str, int]]]] = None
    footer: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, HttpUrl]] = None
    thumbnail: Optional[Dict[str, HttpUrl]] = None
    video: Optional[Dict[str, HttpUrl]] = None
    provider: Optional[str] = None
    timestamp: Optional[str] = None

class AllowedMentions(BaseModel):
    parse: Optional[List[str]] = None
    users: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    replied_user: Optional[bool] = None

class Attachment(BaseModel):
    id: Optional[int] = None
    filename: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    url: Optional[HttpUrl] = None

class WebhookRequest(BaseModel):
    content: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    embeds: Optional[List[Embed]] = None
    tts: Optional[bool] = None
    allowed_mentions: Optional[AllowedMentions] = None
    attachments: Optional[List[Attachment]] = None
    flags: Optional[int] = None
    components: Optional[List[Dict[str, Union[str, int]]]] = None
    sticker_ids: Optional[List[int]] = None

@app.post("/api/webhooks/{webhook_id}/{webhook_token}")
async def proxy(webhook_id: str, webhook_token: str, body: WebhookRequest):
    discord_url = DISCORD_API_URL.format(webhook_id=webhook_id, webhook_token=webhook_token)
    async with httpx.AsyncClient() as client:
        response = await client.post(discord_url, json=body.dict(exclude_unset=True))
    if response.status_code == 204:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/api/webhooks/{webhook_id}/{webhook_token}")
async def webhook_info(webhook_id: str, webhook_token: str):
    return {
        "status": "online",
        "message": "Discord Webhook Proxy is running.",
        "webhook_id": webhook_id
    }

@app.get("/")
async def root():
    return {"status": "ok", "message": "Proxy is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
