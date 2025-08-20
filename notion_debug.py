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
        "status": {"select": {"name": "Pending"}},
        "timestamp": {"date": {"start": datetime.now().isoformat()}},
        "details": {"rich_text": [{"text": {"content": "This is a test log from AuditorAgent setup."}}]},
    },
)

print("✅ Entry added to Notion:", response["id"])
