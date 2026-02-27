import requests
import json
import re
from typing import Dict, Any, Optional, List
class RSCParser:
    """Generic parser for React Server Components streaming format"""
    
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
    
    def fetch_rsc_data(self, url: str, headers: Dict[str, str]) -> Optional[str]:
        """Fetch RSC data from URL"""
        try:
            response = requests.get(url, headers=headers, timeout=30)
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
