import mlflow
from me_ecu_agent.model import ECUAgentModel

# This line registers the model for MLflow's "Models from Code" feature, avoiding cloudpickle entirely.
mlflow.models.set_model(ECUAgentModel())
