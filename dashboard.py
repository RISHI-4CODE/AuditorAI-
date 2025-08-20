import streamlit as st
from notion_client import Client
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
# Load Notion API credentials
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=NOTION_API_KEY)

st.set_page_config(page_title="AI Auditor Dashboard", layout="wide")

st.title("📊 AI Auditor - Live Dashboard")

def fetch_audit_logs():
    """Fetch audit results from Notion DB"""
    try:
        response = notion.databases.query(database_id=NOTION_DB)
        results = []
        for row in response["results"]:
            props = row["properties"]
            results.append({
                "Task": props["Task"]["title"][0]["text"]["content"] if props["Task"]["title"] else "N/A",
                "status": props["status"]["select"]["name"] if props["status"]["select"] else "N/A",
                "timestamp": props["timestamp"]["date"]["start"] if props["timestamp"]["date"] else "N/A",
                "details": props["details"]["rich_text"][0]["text"]["content"] if props["details"]["rich_text"] else "N/A"
            })
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return pd.DataFrame()

# Fetch & display data
df = fetch_audit_logs()

if not df.empty:
    st.subheader("📋 Audit Logs")
    st.dataframe(df)

    st.subheader("📊 Audit Summary")
    summary = df["status"].value_counts().reset_index()
    summary.columns = ["status", "Count"]
    st.bar_chart(summary.set_index("status"))
else:
    st.info("No audit logs found yet. Run AuditorAgent to populate data.")
