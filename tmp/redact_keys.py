import os
import re

# List of real keys found in the project
KEYS_TO_REDACT = [
    r"your-api-key-placeholder",
    r"your-api-key-placeholder",
    r"your-api-key-placeholder",
    r"your-api-key-placeholder",
    r"your-api-key-placeholder"
]

# Patterns for general keys (be careful not to catch placeholders)
# This catches things that look like real hex/base64 keys
GENERAL_PATTERNS = [
    r"sk-[a-zA-Z0-9]{32,}",
    r"sk-lf-[a-zA-Z0-9-]{20,}",
    r"pk-lf-[a-zA-Z0-9-]{20,}"
]

PLACEHOLDER = "your-api-key-placeholder"

def redact_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Redact specific known keys
        for key in KEYS_TO_REDACT:
            content = content.replace(key, PLACEHOLDER)
            
        # 2. Redact patterns (excluding already known placeholders)
        def replace_match(match):
            val = match.group(0)
            if "your-" in val or "sk-xxx" in val or "sk-your" in val:
                return val
            return PLACEHOLDER

        for pattern in GENERAL_PATTERNS:
            content = re.sub(pattern, replace_match, content)
            
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        # print(f"Error processing {file_path}: {e}")
        pass
    return False

def main():
    modified_count = 0
    # Walk through the project (excluding .git and other non-text dirs if needed)
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.lower().endswith(('.md', '.py', '.yml', '.yaml', '.sh', '.json', '.env', '.html')):
                path = os.path.join(root, file)
                if redact_file(path):
                    print(f"Redacted: {path}")
                    modified_count += 1
    
    print(f"Total files redacted: {modified_count}")

if __name__ == "__main__":
    main()
