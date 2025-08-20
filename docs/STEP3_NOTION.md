# Step 3: Notion Integration

### What we did
- Connected project to Notion API using `notion_client`.
- Created environment variables:
  - `NOTION_API_KEY` → integration secret from Notion
  - `NOTION_DATABASE_ID` → database where audit logs are stored
- Updated `auditor_agent.py` to log each audit result into Notion with the following fields:
  - **Name** (Title)
  - **Status** (Select)
  - **Timestamp** (Date)
  - **Details** (Text)

### Debugging
- Added `notion_debug.py` to print property names & types for the database.
- Fixed property names to match Notion schema exactly (case-sensitive).

### Output
- When running the agent, results are sent to both:
  - **Slack** (for instant alerts)
  - **Notion** (for structured storage)
