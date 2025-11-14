#!/usr/bin/env python3
"""
Script to automatically convert old-style org-mode code blocks to modern #+BEGIN_SRC blocks.

OLD FORMAT:
  : X
  : iyaml filename.conf
  : 
  : [content line 1]
  : [content line 2]
  : X

NEW FORMAT:
  #+BEGIN_SRC bash
  [content line 1]
  [content line 2]
  #+END_SRC
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/omcgonag/Work/mymcp/analysis")

# Mapping of file extensions to org-mode source block language
EXTENSION_MAP = {
    '.conf': 'bash',  # .conf files use bash highlighting
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.py': 'python',
    '.sh': 'bash',
    '.js': 'javascript',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
}

def detect_language_from_marker(line):
    """Detect the programming language from an 'iyaml/ipython/ishell <filename>' line.
    
    Returns: tuple of (language, filename) or (language, None)
    """
    # Check for ipython marker - always Python
    match = re.search(r': ipython\s+(.+)', line)
    if match:
        filename = match.group(1).strip()
        return ('python', filename if filename else None)
    
    # Check for ishell marker - check file extension or default to bash
    match = re.search(r': ishell\s+(.+)', line)
    if match:
        filename = match.group(1).strip()
        ext = Path(filename).suffix.lower()
        lang = EXTENSION_MAP.get(ext, 'bash')
        return (lang, filename)
    
    # Check for iyaml marker - check file extension
    match = re.search(r': iyaml\s+(.+)', line)
    if match:
        filename = match.group(1).strip()
        ext = Path(filename).suffix.lower()
        lang = EXTENSION_MAP.get(ext, 'bash')
        return (lang, filename)
    
    # Check for iyaml without filename - likely YAML content
    if re.search(r': iyaml\s*$', line):
        return ('yaml', None)
    
    return ('bash', None)  # Default fallback

def convert_org_file(filepath, dry_run=False):
    """Convert old-style code blocks in an org file to modern #+BEGIN_SRC blocks."""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return False
    
    new_lines = []
    i = 0
    conversions = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for start of old-style code block (: X)
        if line.strip() == ': X':
            # Found start of code block
            block_start = i
            i += 1
            
            # Look for language marker on next line(s)
            language = 'bash'  # Default
            filename = None
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith(': iyaml') or next_line.startswith(': ipython') or next_line.startswith(': ishell'):
                    language, filename = detect_language_from_marker(next_line)
                    i += 1
                    break
                elif next_line.strip() == ':':
                    # Empty line in code block, skip language detection
                    i += 1
                    break
                elif next_line.strip() == ': X':
                    # Immediate end, empty code block
                    break
                else:
                    # No language marker found, start of content
                    break
            
            # Collect code block content (lines starting with ':')
            code_lines = []
            while i < len(lines):
                content_line = lines[i]
                if content_line.strip() == ': X':
                    # End of code block
                    i += 1
                    break
                elif content_line.startswith(':'):
                    # Code line - strip the leading ': '
                    if len(content_line) > 2 and content_line[1] == ' ':
                        code_lines.append(content_line[2:])
                    elif len(content_line) == 2:  # Just ':'
                        code_lines.append('\n')
                    else:
                        code_lines.append(content_line[1:])
                    i += 1
                else:
                    # Should not happen, but break if we hit non-colon line
                    break
            
            # Write the new format
            if filename:
                # Add filename as a comment on the same line
                new_lines.append(f"#+BEGIN_SRC {language}   # {filename}\n")
            else:
                new_lines.append(f"#+BEGIN_SRC {language}\n")
            new_lines.extend(code_lines)
            new_lines.append("#+END_SRC\n")
            conversions += 1
        else:
            # Regular line, keep as-is
            new_lines.append(line)
            i += 1
    
    # Write the converted file
    if conversions > 0:
        if dry_run:
            print(f"  ✓ Would convert {conversions} code blocks")
            return True
        else:
            # Create backup
            backup_path = filepath.with_suffix(filepath.suffix + '.backup')
            shutil.copy2(filepath, backup_path)
            
            # Write converted content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"  ✓ Converted {conversions} code blocks (backup: {backup_path.name})")
            return True
    else:
        print(f"  ℹ No code blocks to convert")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert old-style org code blocks to modern format')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--file', type=str, help='Convert a specific file instead of all files')
    args = parser.parse_args()
    
    print("=" * 80)
    print("Org-Mode Code Block Converter")
    print("=" * 80)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    # Find files to convert
    if args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        org_files = [file_path]
    else:
        org_files = sorted(BASE_DIR.rglob("*.org"))
    
    print(f"Found {len(org_files)} .org file(s) to check\n")
    
    # Convert each file
    converted_count = 0
    for org_file in org_files:
        rel_path = org_file.relative_to(Path("/home/omcgonag/Work/mymcp"))
        print(f"📄 {rel_path}")
        
        if convert_org_file(org_file, dry_run=args.dry_run):
            converted_count += 1
    
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    if args.dry_run:
        print(f"Would convert {converted_count} file(s)")
        print()
        print("To perform the actual conversion, run:")
        print("  python3 convert-org-codeblocks-auto.py")
    else:
        print(f"✅ Converted {converted_count} file(s)")
        print()
        print("Backups created with .backup extension")
        print()
        print("To restore a file:")
        print("  mv <file>.org.backup <file>.org")
    
    print()
    return 0

if __name__ == "__main__":
    exit(main())

