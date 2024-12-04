from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Union
import httpx

app = FastAPI()

# Base URL for Discord API, to be replaced with localhost
DISCORD_API_URL = 'https://discord.com/api/webhooks/{webhook_id}/{webhook_token}'

# Embed model for rich embeds (supports title, description, color, etc.)
class Embed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    author: Optional[Dict[str, Union[str, HttpUrl]]] = None  # author name and icon_url
    fields: Optional[List[Dict[str, Union[str, int]]]] = None  # list of fields
    footer: Optional[Dict[str, str]] = None  # footer with text and icon_url
    image: Optional[Dict[str, HttpUrl]] = None  # image URL
    thumbnail: Optional[Dict[str, HttpUrl]] = None  # thumbnail URL
    video: Optional[Dict[str, HttpUrl]] = None  # video URL
    provider: Optional[str] = None  # provider name
    timestamp: Optional[str] = None  # timestamp

# Allowed Mentions for controlling mentions behavior
class AllowedMentions(BaseModel):
    parse: Optional[List[str]] = None  # ['roles', 'users', 'everyone']
    users: Optional[List[str]] = None  # list of user IDs to mention
    roles: Optional[List[str]] = None  # list of role IDs to mention
    replied_user: Optional[bool] = None  # whether the mentioned user should be allowed to reply

# Attachment model for sending files (requires a URL or file data)
class Attachment(BaseModel):
    id: Optional[int] = None  # attachment ID, optional
    filename: str  # filename (required)
    content_type: Optional[str] = None  # MIME type (optional)
    size: Optional[int] = None  # size of the file (optional)
    url: Optional[HttpUrl] = None  # URL to the file (optional, for image/video)

# Main WebhookRequest model for Discord Webhook data
class WebhookRequest(BaseModel):
    content: Optional[str] = None  # The message content
    username: Optional[str] = None  # The username to send the message as
    avatar_url: Optional[HttpUrl] = None  # Avatar URL to use for the message
    embeds: Optional[List[Embed]] = None  # List of embed objects
    tts: Optional[bool] = None  # Whether the message should be sent as text-to-speech
    allowed_mentions: Optional[AllowedMentions] = None  # Mentions handling
    attachments: Optional[List[Attachment]] = None  # List of attachments
    flags: Optional[int] = None  # Message flags (bitwise value)
    components: Optional[List[Dict[str, Union[str, int]]]] = None  # Buttons, Select menus, etc.
    sticker_ids: Optional[List[int]] = None  # Sticker IDs for stickers to send with the message

@app.post("/api/webhooks/{webhook_id}/{webhook_token}")
async def proxy(webhook_id: str, webhook_token: str, body: WebhookRequest):
    # Construct the actual Discord webhook URL by replacing the discord.com with localhost:8000
    discord_url = DISCORD_API_URL.format(webhook_id=webhook_id, webhook_token=webhook_token)
    
    # Use httpx to send the POST request asynchronously
    async with httpx.AsyncClient() as client:
        response = await client.post(discord_url, json=body.dict(exclude_unset=True))  # exclude_unset excludes None values
    
    # Check if the request was successful
    if response.status_code == 204:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
