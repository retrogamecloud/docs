#!/usr/bin/env python3
"""
Fix MDX syntax errors in generated files
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_unclosed_tabs(content: str) -> Tuple[str, List[str]]:
    """Fix unclosed <Tab> and <Tabs> tags - SMART version"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    tabs_stack = []  # Stack to track <Tabs> positions
    tab_stack = []   # Stack to track <Tab> positions
    
    for i, line in enumerate(lines):
        # Count <Tabs> and </Tabs>
        if '<Tabs>' in line:
            tabs_stack.append(i)
        if '</Tabs>' in line:
            # Before closing Tabs, check if there are unclosed Tabs
            if tab_stack:
                # Insert missing </Tab> before </Tabs>
                for _ in range(len(tab_stack)):
                    fixed_lines.append('</Tab>')
                    fixes.append(f"Added missing </Tab> before </Tabs> at line {i+1}")
                tab_stack.clear()
            
            if tabs_stack:
                tabs_stack.pop()
        
        # Count <Tab ...> (but not self-closing or already closed)
        tab_pattern = r'<Tab(?:\s+[^/>]*)?(?<!/)>(?!\s*</Tab>)'
        if re.search(tab_pattern, line):
            tab_stack.append(i)
        
        # Count </Tab>
        if '</Tab>' in line:
            if tab_stack:
                tab_stack.pop()
        
        fixed_lines.append(line)
    
    # At the end, close any remaining open tags
    if tab_stack:
        for _ in tab_stack:
            fixed_lines.append('</Tab>')
            fixes.append(f"Added missing </Tab> at end of file")
        tab_stack.clear()
    
    if tabs_stack:
        for _ in tabs_stack:
            fixed_lines.append('</Tabs>')
            fixes.append(f"Added missing </Tabs> at end of file")
        tabs_stack.clear()
    
    return '\n'.join(fixed_lines), fixes

def fix_unclosed_components(content: str) -> Tuple[str, List[str]]:
    """Fix unclosed Mintlify components"""
    fixes = []
    
    # Common Mintlify components
    components = ['Note', 'Warning', 'Info', 'Tip', 'Card', 'CardGroup', 
                  'Accordion', 'AccordionGroup', 'Steps', 'Step']
    
    for component in components:
        pattern = f'<{component}(?:\\s+[^>]*)?>(?!</{component}>)'
        opens = len(re.findall(pattern, content))
        closes = content.count(f'</{component}>')
        
        if opens > closes:
            # Add missing closing tags at the end
            for _ in range(opens - closes):
                content += f'\n</{component}>'
                fixes.append(f"Added missing </{component}>")
    
    return content, fixes

def fix_code_blocks(content: str) -> Tuple[str, List[str]]:
    """Fix unclosed code blocks"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    code_fence = None
    
    for line in lines:
        # Check for code fence
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_fence = line.strip()
            else:
                in_code_block = False
                code_fence = None
        
        fixed_lines.append(line)
    
    # If still in code block at end, close it
    if in_code_block:
        fixed_lines.append('```')
        fixes.append("Added missing closing code fence")
    
    return '\n'.join(fixed_lines), fixes

def validate_frontmatter(content: str) -> Tuple[str, List[str]]:
    """Ensure valid frontmatter"""
    fixes = []
    
    if not content.strip().startswith('---'):
        # Add minimal frontmatter
        content = '---\ntitle: "Documentation"\n---\n\n' + content
        fixes.append("Added missing frontmatter")
    else:
        # Check if frontmatter is closed
        parts = content.split('---', 2)
        if len(parts) < 3:
            # Frontmatter not closed
            content = content.replace('---', '---\n---\n', 1)
            fixes.append("Fixed unclosed frontmatter")
    
    return content, fixes

def fix_mdx_file(filepath: Path) -> List[str]:
    """Fix all MDX syntax issues in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        all_fixes = []
        
        # Apply fixes
        content, fixes = validate_frontmatter(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_unclosed_tabs(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_unclosed_components(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_code_blocks(content)
        all_fixes.extend(fixes)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed: {filepath.relative_to(Path.cwd())}")
            for fix in all_fixes:
                print(f"   - {fix}")
            
            return all_fixes
        
        return []
    
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return []

def main():
    """Fix all MDX files with syntax errors"""
    print("🔧 Fixing MDX syntax errors...")
    
    docs_path = Path.cwd()
    mdx_files = list(docs_path.glob('**/*.mdx'))
    
    # Filter out node_modules, .next, etc
    mdx_files = [f for f in mdx_files if not any(
        part.startswith('.') or part == 'node_modules' 
        for part in f.parts
    )]
    
    total_fixed = 0
    
    for mdx_file in mdx_files:
        fixes = fix_mdx_file(mdx_file)
        if fixes:
            total_fixed += 1
    
    print(f"\n📊 Fixed {total_fixed} files")

if __name__ == '__main__':
    main()
