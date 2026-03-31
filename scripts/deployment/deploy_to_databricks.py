"""
Deploy ME ECU Agent to Databricks

This script deploys the MLflow model and creates Databricks jobs for automation.

Usage:
    python scripts/deployment/deploy_to_databricks.py [--target dev|staging|prod]
"""

import argparse
import sys
from pathlib import Path
from databricks.sdk import WorkspaceClient
import yaml


class DatabricksDeployer:
    """Deploy ME ECU Agent to Databricks workspace."""

    def __init__(self, target: str = "dev"):
        """Initialize deployer.

        Args:
            target: Deployment target (dev, staging, prod)
        """
        self.target = target
        self.client = WorkspaceClient()
        self.project_root = Path(__file__).parent.parent.parent

        # Load databricks.yml configuration
        with open(self.project_root / "databricks.yml", 'r') as f:
            self.config = yaml.safe_load(f)

    def create_job(self):
        """Create Databricks job for automated deployment.

        Returns:
            Job ID
        """
        print(f"\n[1] Creating Databricks Job")

        # Get target-specific configuration
        target_config = self.config["targets"][self.target]
        job_name = target_config["resources"]["jobs"]["build_and_log_model"]["name"]

        # Get notification email
        notification_email = self.config["variables"]["notification_email"]["default"]
        node_type = self.config["variables"]["node_type"]["default"]

        print(f"  Job Name: {job_name}")
        print(f"  Node Type: {node_type}")
        print(f"  Notification Email: {notification_email}")

        # Define job tasks using dict format
        tasks = [
            {
                "task_key": "validate_environment",
                "description": "Validate deployment environment",
                "python_file": "scripts/deployment/validate_environment.py",
                "libraries": [
                    {"pypi": {"package": "mlflow"}}
                ],
                "timeout_seconds": 600,
                "new_cluster": {
                    "spark_version": "latest LTS",
                    "node_type_id": node_type,
                    "num_workers": 0,
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode"
                    }
                }
            },
            {
                "task_key": "build_and_log",
                "description": "Build and log MLflow model",
                "python_file": "scripts/log_mlflow_model.py",
                "depends_on": [{"task_key": "validate_environment"}],
                "libraries": [
                    {"pypi": {"package": "mlflow"}},
                    {"pypi": {"package": "langchain>=0.2.0"}},
                    {"pypi": {"package": "langchain-openai"}},
                    {"pypi": {"package": "faiss-cpu"}},
                    {"pypi": {"package": "databricks-sdk"}}
                ],
                "timeout_seconds": 3600,
                "new_cluster": {
                    "spark_version": "latest LTS",
                    "node_type_id": node_type,
                    "num_workers": 0,
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode"
                    },
                    "environment_vars": {
                        "OPENAI_API_KEY": "{{secrets/scope/openai_api_key}}",
                        "MLFLOW_TRACKING_URI": "databricks"
                    }
                }
            },
            {
                "task_key": "validate_model",
                "description": "Validate deployed model",
                "python_file": "scripts/deployment/validate_model.py",
                "depends_on": [{"task_key": "build_and_log"}],
                "libraries": [
                    {"pypi": {"package": "mlflow"}}
                ],
                "timeout_seconds": 1800,
                "new_cluster": {
                    "spark_version": "latest LTS",
                    "node_type_id": node_type,
                    "num_workers": 0,
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode"
                    }
                }
            }
        ]

        # Create job settings
        create_job_req = {
            "name": job_name,
            "tasks": tasks,
        }

        # Add schedule for staging/prod
        if self.target in ["staging", "prod"]:
            schedule_config = target_config["resources"]["jobs"]["build_and_log_model"]["schedule"]
            create_job_req["schedule"] = {
                "quartz_cron_expression": schedule_config["quartz_cron_expression"],
                "timezone_id": schedule_config["timezone_id"]
            }

        # Create job
        try:
            print(f"\n  Creating job with {len(tasks)} tasks...")
            created_job = self.client.jobs.create(**create_job_req)
            print(f"  [OK] Job created: {created_job.job_id}")
            print(f"  [INFO] Job name: {job_name}")
            return created_job.job_id
        except Exception as e:
            print(f"  [ERROR] Failed to create job: {e}")
            import traceback
            traceback.print_exc()
            raise

    def deploy(self):
        """Execute deployment."""
        print("="*60)
        print(f"Deploying ME ECU Agent to Databricks")
        print("="*60)
        print(f"Target: {self.target}")
        print(f"Workspace: {self.client.config.host}")
        print("="*60)

        try:
            # Create job
            job_id = self.create_job()

            # Summary
            print("\n" + "="*60)
            print("Deployment Summary")
            print("="*60)
            print(f"Job ID: {job_id}")
            print(f"Job URL: {self.client.config.host}/#job/{job_id}")
            print("="*60)
            print("[SUCCESS] Deployment completed!")
            print("\nIMPORTANT: Next Steps Required")
            print("="*60)
            print("1. Set OPENAI_API_KEY as Databricks secret:")
            print("   - Go to: https://dbc-89361048-7185.cloud.databricks.com/#secrets/createSecret")
            print("   - Scope: scope (or create a new scope)")
            print("   - Key: openai_api_key")
            print("   - Value: your OpenAI API key (sk-...)")
            print()
            print("2. Upload data files to workspace:")
            print(f"   - Upload files from: {self.project_root / 'data'}")
            print("   - To: /Workspace/Users/your-email/me-ecu-agent/data/")
            print()
            print("3. Upload source code to workspace:")
            print(f"   - Upload: {self.project_root / 'src'}")
            print("   - To: /Workspace/Users/your-email/me-ecu-agent/src/")
            print()
            print("4. Run the job:")
            print(f"   - Manual: {self.client.config.host}/#job/{job_id}")
            print("   - Click 'Run Now' button")
            print()
            print("5. Monitor job execution:")
            print("   - Check job runs in the Workflows UI")
            print("   - Verify all 3 tasks complete successfully")
            print("="*60)

            return 0

        except Exception as e:
            print(f"\n[ERROR] Deployment failed: {e}")
            return 1


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Deploy ME ECU Agent to Databricks")
    parser.add_argument(
        "--target",
        type=str,
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Deployment target (default: dev)"
    )

    args = parser.parse_args()

    deployer = DatabricksDeployer(target=args.target)
    return deployer.deploy()


if __name__ == "__main__":
    sys.exit(main())
