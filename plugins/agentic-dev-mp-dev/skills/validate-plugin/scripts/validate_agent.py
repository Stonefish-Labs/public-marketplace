#!/usr/bin/env python3
import os
import sys

def validate_agent(file_path):
    if not os.path.exists(file_path):
        return False, f"Agent file not found: {file_path}"
    
    if not file_path.endswith('.md'):
        return False, f"Agent file must be a Markdown (.md) file: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return False, f"Agent file is empty: {file_path}"
    except Exception as e:
        return False, f"Error reading agent file: {e}"
        
    return True, f"Agent valid: {file_path}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_agent.py <path_to_agent.md>")
        sys.exit(1)
        
    success, message = validate_agent(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
