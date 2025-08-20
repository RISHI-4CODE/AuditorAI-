import os
from notion_client import Client

def log_to_notion(input_text: str, score: int, status: str, output_text: str = ""):
    key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DB_ID")
    if not (key and db_id):
        return
    notion = Client(auth=key)
    properties = {
        "Title": {"title": [{"text": {"content": input_text[:50] + ("..." if len(input_text)>50 else "")}}]},
        "Risk": {"number": score},
        "Status": {"select": {"name": status}},
    }
    children = []
    if output_text:
        children.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":output_text}}]}})
    notion.pages.create(parent={"database_id": db_id}, properties=properties, children=children)
