# app/notion_utils.py
import os
from typing import Dict, Any
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

# Notion client + DB
notion = Client(auth=os.getenv("NOTION_API_KEY"))
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")

def log_audit_to_notion(result: Dict[str, Any]) -> bool:
    """
    Logs audit results (before/after, risk, status) to Notion for visibility.
    """
    try:
        notion.pages.create(
            parent={"database_id": NOTION_DB_ID},
            properties={
                "Before": {"rich_text": [{"text": {"content": result["original"][:2000]}}]},
                "After": {"rich_text": [{"text": {"content": (result.get('cleaned') or '')[:2000]}}]},
                "Risk": {"number": result.get("risk_score", 0)},
                "Status": {"select": {"name": result["outcome"]}},
                "Reasons": {"rich_text": [{"text": {"content": " | ".join(result.get("reasons", []))[:2000]}}]},
            }
        )
        return True
    except Exception as e:
        print(f"[Notion] Error logging audit: {e}")
        return False
