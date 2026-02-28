#!/usr/bin/env python3
import os
import sys
import re
import argparse

def validate_name(name):
    """Validate that the skill name is strictly kebab-case."""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"Error: Skill name '{name}' must be kebab-case.")
        sys.exit(1)

def validate_no_xml(text, field_name):
    """Validate that the given text does not contain any XML tags."""
    if text and ('<' in text or '>' in text):
        print(f"Error: XML tags (< or >) are not allowed in the {field_name}.")
        sys.exit(1)

def create_skill(name, description, hide=False, with_subfolders=False, license=None, compatibility=None, author=None, version="1.0.0", mcp_server=None, category=None, tags=None, target_dir=".", link_to_plugin=None, python_version=None, dependencies=None):
    """Create a new skill folder with SKILL.md and progressive disclosure subfolders."""
    validate_name(name)
    validate_no_xml(name, "name")
    validate_no_xml(description, "description")
    
    skill_dir = os.path.join(target_dir, name)
    os.makedirs(skill_dir, exist_ok=True)
    
    # Always create standard subfolders for progressive disclosure as per docs
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "references"), exist_ok=True)
    print(f"Created subfolders for progressive disclosure: scripts/, assets/, references/")
    
    file_path = os.path.join(skill_dir, "SKILL.md")
    with open(file_path, "w") as f:
        f.write("---\n")
        f.write(f"name: {name}\n")
        f.write(f"description: {description}\n")
        
        if hide:
            f.write("user-invocable: false\n")
            
        if license:
            validate_no_xml(license, "license")
            f.write(f"license: {license}\n")
            
        if compatibility:
            validate_no_xml(compatibility, "compatibility")
            f.write(f"compatibility: {compatibility}\n")
            
        has_metadata = any([author, version, mcp_server, category, tags])
        if has_metadata:
            f.write("metadata:\n")
            if author:
                validate_no_xml(author, "author")
                f.write(f"  author: {author}\n")
            if version:
                validate_no_xml(version, "version")
                f.write(f"  version: {version}\n")
            if mcp_server:
                validate_no_xml(mcp_server, "mcp-server")
                f.write(f"  mcp-server: {mcp_server}\n")
            if category:
                validate_no_xml(category, "category")
                f.write(f"  category: {category}\n")
            if tags:
                validate_no_xml(tags, "tags")
                # format as a yaml list
                tag_list = [t.strip() for t in tags.split(",")]
                f.write(f"  tags: {tag_list}\n".replace("'", '"'))
                
        f.write("---\n\n")
        f.write(f"# {name}\n\n")
        
        if dependencies:
            f.write("## Prerequisites\n\n")
            f.write("- [uv](https://docs.astral.sh/uv/) — Python package runner (handles dependencies automatically)\n")
            f.write("  ```bash\n")
            f.write("  curl -LsSf https://astral.sh/uv/install.sh | sh\n")
            f.write("  ```\n\n")
        
        f.write("## Usage\n")
        f.write("Explain how to use the skill here.\n")
        
        if dependencies:
            f.write("\nExample execution with `uv`:\n")
            f.write("```bash\n")
            f.write(f"uv run scripts/example.py\n")
            f.write("```\n")
    
    print(f"Skill '{name}' scaffolded at {file_path}")

    # Create an example script if dependencies are provided
    if dependencies:
        script_path = os.path.join(skill_dir, "scripts", "example.py")
        with open(script_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# /// script\n")
            if python_version:
                f.write(f'# requires-python = "{python_version}"\n')
            f.write("# dependencies = [\n")
            for dep in [d.strip() for d in dependencies.split(",")]:
                if dep:
                    f.write(f'#     "{dep}",\n')
            f.write("# ]\n")
            f.write("# ///\n\n")
            f.write("print('Hello from uv-powered script!')\n")
        print(f"Created example script with dependencies at {script_path}")

    if link_to_plugin:
        import json
        if os.path.exists(link_to_plugin):
            try:
                with open(link_to_plugin, 'r') as f:
                    plugin_data = json.load(f)
                
                if "skills" not in plugin_data:
                    plugin_data["skills"] = []
                
                # Check if already exists
                if not any(s.get("name") == name for s in plugin_data["skills"]):
                    plugin_data["skills"].append({
                        "name": name,
                        "path": file_path
                    })
                    with open(link_to_plugin, 'w') as f:
                        json.dump(plugin_data, f, indent=2)
                    print(f"Linked skill '{name}' to plugin at {link_to_plugin}")
                else:
                    print(f"Skill '{name}' already linked in {link_to_plugin}")
            except Exception as e:
                print(f"Failed to link to plugin {link_to_plugin}: {e}")
        else:
            print(f"Plugin file {link_to_plugin} not found. Skipping linking.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new skill.")
    parser.add_argument("--name", required=True, help="Kebab-case name of the skill")
    parser.add_argument("--description", required=True, help="Description of the skill")
    parser.add_argument("--hide", action="store_true", help="Set user-invocable to false")
    parser.add_argument("--with-subfolders", action="store_true", help="(Deprecated) Subfolders are always created")
    parser.add_argument("--license", help="License for the skill")
    parser.add_argument("--compatibility", help="Compatibility environment requirements")
    parser.add_argument("--author", help="Author of the skill")
    parser.add_argument("--version", default="1.0.0", help="Version of the skill")
    parser.add_argument("--mcp-server", help="Associated MCP server")
    parser.add_argument("--category", help="Category of the skill")
    parser.add_argument("--tags", help="Comma-separated tags for the skill")
    parser.add_argument("--target-dir", default=".", help="Target directory for the skill")
    parser.add_argument("--link-to-plugin", help="Path to plugin.json to link this skill")
    parser.add_argument("--python-version", help="Target Python version (e.g. >=3.11)")
    parser.add_argument("--dependencies", help="Comma-separated Python dependencies")
    args = parser.parse_args()
    
    create_skill(
        name=args.name, 
        description=args.description, 
        hide=args.hide, 
        with_subfolders=args.with_subfolders,
        license=args.license,
        compatibility=args.compatibility,
        author=args.author,
        version=args.version,
        mcp_server=getattr(args, 'mcp_server', None),
        category=args.category,
        tags=args.tags,
        target_dir=args.target_dir,
        link_to_plugin=args.link_to_plugin,
        python_version=getattr(args, 'python_version', None),
        dependencies=getattr(args, 'dependencies', None)
    )
