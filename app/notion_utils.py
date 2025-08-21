# app/notion_utils.py
import os
from notion_client import Client
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_API_KEY"))

# Notion DB where audit results will be stored
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")

def log_audit_to_notion(result: Dict[str, Any]):
    """
    Logs an audit result dictionary into the Notion database.
    """
    try:
        notion.pages.create(
            parent={"database_id": NOTION_DB_ID},
            properties={
                "Original": {"title": [{"text": {"content": " | ".join(result["reasons"])}}]},
                "Findings": {"rich_text": [{"text": {"content": str(result["findings"])}}]},
                "Reasons": {"rich_text": [{"text": {"content": result["original"][:2000]}}]},  # limit size
                "Outcome": {"select": {"name": result["outcome"]}},

            }
        )
        return True
    except Exception as e:
        print(f"[Notion] Error logging audit: {e}")
        return False


def fetch_audit_logs(limit: int = 20):
    """
    Fetch recent audit logs from Notion.
    """
    try:
        response = notion.databases.query(
            database_id=NOTION_DB_ID,
            page_size=limit,
            sorts=[{"property": "Created", "direction": "descending"}]
        )
        return response.get("results", [])
    except Exception as e:
        print(f"[Notion] Error fetching logs: {e}")
        return []
