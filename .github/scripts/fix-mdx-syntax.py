#!/usr/bin/env python3
"""
Fix MDX syntax errors in generated files
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_unclosed_tabs(content: str) -> Tuple[str, List[str]]:
    """Fix unclosed <Tab> and <Tabs> tags"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    tabs_stack = []  # Stack to track <Tabs> depth
    tab_stack = []   # Stack to track <Tab> depth
    
    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line
        
        # Count <Tabs> and </Tabs>
        tabs_opens = line.count('<Tabs>')
        tabs_closes = line.count('</Tabs>')
        
        for _ in range(tabs_opens):
            tabs_stack.append(i)
        for _ in range(tabs_closes):
            if tabs_stack:
                tabs_stack.pop()
        
        # Count <Tab ...> and </Tab>
        # Match <Tab> or <Tab title="..."> but not </Tab>
        tab_pattern = r'<Tab(?:\s+[^/>]*)?(?<!/)>(?!\s*</Tab>)'
        tab_opens = len(re.findall(tab_pattern, line))
        tab_closes = line.count('</Tab>')
        
        for _ in range(tab_opens):
            tab_stack.append(i)
        for _ in range(tab_closes):
            if tab_stack:
                tab_stack.pop()
        
        fixed_lines.append(line)
        i += 1
        
        # If we just closed the last <Tabs> but have open <Tab>s, close them
        if tabs_closes > 0 and not tabs_stack and tab_stack:
            # Insert missing </Tab> before the </Tabs>
            num_unclosed = len(tab_stack)
            # Go back and insert before the </Tabs> line
            last_line = fixed_lines[-1]
            if '</Tabs>' in last_line:
                # Remove the line with </Tabs>
                fixed_lines.pop()
                # Add closing </Tab>s
                for _ in range(num_unclosed):
                    fixed_lines.append('</Tab>')
                    fixes.append(f"Added missing </Tab> before </Tabs> at line {i}")
                # Re-add the </Tabs>
                fixed_lines.append(last_line)
                tab_stack.clear()
    
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
