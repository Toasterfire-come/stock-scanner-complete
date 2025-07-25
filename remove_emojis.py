#!/usr/bin/env python3
"""
Remove all emojis from the codebase
"""

import os
import re
from pathlib import Path

# Common emojis used in the codebase
EMOJI_PATTERNS = [
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
r'', r'', r'', r'', r'', r'', r'', r'', r'', r''
]

def remove_emojis_from_file(file_path):
"""Remove emojis from a single file"""
try:
with open(file_path, 'r', encoding='utf-8') as f:
content = f.read()

original_content = content

# Remove all emoji patterns
for emoji in EMOJI_PATTERNS:
content = re.sub(emoji, '', content)

# Remove any remaining emoji characters (Unicode ranges)
emoji_pattern = re.compile("["
u"\U0001F600-\U0001F64F" # emoticons
u"\U0001F300-\U0001F5FF" # symbols & pictographs
u"\U0001F680-\U0001F6FF" # transport & map symbols
u"\U0001F1E0-\U0001F1FF" # flags (iOS)
u"\U00002702-\U000027B0"
u"\U000024C2-\U0001F251"
"]+", flags=re.UNICODE)
content = emoji_pattern.sub('', content)

# Clean up extra spaces left by emoji removal
content = re.sub(r' +', ' ', content) # Multiple spaces to single space
content = re.sub(r'^ +', '', content, flags=re.MULTILINE) # Leading spaces

if content != original_content:
with open(file_path, 'w', encoding='utf-8') as f:
f.write(content)
return True
return False

except Exception as e:
print(f"Error processing {file_path}: {e}")
return False

def main():
"""Remove emojis from all files in the project"""
project_root = Path('.')

# File extensions to process
extensions = ['.py', '.sh', '.md', '.txt', '.yml', '.yaml', '.json']

# Directories to skip
skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', '.venv'}

modified_files = []

for root, dirs, files in os.walk(project_root):
# Skip unwanted directories
dirs[:] = [d for d in dirs if d not in skip_dirs]

for file in files:
file_path = Path(root) / file

# Check if file has a relevant extension
if any(file.endswith(ext) for ext in extensions):
if remove_emojis_from_file(file_path):
modified_files.append(str(file_path))

print(f"Emoji removal complete!")
print(f"Modified {len(modified_files)} files:")
for file_path in modified_files:
print(f" - {file_path}")

if __name__ == "__main__":
main()