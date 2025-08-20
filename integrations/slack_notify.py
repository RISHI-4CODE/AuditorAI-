import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def post_high_risk(text: str, score: int, safe_attempt: str):
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL_ID")
    if not (token and channel):
        return
    client = WebClient(token=token)
    msg = f"⚠️ High-risk output detected (score {score}).\n*Original:*\n{text}\n\n*Auto-redo attempt:*\n{safe_attempt}"
    try:
        client.chat_postMessage(channel=channel, text=msg)
    except SlackApiError:
        pass
