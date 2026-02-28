#!/usr/bin/env python3
"""
Update the exercise database cache from JEFit RSC endpoint.
Run this manually to refresh the exercise database when needed.
The database is also automatically created on first startup if missing.
"""

import json
from pathlib import Path
from workout_info import fetch_exercise_database

if __name__ == "__main__":
    try:
        print("Fetching exercise database from JEFit...")
        exercises = fetch_exercise_database()
        
        if not exercises:
            print("❌ No exercises found. Check your auth token.")
            exit(1)
        
        # Ensure data directory exists
        db_path = Path('data/exercises_db.json')
        db_path.parent.mkdir(exist_ok=True)
        
        # Save to JSON
        with open(db_path, 'w') as f:
            json.dump(exercises, f, indent=2)
        
        print(f"✓ Successfully updated {db_path}")
        print(f"✓ Total exercises: {len(exercises)}")
        
        # Show some stats
        system_exercises = sum(1 for ex_id in exercises.keys() if ex_id.startswith('d_'))
        custom_exercises = sum(1 for ex_id in exercises.keys() if ex_id.startswith('u_'))
        
        print(f"  - System exercises: {system_exercises}")
        print(f"  - Custom exercises: {custom_exercises}")
        
    except Exception as e:
        print(f"❌ Error updating exercise database: {e}")
        exit(1)

