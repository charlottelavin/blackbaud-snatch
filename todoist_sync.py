from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv
import json
import os

load_dotenv()

ID_FILE = "synced_ids.json"

def load_synced_ids():
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_synced_ids(ids):
    with open(ID_FILE, "w") as f:
        json.dump(list(ids), f)

TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
api = TodoistAPI(TODOIST_API_TOKEN)

def sync_assignment(assignment):
    assignment_id = assignment['id']
    title = assignment['title']
    class_name = assignment['class_name']
    due_date = assignment['due_date']
    content = f"{title}"
    synced_ids = load_synced_ids()

    if assignment_id in synced_ids:
        print(f"🔁 Already synced: {content}")
        return
    api.add_task(
        content=content,
        due_string=due_date,
        labels=[class_name]
    )
    print(f"➕ Created task: {content}")

    # Save new ID
    synced_ids.add(assignment_id)
    save_synced_ids(synced_ids)
