#!/usr/bin/env python3
"""
Script to convert old-style org-mode code blocks (: X format) to modern #+BEGIN_SRC blocks.
"""

import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/home/omcgonag/Work/mymcp/analysis")

# Mapping of file extensions to org-mode source block language
EXTENSION_MAP = {
    '.conf': 'bash',  # .conf files use bash highlighting (most similar)
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
    """Detect the programming language from an 'iyaml/ipython/ishell <filename>' line."""
    # Check for ipython marker - always Python
    if re.search(r': ipython\s+', line):
        return 'python'
    
    # Check for ishell marker - check file extension or default to bash
    match = re.search(r': ishell\s+(\S+)', line)
    if match:
        filename = match.group(1)
        ext = Path(filename).suffix.lower()
        return EXTENSION_MAP.get(ext, 'bash')
    
    # Check for iyaml marker - check file extension
    match = re.search(r': iyaml\s+(\S+)', line)
    if match:
        filename = match.group(1)
        ext = Path(filename).suffix.lower()
        return EXTENSION_MAP.get(ext, 'bash')  # Default to bash if unknown
    
    return None

def analyze_org_file(filepath):
    """Analyze an org file for code blocks that need conversion."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_code_block = False
        block_start_line = None
        block_language = None
        block_lines = []
        
        for i, line in enumerate(lines, 1):
            # Check for ": X" marker (start of code block)
            if line.strip() == ': X':
                if not in_code_block:
                    in_code_block = True
                    block_start_line = i
                    block_lines = []
                else:
                    # End of code block (another : X)
                    if block_lines:
                        issues.append({
                            'file': filepath,
                            'start_line': block_start_line,
                            'end_line': i,
                            'language': block_language or 'unknown',
                            'line_count': len(block_lines),
                            'sample': block_lines[0][:60] if block_lines else '',
                        })
                    in_code_block = False
                    block_language = None
                    block_lines = []
            
            # Check for language markers (": iyaml", ": ipython", ": ishell")
            elif line.startswith(': iyaml') or line.startswith(': ipython') or line.startswith(': ishell'):
                lang = detect_language_from_marker(line)
                if lang:
                    block_language = lang
            
            # Collect code block content
            elif in_code_block and line.startswith(':'):
                # Strip the leading ": " from the line
                content = line[2:] if len(line) > 2 else ''
                block_lines.append(content)
    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return issues

def main():
    print("=" * 80)
    print("Org-Mode Code Block Analysis")
    print("=" * 80)
    print()
    
    # Find all .org files
    org_files = list(BASE_DIR.rglob("*.org"))
    print(f"Found {len(org_files)} .org files\n")
    
    # Analyze each file
    all_issues = []
    files_with_issues = 0
    
    for org_file in sorted(org_files):
        issues = analyze_org_file(org_file)
        if issues:
            all_issues.extend(issues)
            files_with_issues += 1
    
    # Summary
    print(f"📊 Summary")
    print(f"  Total files checked: {len(org_files)}")
    print(f"  Files with old-style code blocks: {files_with_issues}")
    print(f"  Total code blocks to convert: {len(all_issues)}")
    print()
    
    # Group by language
    by_language = defaultdict(list)
    for issue in all_issues:
        by_language[issue['language']].append(issue)
    
    print(f"📋 By Language:")
    for lang, items in sorted(by_language.items()):
        print(f"  {lang}: {len(items)} blocks")
    print()
    
    # Detailed listing
    print("=" * 80)
    print("Detailed Report")
    print("=" * 80)
    print()
    
    current_file = None
    for issue in all_issues:
        rel_path = issue['file'].relative_to(Path("/home/omcgonag/Work/mymcp"))
        
        if current_file != rel_path:
            if current_file is not None:
                print()
            print(f"\n📄 {rel_path}")
            print("-" * 80)
            current_file = rel_path
        
        print(f"  Lines {issue['start_line']}-{issue['end_line']}: "
              f"{issue['language']} block ({issue['line_count']} lines)")
        if issue['sample']:
            print(f"    Sample: {issue['sample'].strip()[:70]}")
    
    print()
    print("=" * 80)
    print("Conversion Pattern")
    print("=" * 80)
    print()
    print("OLD FORMAT:")
    print("  : X")
    print("  : iyaml filename.conf")
    print("  :")
    print("  : [content line 1]")
    print("  : [content line 2]")
    print("  : X")
    print()
    print("NEW FORMAT (.conf files):")
    print("  #+BEGIN_SRC bash")
    print("  [content line 1]")
    print("  [content line 2]")
    print("  #+END_SRC")
    print()
    print("NEW FORMAT (.yaml/.yml files):")
    print("  #+BEGIN_SRC yaml")
    print("  [content line 1]")
    print("  [content line 2]")
    print("  #+END_SRC")
    print()
    print("NEW FORMAT (.py files):")
    print("  #+BEGIN_SRC python")
    print("  [content line 1]")
    print("  [content line 2]")
    print("  #+END_SRC")
    print()
    
    # Files that need attention
    if by_language.get('unknown'):
        print("⚠️  WARNING: Unknown file types found")
        print("These blocks don't match our patterns and need manual review:")
        print()
        for issue in by_language['unknown']:
            rel_path = issue['file'].relative_to(Path("/home/omcgonag/Work/mymcp"))
            print(f"  {rel_path}:{issue['start_line']}")
        print()
    
    return len(all_issues)

if __name__ == "__main__":
    count = main()
    exit(0 if count == 0 else 1)

