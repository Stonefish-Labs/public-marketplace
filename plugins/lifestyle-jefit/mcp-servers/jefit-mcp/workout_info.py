"""
Get complete workout information for a specific date.
This script fetches workout logs from the API and enriches them with 
exercise details (names, muscle groups, equipment) from the cached database.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
from auth import get_access_token, get_user_id

def fetch_exercise_database() -> dict[str, dict]:
    """Fetch the full exercise database from RSC endpoint"""
    from rsc_base import RSCParser
    
    rsc_parser = RSCParser()
    headers = {
        'rsc': '1',
        'Cookie': f'jefitAccessToken={get_access_token()}'
    }
    
    response = requests.get("https://www.jefit.com/my-jefit/progress/history", headers=headers)
    chunks = rsc_parser.parse_rsc_response(response.text)
    
    exercises_db = {}
    
    def extract_exercises(data, depth=0):
        if depth > 15:
            return
        
        if isinstance(data, dict):
            # Check if this is an exercise definition
            if 'id' in data and 'name' in data and 'body_parts' in data:
                exercises_db[data['id']] = {
                    'id': data['id'],
                    'name': data['name'],
                    'body_parts': [bp for bp in data.get('body_parts', []) if bp != 'none'],
                    'equipment': [eq for eq in data.get('equipment', []) if eq != 'none'],
                    'input_format': data.get('input_format'),
                    'popularity': data.get('popularity')
                }
            
            for value in data.values():
                if isinstance(value, (dict, list)):
                    extract_exercises(value, depth + 1)
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    extract_exercises(item, depth + 1)
    
    for chunk_data in chunks.values():
        extract_exercises(chunk_data)
    
    return exercises_db


def load_exercise_db() -> dict[str, dict]:
    """Load exercise database from JSON cache, creating it if necessary"""
    db_path = Path('data/exercises_db.json')
    
    # Create data directory if it doesn't exist
    db_path.parent.mkdir(exist_ok=True)
    
    # If database doesn't exist, fetch and create it
    if not db_path.exists():
        print("Exercise database not found. Fetching from JEFit...")
        try:
            exercises = fetch_exercise_database()
            
            if not exercises:
                print("⚠️  No exercises found. Check your authentication.")
                return {}
            
            # Save to JSON
            with open(db_path, 'w') as f:
                json.dump(exercises, f, indent=2)
            
            print(f"✓ Created exercise database with {len(exercises)} exercises")
            return exercises
            
        except Exception as e:
            print(f"⚠️  Failed to fetch exercise database: {e}")
            return {}
    
    # Load existing database
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading exercise database: {e}")
        return {}

def get_workout_for_date(date_str: str) -> dict:
    """Get workout logs for a specific date"""
    date_unix = int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))
    # Get Access Token and User ID
    access_token = get_access_token()
    user_id = get_user_id(access_token)
    url = f"https://www.jefit.com/api/v2/users/{user_id}/sessions?startDate={date_unix}"
    headers = {
        'content-type': 'application/json',
        'Cookie': f'jefitAccessToken={access_token}'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get workout details: status={response.status_code}")
    return response.json()


def format_workout_markdown(
    date_str: str,
    workout_data: dict,
    exercise_db: dict[str, dict],
) -> str:
    """Format workout API response data as markdown text."""
    output_lines = [f"# Workout for {date_str}\n"]

    if "data" not in workout_data or not workout_data["data"]:
        output_lines.append("No workout found for this date.")
        return "\n".join(output_lines)

    for session in workout_data["data"]:
        session_date = datetime.fromtimestamp(session["date"]).strftime("%Y-%m-%d %H:%M:%S")
        duration_minutes = session["total_time"] // 60
        duration_seconds = session["total_time"] % 60
        total_weight = session["total_weight"]

        output_lines.append(f"**Started:** {session_date}")
        output_lines.append(f"**Duration:** {duration_minutes}m {duration_seconds}s")
        output_lines.append(f"**Weight Lifted:** {total_weight} lbs\n")
        output_lines.append("## Exercises\n")

        for index, log in enumerate(session["logs"], 1):
            exercise_id = log["exercise_id"]
            exercise = exercise_db.get(exercise_id, {})

            name = exercise.get("name", f"Unknown Exercise ({exercise_id})")
            muscle_groups = ", ".join(exercise.get("body_parts", ["Unknown"]))
            equipment = ", ".join(exercise.get("equipment", ["Unknown"]))

            output_lines.append(f"### {index}. {name}")
            output_lines.append(f"- **Muscle Groups:** {muscle_groups}")
            output_lines.append(f"- **Equipment:** {equipment}")
            output_lines.append("")

            for set_index, set_item in enumerate(log["log_sets"], 1):
                weight = set_item.get("weight", 0)
                reps = set_item.get("reps", 0)
                output_lines.append(f"  - Set {set_index}: {weight} lbs x {reps} reps")

            output_lines.append("")

    return "\n".join(output_lines)
