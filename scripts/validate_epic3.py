"""
Epic 3 Validation Script

Comprehensive validation for Epic 3 implementation without requiring
Databricks environment. Validates configuration, scripts, and deployment readiness.

Usage:
    python scripts/validate_epic3.py
"""

import os
import sys
import ast
import yaml
from pathlib import Path
from typing import List, Tuple, Dict


class Epic3Validator:
    """Validator for Epic 3 implementation."""

    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.results = []
        self.errors = []
        self.warnings = []

    def log_result(self, category: str, test: str, passed: bool, message: str):
        """Log validation result."""
        self.results.append({
            "category": category,
            "test": test,
            "passed": passed,
            "message": message
        })
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test}: {message}")

    def validate_file_structure(self) -> bool:
        """Validate required file structure."""
        print("\n[1] File Structure Validation")
        print("="*60)

        required_files = [
            ("databricks.yml", "DAB configuration file"),
            ("pyproject.toml", "Python package configuration"),
            ("src/me_ecu_agent", "Source code directory"),
            ("src/me_ecu_agent/config.py", "Configuration module"),
            ("src/me_ecu_agent/graph.py", "LangGraph agent"),
            ("src/me_ecu_agent/mlflow_model.py", "MLflow model wrapper"),
            ("src/me_ecu_agent/vectorstore.py", "Vector store module"),
            ("scripts/log_mlflow_model.py", "Model logging script"),
            ("scripts/deployment/validate_environment.py", "Environment validation"),
            ("scripts/deployment/validate_model.py", "Model validation"),
            ("data", "Data directory"),
        ]

        all_exist = True
        for file_path, description in required_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            self.log_result(
                "File Structure",
                f"{file_path}",
                exists,
                f"{description} - {'Found' if exists else 'NOT FOUND'}"
            )
            if not exists:
                all_exist = False
                self.errors.append(f"Required file not found: {file_path}")

        return all_exist

    def validate_databricks_yml(self) -> bool:
        """Validate databricks.yml configuration."""
        print("\n[2] Databricks.yml Validation")
        print("="*60)

        yml_path = self.project_root / "databricks.yml"
        if not yml_path.exists():
            self.log_result("Databricks.yml", "File exists", False, "File not found")
            return False

        self.log_result("Databricks.yml", "File exists", True, "File found")

        try:
            with open(yml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Validate top-level structure
            required_sections = ["bundle", "workspace", "targets", "resources"]
            all_valid = True

            for section in required_sections:
                exists = section in config
                self.log_result(
                    "Databricks.yml",
                    f"Section: {section}",
                    exists,
                    f"{'Present' if exists else 'MISSING'}"
                )
                if not exists:
                    all_valid = False
                    self.errors.append(f"Missing section: {section}")

            # Validate bundle configuration
            if "bundle" in config:
                bundle = config["bundle"]
                self.log_result(
                    "Databricks.yml",
                    "Bundle name",
                    "name" in bundle,
                    bundle.get("name", "NOT SET")
                )
                self.log_result(
                    "Databricks.yml",
                    "Bundle version",
                    "version" in bundle,
                    bundle.get("version", "NOT SET")
                )

            # Validate targets
            if "targets" in config:
                targets = config["targets"]
                required_targets = ["dev", "staging", "prod"]
                for target in required_targets:
                    exists = target in targets
                    self.log_result(
                        "Databricks.yml",
                        f"Target: {target}",
                        exists,
                        f"{'Defined' if exists else 'NOT DEFINED'}"
                    )

            # Validate resources
            if "resources" in config:
                resources = config["resources"]
                has_models = "models" in resources
                has_jobs = "jobs" in resources
                has_experiments = "experiments" in resources

                self.log_result(
                    "Databricks.yml",
                    "Resources: models",
                    has_models,
                    f"{'Defined' if has_models else 'NOT DEFINED'}"
                )
                self.log_result(
                    "Databricks.yml",
                    "Resources: jobs",
                    has_jobs,
                    f"{'Defined' if has_jobs else 'NOT DEFINED'}"
                )
                self.log_result(
                    "Databricks.yml",
                    "Resources: experiments",
                    has_experiments,
                    f"{'Defined' if has_experiments else 'NOT DEFINED'}"
                )

            # Validate variables
            if "variables" in config:
                variables = config["variables"]
                required_vars = ["openai_api_key"]
                for var in required_vars:
                    exists = var in variables
                    self.log_result(
                        "Databricks.yml",
                        f"Variable: {var}",
                        exists,
                        f"{'Defined' if exists else 'NOT DEFINED'}"
                    )

            return all_valid

        except yaml.YAMLError as e:
            self.log_result("Databricks.yml", "Syntax", False, f"YAML error: {e}")
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.log_result("Databricks.yml", "Parsing", False, f"Error: {e}")
            self.errors.append(f"Config parsing error: {e}")
            return False

    def validate_deployment_scripts(self) -> bool:
        """Validate deployment scripts."""
        print("\n[3] Deployment Scripts Validation")
        print("="*60)

        scripts = [
            ("scripts/deployment/validate_environment.py", "Environment validation"),
            ("scripts/deployment/validate_model.py", "Model validation"),
        ]

        all_valid = True
        for script_path, description in scripts:
            full_path = self.project_root / script_path
            if not full_path.exists():
                self.log_result(
                    "Deployment Scripts",
                    f"{script_path}",
                    False,
                    "File not found"
                )
                all_valid = False
                continue

            # Validate Python syntax
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    ast.parse(code)
                self.log_result(
                    "Deployment Scripts",
                    f"{script_path}",
                    True,
                    f"Valid Python - {description}"
                )
            except SyntaxError as e:
                self.log_result(
                    "Deployment Scripts",
                    f"{script_path}",
                    False,
                    f"Syntax error: {e}"
                )
                all_valid = False
                self.errors.append(f"Syntax error in {script_path}: {e}")

        return all_valid

    def validate_script_functionality(self) -> bool:
        """Validate that deployment scripts can run."""
        print("\n[4] Script Functionality Validation")
        print("="*60)

        all_valid = True

        # Test environment validation script
        print("\n  Testing environment validation script...")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "scripts/deployment/validate_environment.py"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )

            if result.returncode == 0:
                self.log_result(
                    "Functionality",
                    "Environment validation",
                    True,
                    "Script executed successfully"
                )
            else:
                self.log_result(
                    "Functionality",
                    "Environment validation",
                    False,
                    f"Script failed (exit code: {result.returncode})"
                )
                all_valid = False
                self.warnings.append(f"Environment validation failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.log_result(
                "Functionality",
                "Environment validation",
                False,
                "Timeout (>30s)"
            )
            all_valid = False
        except Exception as e:
            self.log_result(
                "Functionality",
                "Environment validation",
                False,
                f"Error: {e}"
            )
            all_valid = False

        return all_valid

    def validate_documentation(self) -> bool:
        """Validate documentation."""
        print("\n[5] Documentation Validation")
        print("="*60)

        required_docs = [
            ("docs/EPIC-3-DEPLOYMENT-GUIDE.md", "Deployment guide"),
            ("docs/EPIC-3-COMPLETE.md", "Epic 3 completion summary"),
        ]

        all_exist = True
        for doc_path, description in required_docs:
            full_path = self.project_root / doc_path
            exists = full_path.exists()
            self.log_result(
                "Documentation",
                f"{doc_path}",
                exists,
                f"{description} - {'Found' if exists else 'NOT FOUND'}"
            )
            if not exists:
                all_exist = False

        return all_exist

    def validate_integration(self) -> bool:
        """Validate integration with previous Epics."""
        print("\n[6] Integration Validation")
        print("="*60)

        # Check Epic 1 components
        epic1_components = [
            "src/me_ecu_agent/graph.py",
            "src/me_ecu_agent/vectorstore.py",
            "src/me_ecu_agent/document_processor.py",
        ]

        # Check Epic 2 components
        epic2_components = [
            "src/me_ecu_agent/mlflow_model.py",
            "src/me_ecu_agent/error_handling.py",
            "scripts/log_mlflow_model.py",
        ]

        all_valid = True

        for component in epic1_components:
            exists = (self.project_root / component).exists()
            self.log_result(
                "Integration",
                f"Epic 1: {component}",
                exists,
                "Epic 1 component present"
            )

        for component in epic2_components:
            exists = (self.project_root / component).exists()
            self.log_result(
                "Integration",
                f"Epic 2: {component}",
                exists,
                "Epic 2 component present"
            )

        return all_valid

    def generate_report(self) -> Dict:
        """Generate validation report."""
        print("\n" + "="*60)
        print("Validation Summary")
        print("="*60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed

        print(f"\nTotal Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {passed/total*100:.1f}%")

        if self.errors:
            print(f"\nErrors: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\nWarnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "="*60)

        if passed == total:
            print("[SUCCESS] All validation checks passed!")
            print("Epic 3 implementation is complete and ready for deployment.")
            print("="*60)
            return {"status": "success", "passed": passed, "failed": failed}
        elif passed >= total * 0.8:
            print("[PARTIAL] Most checks passed, but some issues found.")
            print("Review errors above before deploying to production.")
            print("="*60)
            return {"status": "partial", "passed": passed, "failed": failed}
        else:
            print("[FAILURE] Too many validation checks failed.")
            print("Please fix the errors before deploying.")
            print("="*60)
            return {"status": "failure", "passed": passed, "failed": failed}


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent

    print("="*60)
    print("Epic 3 Validation")
    print("="*60)
    print(f"Project Root: {project_root}")

    validator = Epic3Validator(project_root)

    # Run validations
    validator.validate_file_structure()
    validator.validate_databricks_yml()
    validator.validate_deployment_scripts()
    validator.validate_documentation()
    validator.validate_integration()

    # Note: Skip script functionality if no Databricks environment
    # validator.validate_script_functionality()

    # Generate report
    report = validator.generate_report()

    return 0 if report["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
