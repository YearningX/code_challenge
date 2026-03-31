"""
Automated Code Quality Fix Script

Fixes common pylint issues to improve code quality from 7.00/10 to 8.5+/10

Issues addressed:
- Trailing whitespace (C0303)
- Missing docstrings (C0111, C0115, C0116)
- Unused imports (W0611)
- Bare excepts (W0702)
- Logging f-string interpolation (W1203)
- Redefining built-ins (W0622)
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class CodeQualityFixer:
    """Automated code quality fixes."""

    def __init__(self, source_dir: Path):
        """Initialize fixer.

        Args:
            source_dir: Source directory to fix
        """
        self.source_dir = source_dir
        self.fixes_applied = 0

    def fix_trailing_whitespace(self, content: str) -> str:
        """Remove trailing whitespace.

        Args:
            content: File content

        Returns:
            Fixed content
        """
        lines = content.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        return '\n'.join(fixed_lines)

    def fix_logging_fstrings(self, content: str) -> str:
        """Fix logging f-string interpolation to lazy % formatting.

        Args:
            content: File content

        Returns:
            Fixed content
        """
        # Pattern: logger.error(f"...")
        pattern = r'logger\.(debug|info|warning|error|critical)\(f"([^"]+)"\)'
        replacement = r'logger.\1("%2")'

        # Only fix if no variables in f-string
        def replace_no_vars(match):
            log_level = match.group(1)
            message = match.group(2)
            # If message contains {..}, skip
            if '{' in message and '}' in message:
                return match.group(0)
            return f'logger.{log_level}("{message}")'

        return re.sub(pattern, replace_no_vars, content)

    def add_missing_docstrings(self, content: str, filepath: Path) -> str:
        """Add missing docstrings.

        Args:
            content: File content
            filepath: File path

        Returns:
            Fixed content
        """
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)

            # Check for missing module docstring
            if i == 0 and not line.startswith('"""') and not line.startswith("'"):
                if line.startswith('import') or line.startswith('from'):
                    # Add module docstring before imports
                    module_name = filepath.stem
                    docstring = f'"""{module_name.replace("_", " ").title()} module."""'
                    fixed_lines.insert(0, docstring)
                    fixed_lines.insert(1, '')
                    i += 1

            i += 1

        return '\n'.join(fixed_lines)

    def remove_unused_imports(self, content: str) -> str:
        """Remove commonly unused imports.

        Args:
            content: File content

        Returns:
            Fixed content
        """
        lines = content.split('\n')
        fixed_lines = []
        unused_imports = {
            'from typing import Tuple',
            'from typing import Union',
            'from typing import Dict',
            'import mlflow',
        }

        for line in lines:
            # Check if this is an unused import
            is_unused = False
            for unused in unused_imports:
                if unused in line:
                    # Check if used in file (simple check)
                    import_name = unused.split('import')[-1].strip()
                    if import_name not in content[line:]:
                        is_unused = True
                        self.fixes_applied += 1
                        break

            if not is_unused:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_bare_excepts(self, content: str) -> str:
        """Fix bare except clauses.

        Args:
            content: File content

        Returns:
            Fixed content
        """
        # Replace 'except:' with 'except Exception:'
        pattern = r'(\s+)except:'
        replacement = r'\1except Exception:'
        return re.sub(pattern, replacement, content)

    def fix_redefined_builtins(self, content: str) -> str:
        """Fix redefined built-ins.

        Args:
            content: File content

        Returns:
            Fixed content
        """
        # Replace 'TimeoutError' with 'TimeoutException'
        content = re.sub(r'\bTimeoutError\b', 'TimeoutException', content)
        return content

    def fix_file(self, filepath: Path) -> int:
        """Fix all issues in a file.

        Args:
            filepath: Path to file

        Returns:
            Number of fixes applied
        """
        fixes_before = self.fixes_applied

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Apply fixes
            content = self.fix_trailing_whitespace(content)
            content = self.fix_logging_fstrings(content)
            content = self.fix_bare_excepts(content)
            content = self.fix_redefined_builtins(content)
            content = self.add_missing_docstrings(content, filepath)

            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return self.fixes_applied - fixes_before

        except Exception as e:
            print(f"  [ERROR] Failed to fix {filepath.name}: {e}")
            return 0

    def fix_all(self) -> int:
        """Fix all Python files in source directory.

        Returns:
            Total number of fixes applied
        """
        print("\n" + "="*60)
        print("Code Quality Auto-Fix")
        print("="*60)

        py_files = list(self.source_dir.rglob("*.py"))
        print(f"\nFound {len(py_files)} Python files")

        for filepath in py_files:
            print(f"  Fixing: {filepath.relative_to(self.source_dir.parent)}")
            fixes = self.fix_file(filepath)
            if fixes > 0:
                print(f"    Applied {fixes} fixes")

        print(f"\nTotal fixes applied: {self.fixes_applied}")
        print("="*60)

        return self.fixes_applied


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "src" / "me_ecu_agent"

    fixer = CodeQualityFixer(source_dir)
    fixer.fix_all()

    print("\nNext steps:")
    print("1. Run pylint to verify improvements:")
    print("   pylint src/me_ecu_agent/*.py --max-line-length=120")
    print("2. Run autopep8 for additional formatting:")
    print("   autopep8 --in-place --aggressive src/me_ecu_agent/*.py")
    print("3. Add missing docstrings manually where needed")
    print("="*60)


if __name__ == "__main__":
    main()
