from flask import Flask, request, jsonify, abort
import requests
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Union
import json

app = Flask(__name__)

# Discord Webhook API URL template
DISCORD_API_URL = 'https://discord.com/api/webhooks/{webhook_id}/{webhook_token}'

# Define models with Pydantic to validate incoming data
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

class AllowedMentions(BaseModel):
    parse: Optional[List[str]] = None  # ['roles', 'users', 'everyone']
    users: Optional[List[str]] = None  # list of user IDs to mention
    roles: Optional[List[str]] = None  # list of role IDs to mention
    replied_user: Optional[bool] = None  # whether the mentioned user should be allowed to reply

class Attachment(BaseModel):
    id: Optional[int] = None  # attachment ID, optional
    filename: str  # filename (required)
    content_type: Optional[str] = None  # MIME type (optional)
    size: Optional[int] = None  # size of the file (optional)
    url: Optional[HttpUrl] = None  # URL to the file (optional, for image/video)

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

@app.route('/api/webhooks/<webhook_id>/<webhook_token>', methods=['POST'])
def proxy(webhook_id: str, webhook_token: str):
    # Parse incoming JSON data and validate it using Pydantic model
    try:
        body = WebhookRequest.parse_obj(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Construct the Discord webhook URL
    discord_url = DISCORD_API_URL.format(webhook_id=webhook_id, webhook_token=webhook_token)

    # Prepare the data to be sent to Discord (convert to a dictionary and exclude unset values)
    data = body.dict(exclude_unset=True)

    # Send the request to Discord via the requests library
    response = requests.post(discord_url, json=data)

    # Check if Discord's API responded with a success status (204 No Content)
    if response.status_code == 204:
        return jsonify({"status": "success"}), 200
    else:
        # If there's an error, pass through the Discord error message
        return jsonify({"error": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
