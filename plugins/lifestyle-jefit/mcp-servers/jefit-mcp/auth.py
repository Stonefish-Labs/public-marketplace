import requests
import json
from hashlib import md5
from dotenv import load_dotenv
import os

# Yes - you read that right. You log in with raw MD5 hash of your password.
# Note to Self: Do not use sensitive password on JEFit.

load_dotenv()

def get_access_token() -> str:
    """Login and return a fresh access token."""
    username = os.getenv("JEFIT_USERNAME")
    password = os.getenv("JEFIT_PASSWORD")
    
    if not username or not password:
        raise Exception("JEFIT_USERNAME and JEFIT_PASSWORD must be set in .env")
    
    data = {
        "platform": "web",
        "username": username,
        "passwordMd5": md5(password.encode()).hexdigest()
    }

    response = requests.post(
        "https://www.jefit.com/api/v2/auth/login",
        headers={'content-type': 'application/json'},
        data=json.dumps(data)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to login to JEFit: status={response.status_code}")
    
    return response.json()['accessToken']


def get_user_id(access_token: str) -> str:
    """Get user info from JEFit."""
    headers = {
        'content-type': 'application/json',
        'Cookie': f'jefitAccessToken={access_token}'
    }
    response = requests.get("https://www.jefit.com/api/v2/user", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get user info from JEFit: status={response.status_code}")
    else:
        return response.json()['data']['id']
