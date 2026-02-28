#!/usr/bin/env python3
import os
import sys
import json

def validate_hook(file_path):
    if not os.path.exists(file_path):
        return False, f"Hook file not found: {file_path}"
    
    if not file_path.endswith('.json'):
        return False, f"Hook file must be a JSON (.json) file: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                return False, f"Hook file should contain a JSON array: {file_path}"
            for idx, hook in enumerate(data):
                if not isinstance(hook, dict):
                    return False, f"Hook at index {idx} must be an object: {file_path}"
                if not isinstance(hook.get("event"), str) or not hook["event"].strip():
                    return False, f"Hook at index {idx} missing required 'event' string: {file_path}"
                if not isinstance(hook.get("command"), str) or not hook["command"].strip():
                    return False, f"Hook at index {idx} missing required 'command' string: {file_path}"
                if "pattern" in hook and not isinstance(hook["pattern"], str):
                    return False, f"Hook at index {idx} has non-string 'pattern': {file_path}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in hook file: {e}"
    except Exception as e:
        return False, f"Error reading hook file: {e}"
        
    return True, f"Hook valid: {file_path}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_hook.py <path_to_hook.json>")
        sys.exit(1)
        
    success, message = validate_hook(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
