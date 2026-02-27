"""
MyFitnessPal API Client

Wrapper around the python-myfitnesspal library (local copy from GitHub).
Supports both browser cookie authentication and environment-based cookies.
"""

import sys
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Optional
from http.cookiejar import Cookie, CookieJar

# Add myfitnesspal library to path
myfitnesspal_path = Path(__file__).parent / "myfitnesspal"
sys.path.insert(0, str(myfitnesspal_path))


class MyFitnessPalClient:
    """Simplified client wrapping python-myfitnesspal library"""
    
    def __init__(self, cookies_json: str | None = None):
        """
        Initialize client using cookies from profile/env fallback or browser.
        
        Priority:
        1. Pre-resolved cookie payload from config profile
        2. Browser cookies (for local development)
        """
        import myfitnesspal

        cookiejar = self._load_cookies_from_json(cookies_json)
        
        if cookiejar:
            # Use cookies from environment
            self.client = myfitnesspal.Client(cookiejar=cookiejar)
        else:
            # Fall back to browser cookies
            self.client = myfitnesspal.Client()
    
    def _load_cookies_from_json(self, cookies_json: str | None) -> Optional[CookieJar]:
        """Load cookies from pre-resolved JSON payload if present."""
        if not cookies_json:
            return None
        
        try:
            cookie_dict = json.loads(cookies_json)
            jar = CookieJar()
            
            for name, data in cookie_dict.items():
                cookie = Cookie(
                    version=0,
                    name=name,
                    value=data['value'],
                    port=None,
                    port_specified=False,
                    domain=data.get('domain', '.myfitnesspal.com'),
                    domain_specified=True,
                    domain_initial_dot=data.get('domain', '').startswith('.'),
                    path=data.get('path', '/'),
                    path_specified=True,
                    secure=data.get('secure', False),
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={},
                    rfc2109=False
                )
                jar.set_cookie(cookie)
            
            return jar
            
        except Exception:
            return None
    
    def get_day(self, target_date: date):
        """
        Get complete day data including meals, exercise, water, and notes.
        
        Returns a Day object with:
        - meals: List of Meal objects with entries
        - totals: Dict of total nutrition (calories, carbs, fat, protein, etc.)
        - goals: Dict of daily goals
        - water: Float (water intake)
        - exercises: List of Exercise objects
        - notes: String (food notes)
        - complete: Boolean (whether day is marked complete)
        """
        return self.client.get_date(target_date)
    
    def get_date_range(self, start_date: date, end_date: date):
        """
        Get data for multiple days.
        
        Yields Day objects for each date in the range.
        """
        current = start_date
        while current <= end_date:
            try:
                yield self.get_day(current)
            except Exception:
                # Skip days with errors
                pass
            current = current + timedelta(days=1)
