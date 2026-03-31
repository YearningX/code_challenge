"""
Environment Validation Script

Validates that all required dependencies and environment variables
are properly configured before model deployment.

Usage:
    python scripts/deployment/validate_environment.py
"""

import os
import sys
from typing import List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"


def check_environment_variables() -> List[Tuple[bool, str, str]]:
    """Check required environment variables."""
    required_vars = [
        ("OPENAI_API_KEY", "OpenAI API key for embeddings and LLM"),
        ("MLFLOW_TRACKING_URI", "MLflow tracking server URI"),
    ]

    optional_vars = [
        ("DATABRICKS_HOST", "Databricks workspace host"),
        ("DATABRICKS_TOKEN", "Databricks authentication token"),
    ]

    results = []

    # Check required variables
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value:
            results.append((True, var_name, f"Set (length: {len(value)})"))
        else:
            results.append((False, var_name, f"NOT SET - {description}"))

    # Check optional variables
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if value:
            results.append((True, var_name, f"Set (length: {len(value)})"))
        else:
            results.append((True, var_name, f"Not set (optional: {description})"))

    return results


def check_dependencies() -> List[Tuple[bool, str, str]]:
    """Check required Python packages."""
    required_packages = {
        "mlflow": "2.14.0",
        "langchain": "0.2.0",
        "langchain_openai": "0.1.0",
        "langchain_community": "0.2.0",
        "langchain_core": "0.2.0",
        "langgraph": "0.1.0",
        "faiss": "1.8.0",
        "dotenv": "1.0.0",
    }

    results = []

    for package, min_version in required_packages.items():
        try:
            if package == "dotenv":
                import python_dotenv
                version = "1.0.0"  # Placeholder
            elif package == "faiss":
                import faiss
                version = faiss.__version__
            else:
                module = __import__(package.replace("-", "_"))
                version = getattr(module, "__version__", "unknown")

            results.append((True, package, f"{version} (requires >={min_version})"))
        except ImportError:
            results.append((False, package, f"NOT INSTALLED (requires >={min_version})"))

    return results


def check_mlflow_connection() -> Tuple[bool, str]:
    """Check MLflow connection."""
    try:
        import mlflow

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "databricks")
        mlflow.set_tracking_uri(tracking_uri)

        # Try to access MLflow
        experiment = mlflow.get_experiment_by_name("ME_ECU_Assistant")
        if experiment:
            return True, f"Connected to {tracking_uri}, experiment found"
        else:
            return True, f"Connected to {tracking_uri}, experiment not found (will be created)"

    except Exception as e:
        return False, f"Failed to connect: {str(e)}"


def check_openai_connection() -> Tuple[bool, str]:
    """Check OpenAI API connection."""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "OPENAI_API_KEY not set"

        client = OpenAI()
        # Simple test - list models (lightweight call)
        client.models.list()
        return True, "OpenAI API connection successful"

    except Exception as e:
        return False, f"OpenAI API connection failed: {str(e)}"


def check_file_structure() -> List[Tuple[bool, str]]:
    """Check required file structure."""
    required_paths = [
        ("src/me_ecu_agent", "Source code directory"),
        ("src/me_ecu_agent/config.py", "Configuration module"),
        ("src/me_ecu_agent/graph.py", "LangGraph agent"),
        ("src/me_ecu_agent/vectorstore.py", "Vector store module"),
        ("src/me_ecu_agent/mlflow_model.py", "MLflow model wrapper"),
        ("data", "Data directory"),
        ("pyproject.toml", "Project configuration"),
    ]

    results = []

    for path, description in required_paths:
        if os.path.exists(path):
            results.append((True, path, f"Found ({description})"))
        else:
            results.append((False, path, f"NOT FOUND ({description})"))

    return results


def main():
    """Main validation function."""
    print("="*60)
    print("Environment Validation")
    print("="*60)

    all_passed = True

    # Check Python version
    print("\n[1] Python Version")
    python_ok, python_version = check_python_version()
    print(f"  {'[PASS]' if python_ok else '[FAIL]'} {python_version}")
    if not python_ok:
        all_passed = False

    # Check environment variables
    print("\n[2] Environment Variables")
    env_results = check_environment_variables()
    for passed, var_name, message in env_results:
        print(f"  {'[PASS]' if passed else '[FAIL]'} {var_name}: {message}")
        if not passed:
            all_passed = False

    # Check dependencies
    print("\n[3] Python Dependencies")
    dep_results = check_dependencies()
    for passed, package, message in dep_results:
        print(f"  {'[PASS]' if passed else '[FAIL]'} {package}: {message}")
        if not passed:
            all_passed = False

    # Check MLflow connection
    print("\n[4] MLflow Connection")
    mlflow_ok, mlflow_message = check_mlflow_connection()
    print(f"  {'[PASS]' if mlflow_ok else '[FAIL]'} {mlflow_message}")
    if not mlflow_ok:
        all_passed = False

    # Check OpenAI connection
    print("\n[5] OpenAI API Connection")
    openai_ok, openai_message = check_openai_connection()
    print(f"  {'[PASS]' if openai_ok else '[FAIL]'} {openai_message}")
    if not openai_ok:
        all_passed = False

    # Check file structure
    print("\n[6] File Structure")
    file_results = check_file_structure()
    for passed, path, message in file_results:
        print(f"  {'[PASS]' if passed else '[FAIL]'} {path}: {message}")
        if not passed:
            all_passed = False

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All validation checks passed!")
        print("="*60)
        return 0
    else:
        print("[FAILURE] Some validation checks failed!")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
