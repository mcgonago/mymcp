#!/usr/bin/env python3
"""
Script to check all markdown links in documentation files.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path("/home/omcgonag/Work/mymcp")

# Directories to exclude
EXCLUDE_DIRS = {"venv", ".tox", ".git"}

# Pattern to match markdown links: [text](path)
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

def should_skip_path(path):
    """Check if we should skip this path."""
    path_parts = Path(path).parts
    for part in path_parts:
        if part in EXCLUDE_DIRS:
            return True
    # Skip workspace subdirectories except the main README files
    if "workspace" in path_parts:
        if "horizon-" in str(path) or ".tox" in str(path):
            return True
    return False

def check_link(md_file, link_text, link_path):
    """Check if a link is valid."""
    # Skip external URLs
    parsed = urlparse(link_path)
    if parsed.scheme in ('http', 'https', 'ftp', 'mailto'):
        return None
    
    # Skip anchor-only links (same document)
    if link_path.startswith('#'):
        return None
    
    # Skip placeholder links (template examples)
    placeholder_patterns = [
        'link',  # Generic placeholder: [text](link)
        'XXX',   # Patterns like [PR #XXX](...)
        'YYY',   # Patterns like [PR #YYY](...)
        'XXXX',  # Patterns like [#XXXX](...)
        'YYYY',  # Patterns like [#YYYY](...)
        'XXXXXX', # Patterns like [Review XXXXXX](...)
        'YYYYYY', # Patterns like [Review YYYYYY](...)
        'analysis_other_topic.md',  # Template cross-reference placeholder
    ]
    
    # Check if link_path matches any placeholder pattern
    for pattern in placeholder_patterns:
        if link_path == pattern or pattern in link_path:
            return None
    
    # Handle anchor links to other files
    if '#' in link_path:
        link_path = link_path.split('#')[0]
        if not link_path:  # Just an anchor, skip
            return None
    
    # Resolve the full path
    md_dir = md_file.parent
    if link_path.startswith('/'):
        # Absolute path from repo root
        full_path = BASE_DIR / link_path.lstrip('/')
    else:
        # Relative path
        full_path = (md_dir / link_path).resolve()
    
    # Check if file/directory exists
    if not full_path.exists():
        return {
            'file': str(md_file.relative_to(BASE_DIR)),
            'link_text': link_text,
            'link_path': link_path,
            'expected': str(full_path)
        }
    
    return None

def main():
    print("Checking markdown links in documentation files...")
    print("=" * 60)
    print()
    
    broken_links = []
    
    # Find all markdown files
    for md_file in BASE_DIR.rglob("*.md"):
        if should_skip_path(str(md_file)):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            
            # Find all links
            for match in LINK_PATTERN.finditer(content):
                link_text = match.group(1)
                link_path = match.group(2)
                
                error = check_link(md_file, link_text, link_path)
                if error:
                    broken_links.append(error)
        
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    # Report results
    if broken_links:
        print(f"Found {len(broken_links)} broken links:\n")
        
        # Group by file
        by_file = {}
        for link in broken_links:
            file = link['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(link)
        
        for file, links in sorted(by_file.items()):
            print(f"\n📄 {file}")
            print("-" * 60)
            for link in links:
                print(f"  ✗ Link text: {link['link_text']}")
                print(f"    Link path: {link['link_path']}")
                print(f"    Expected:  {link['expected']}")
                print()
    else:
        print("✅ All links are valid!")
    
    print("=" * 60)
    print("Link check complete!")
    
    return len(broken_links)

if __name__ == "__main__":
    exit(main())

