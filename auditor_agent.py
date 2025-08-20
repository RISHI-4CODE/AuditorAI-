import os
from datetime import datetime
from slack_sdk import WebClient
from notion_client import Client
from dotenv import load_dotenv

# Load keys from .env
load_dotenv()



# Slack setup
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")

# Notion setup
notion = Client(auth=os.getenv("NOTION_API_KEY"))
NOTION_DB = os.getenv("NOTION_DATABASE_ID")


def log_to_slack(message: str):
    """Send a message to Slack channel."""
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
        print(f"✅ Sent to Slack: {message}")
    except Exception as e:
        print(f"❌ Slack error: {e}")



def log_to_notion(task: str, status: str, details: str = ""):
    """Add an entry to Notion Audit Logs DB."""
    try:
        print(f"Using Notion DB: {NOTION_DB}")

        notion.pages.create(
        parent={"database_id": NOTION_DB},
        properties={
            # This must map to your "Name" column (title type)
            "Task": {
                "title": [
                    {"text": {"content": task}}
                ]
            },

            # Status is a Select, so it must use {"select": {"name": "VALUE"}}
            "status": {
                "select": {"name": status}
            },

            # Timestamp is a Date, so it must use {"date": {"start": "..."}}
            "timestamp": {
                "date": {"start": datetime.utcnow().isoformat()}
            },

            # Details is Rich Text (called "Text" in Notion UI), so it must use {"rich_text": [...]}
            "details": {
                "rich_text": [
                    {"text": {"content": details}}
                ]
            }
        },
        )
        print(f"✅ Logged to Notion: {task} -> {status}")

    except Exception as e:
        print(f"❌ Notion error: {e}")


# Example function (later plug real audits here)
from audits.basic_checks import run_basic_audits
from audits.ai_audits import run_ai_audit

# Inside main()
audits = run_basic_audits()

# Add AI-powered audit on some dummy code
ai_result = run_ai_audit("def add(a, b): return a + b")
audits.append(ai_result)

for audit in audits:
    msg = f"📢 Audit Result: {audit['task']} - {audit['status']}"
    log_to_slack(msg)
    log_to_notion(audit['task'], audit['status'], audit['details'])
