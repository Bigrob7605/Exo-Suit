#!/usr/bin/env python3
"""
Kai Core Documentation Sync
Synchronizes documentation with generated code and changes
"""

import os
import re
from datetime import datetime


class DocumentationSync:
    """
    Synchronizes documentation with Kai Core changes
    """

    def __init__(self, toolbox_path: str):
        self.toolbox_path = toolbox_path
        self.docs_dir = os.path.join(toolbox_path, "kai_core", "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

    def update_api_reference(
        self, new_domain: str, function_name: str, description: str
    ):
        """Update API reference with new domain function"""
        api_ref_path = os.path.join(self.toolbox_path, "API_REFERENCE.md")

        if not os.path.exists(api_ref_path):
            self._create_api_reference()

        with open(api_ref_path, "r") as f:
            content = f.read()

        # Check if domain section exists
        domain_section = f"## {new_domain.title()} Domain"

        if domain_section not in content:
            # Add new domain section
            new_section = f"""
{domain_section}

### {function_name}

{description}

```python
from domain.{new_domain} import {function_name}

result = {function_name}(data, **kwargs)
```

**Parameters:**
- `data`: Input data array
- `**kwargs`: Additional parameters

**Returns:**
- Dictionary with test results and pass/fail criteria
"""

            # Insert before the last section
            sections = content.split("## ")
            if len(sections) > 1:
                # Insert before the last section
                sections.insert(-1, new_section)
                content = "## ".join(sections)
            else:
                content += new_section

        with open(api_ref_path, "w") as f:
            f.write(content)

    def _create_api_reference(self):
        """Create initial API reference"""
        api_ref_path = os.path.join(self.toolbox_path, "API_REFERENCE.md")

        content = """# API Reference

## Overview

This document provides the complete API reference for the Universal Open Science Toolbox.

## Domains

The toolbox supports multiple scientific domains, each with specialized test functions.

"""

        with open(api_ref_path, "w") as f:
            f.write(content)

    def update_examples_gallery(self, new_domain: str, function_name: str):
        """Update examples gallery with new domain example"""
        examples_gallery_path = os.path.join(self.toolbox_path, "EXAMPLES_GALLERY.md")

        if not os.path.exists(examples_gallery_path):
            self._create_examples_gallery()

        with open(examples_gallery_path, "r") as f:
            content = f.read()

        # Add new example
        new_example = f"""
### {new_domain.title()} Domain Example

```python
import numpy as np
from domain.{new_domain} import {function_name}

# Generate sample data
data = np.random.randn(100, 2)

# Run test
result = {function_name}(data)

print(f"Test passed: {{result['pass_fail']}}")
print(f"Metrics: {{result['metrics']}}")
```
"""

        # Find the right place to insert
        if f"## {new_domain.title()} Domain" not in content:
            content += f"\n## {new_domain.title()} Domain{new_example}"

        with open(examples_gallery_path, "w") as f:
            f.write(content)

    def _create_examples_gallery(self):
        """Create initial examples gallery"""
        examples_gallery_path = os.path.join(self.toolbox_path, "EXAMPLES_GALLERY.md")

        content = """# Examples Gallery

## Overview

This document provides examples for using the Universal Open Science Toolbox.

## Domain Examples

Each domain has specialized test functions with specific requirements.

"""

        with open(examples_gallery_path, "w") as f:
            f.write(content)

    def create_domain_documentation(self, domain: str, function_name: str, code: str):
        """Create domain-specific documentation"""
        domain_doc_path = os.path.join(self.docs_dir, f"{domain}_domain.md")

        # Extract function docstring
        docstring = self._extract_docstring(code)

        content = f"""# {domain.title()} Domain

## Overview

The {domain} domain provides specialized test functions for {domain} research.

## Functions

### {function_name}

{docstring}

## Usage

```python
import numpy as np
from domain.{domain} import {function_name}

# Your data here
data = np.random.randn(100, 2)

# Run test
result = {function_name}(data)

# Check results
if result['pass_fail']['criteria']:
    print("Test passed!")
else:
    print("Test failed!")
```

## Requirements

- Real public dataset integration
- Truth table format with pass/fail criteria
- Appropriate statistical tests
- Effect size and power analysis
- Data quality validation

## Examples

See the [Examples Gallery](EXAMPLES_GALLERY.md) for complete examples.
"""

        with open(domain_doc_path, "w") as f:
            f.write(content)

    def _extract_docstring(self, code: str) -> str:
        """Extract docstring from generated code"""
        # Simple regex to find docstring
        docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
        if docstring_match:
            return docstring_match.group(1).strip()
        return "No docstring found"

    def update_changelog(
        self, change_hash: str, domain: str, function_name: str, description: str
    ):
        """Update changelog with new changes"""
        changelog_path = os.path.join(self.toolbox_path, "CHANGELOG.md")

        if not os.path.exists(changelog_path):
            self._create_changelog()

        with open(changelog_path, "r") as f:
            content = f.read()

        # Add new entry
        timestamp = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""
## [{timestamp}] - Kai Core Generated {domain.title()} Domain

### Added
- Generated `{function_name}` function for {domain} domain
- {description}
- Change hash: `{change_hash}`

### Changed
- Updated API reference
- Updated examples gallery
- Updated domain documentation

---
"""

        # Insert at the top after the header
        lines = content.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith("## [") and i > 0:
                insert_index = i
                break

        lines.insert(insert_index, new_entry)
        content = "\n".join(lines)

        with open(changelog_path, "w") as f:
            f.write(content)

    def _create_changelog(self):
        """Create initial changelog"""
        changelog_path = os.path.join(self.toolbox_path, "CHANGELOG.md")

        content = """# Changelog

All notable changes to the Universal Open Science Toolbox will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release
- Kai Core integration

---
"""

        with open(changelog_path, "w") as f:
            f.write(content)

    def sync_all_documentation(
        self,
        change_hash: str,
        domain: str,
        function_name: str,
        description: str,
        code: str,
    ):
        """Sync all documentation with new changes"""
        print(f"📚 Syncing documentation for {domain} domain...")

        # Update API reference
        self.update_api_reference(domain, function_name, description)

        # Update examples gallery
        self.update_examples_gallery(domain, function_name)

        # Create domain documentation
        self.create_domain_documentation(domain, function_name, code)

        # Update changelog
        self.update_changelog(change_hash, domain, function_name, description)

        print(f"SUCCESS Documentation synced for {domain} domain")
