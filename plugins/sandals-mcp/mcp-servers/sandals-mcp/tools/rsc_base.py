#!/usr/bin/env python3
"""
Base RSC (React Server Components) Parser
Generic functionality for parsing RSC streaming format
"""
import requests
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

class RSCParser:
    """Generic parser for React Server Components streaming format"""
    
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'next-router-prefetch': '1',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'rsc': '1',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
        }
    
    def parse_rsc_response(self, response_text: str) -> Dict[str, Any]:
        """Parse React Server Components streaming format into chunks"""
        lines = response_text.strip().split('\n')
        chunks = {}
        
        for line in lines:
            if not line.strip():
                continue
                
            # Look for chunk patterns like: 123:{"data": "value"}
            chunk_match = re.match(r'^([a-f0-9]+):(.*)', line)
            if chunk_match:
                chunk_id = chunk_match.group(1)
                chunk_data = chunk_match.group(2)
                
                try:
                    parsed_data = json.loads(chunk_data)
                    chunks[f"${chunk_id}"] = parsed_data
                except json.JSONDecodeError:
                    chunks[f"${chunk_id}"] = chunk_data
        
        return chunks
    
    def resolve_references(self, data: Any, chunks: Dict[str, Any]) -> Any:
        """Recursively resolve $xxx references in the data structure"""
        if isinstance(data, str) and data.startswith('$'):
            if data in chunks:
                resolved = chunks[data]
                return self.resolve_references(resolved, chunks)
            else:
                return data
        
        elif isinstance(data, list):
            return [self.resolve_references(item, chunks) for item in data]
        
        elif isinstance(data, dict):
            return {key: self.resolve_references(value, chunks) for key, value in data.items()}
        
        else:
            return data
    
    def fetch_rsc_data(self, url: str) -> Optional[str]:
        """Fetch RSC data from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {str(e)}")
            return None
    
    def analyze_rsc_content(self, chunks: Dict[str, Any], content_type: str, field_patterns: List[str]) -> List[Dict[str, Any]]:
        """Analyze RSC chunks to find content matching specific field patterns"""
        content_objects = []
        
        def search_nested(obj, depth=0):
            """Recursively search for content in nested structures"""
            if depth > 10:  # Prevent infinite recursion
                return
                
            if isinstance(obj, dict):
                # Check if this object matches our field patterns
                if any(field in obj for field in field_patterns):
                    content_objects.append(obj)
                    return  # Don't search deeper once we find a match
                
                # Continue searching deeper
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        search_nested(value, depth + 1)
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        search_nested(item, depth + 1)
        
        # Search through all chunks
        for chunk_data in chunks.values():
            search_nested(chunk_data)
        
        return content_objects

# Resort configuration
RESORT_CODES = {
    'sandals': {
        'SMB': 'montego-bay',
        'SRC': 'royal-caribbean', 
        'SNG': 'negril',
        'SGO': 'ochi',
        'BRP': 'royal-plantation',
        'SWH': 'south-coast',
        'SDR': 'dunns-river',
        'SRB': 'royal-bahamian',
        'SLS': 'sandals-grenada',
        'SBD': 'sandals-barbados',
        'SBR': 'royal-barbados',
        'SHC': 'halcyon-beach',
        'SLU': 'regency-la-toc',
        'SGL': 'grande-st-lucian',
        'SCR': 'royal-curacao',
        'SAT': 'grande-antigua',
        'SSV': 'sandals-saint-vincent'
    },
    'beaches': {
        'BNG': 'negril',
        'BTC': 'turks-caicos'
    }
}

def build_rsc_url(brand: str, resort_code: str, content_type: str, rsc_param: str = None) -> str:
    """Build URL for RSC endpoint"""
    base_urls = {
        'sandals': 'https://www.sandals.com',
        'beaches': 'https://www.beaches.com'
    }
    
    if brand not in RESORT_CODES or resort_code not in RESORT_CODES[brand]:
        raise ValueError(f"Unknown resort code: {resort_code}")
    
    resort_slug = RESORT_CODES[brand][resort_code]
    base_url = base_urls[brand]
    
    # Build URL based on brand and content type
    if brand == 'beaches':
        if content_type == 'rooms':
            url = f"{base_url}/resorts/{resort_slug}/rooms-suites/"
        elif content_type == 'restaurants':
            url = f"{base_url}/resorts/{resort_slug}/restaurants/"
        elif content_type == 'activities':
            url = f"{base_url}/resorts/{resort_slug}/activities/"
        else:
            url = f"{base_url}/resorts/{resort_slug}/{content_type}/"
    else:  # sandals
        if content_type == 'rooms':
            url = f"{base_url}/{resort_slug}/rooms-suites/"
        elif content_type == 'restaurants':
            url = f"{base_url}/{resort_slug}/restaurants/"
        elif content_type == 'activities':
            url = f"{base_url}/{resort_slug}/activities/"
        else:
            url = f"{base_url}/{resort_slug}/{content_type}/"
    
    if rsc_param:
        url += f"?_rsc={rsc_param}"
    
    return url

def get_brand_for_resort(resort_code: str) -> str:
    """Get brand (sandals/beaches) for a resort code"""
    for brand, resorts in RESORT_CODES.items():
        if resort_code in resorts:
            return brand
    raise ValueError(f"Unknown resort code: {resort_code}")
