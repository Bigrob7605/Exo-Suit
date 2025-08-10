#!/usr/bin/env python3
"""
Convert dependency JSON to Mermaid diagram format.
"""
import json
import sys
import os


def walk_dependencies(deps, parent='root'):
    """Recursively walk dependency tree and write Mermaid syntax."""
    for key, value in deps.get('dependencies', {}).items():
        yield f'  {parent}-->{key};'
        yield from walk_dependencies(value, key)


def main():
    """Main function to convert dependencies to Mermaid format."""
    input_file = 'mermaid/dep.json'
    output_file = 'mermaid/deps.mmd'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found, skipping Mermaid generation")
        return 0
    
    try:
        # Load dependency data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Generate Mermaid diagram
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('graph TD;\n')
            for line in walk_dependencies(data):
                f.write(line + '\n')
        
        print(f"✅ Mermaid diagram generated: {output_file}")
        return 0
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        return 1
    except Exception as e:
        print(f"Error generating Mermaid diagram: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
