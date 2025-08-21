import os
from notion_client import Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_API_KEY"))
database_id = os.getenv("NOTION_DATABASE_ID")

response = notion.pages.create(
    parent={"database_id": database_id},
    properties={
        "Task": {"title": [{"text": {"content": "Test Audit Entry"}}]},
        "status": {"rich_text": {"name": "Pending"}},
        "timestamp": {"rich_text": {"start": datetime.now().isoformat()}},
        "Outcome": {"": [{"text": {"content": "This is a test log from AuditorAgent setup."}}]},
    },
)

print("✅ Entry added to Notion:", response["id"])
