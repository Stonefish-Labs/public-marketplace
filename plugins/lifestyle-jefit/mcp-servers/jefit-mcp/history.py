import requests
import json
import os 
from dotenv import load_dotenv
from auth import get_access_token, get_user_id
load_dotenv()

def get_workout_history() -> list[str]:
    access_token = get_access_token()
    user_id = get_user_id(access_token)
    timezone_offset = os.getenv("JEFIT_TIMEZONE", "-04:00")

    headers = {
        'content-type': 'application/json',
        'Cookie': f'jefitAccessToken={access_token}'
    }
    response = requests.get(f"https://www.jefit.com/api/v2/users/{user_id}/sessions/calendar?timezone_offset={timezone_offset}", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get workout history: status={response.status_code}")
    else:
        calendar = response.json()
        calendar_data = calendar["data"]
        workouts = []
        for workout in calendar_data:
            # We will skip if the workout has no logs
            if not workout["has_logs"]:
                continue
            workouts.append(workout["date"])
        return workouts

if __name__ == "__main__":
    workouts = get_workout_history()
    print(workouts)
