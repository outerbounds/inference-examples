"""
Metaflow flow that trains a dummy model and logs the experiment to a
deployed MLflow Tracking Server on Outerbounds.

Usage:
    python train_flow.py run

Prerequisites:
    Deploy the MLflow server first:
        outerbounds app deploy --config-file config.yaml
"""

from metaflow import FlowSpec, step, pypi_base, Parameter
from metaflow.apps import AppDeployer

MLFLOW_DEPLOYMENT_NAME = "mlflow-tracking"


def get_mlflow_url():
    """Resolve the internal URL of the deployed MLflow server."""
    deployments = AppDeployer().list_deployments(name=MLFLOW_DEPLOYMENT_NAME)
    if not deployments:
        raise ValueError(
            f"No deployment found with name '{MLFLOW_DEPLOYMENT_NAME}'. "
            "Deploy it first: outerbounds app deploy --config-file config.yaml"
        )
    return deployments[0].internal_url


@pypi_base(
    packages={
        "mlflow": "",
        "scikit-learn": "",
        "pandas": "",
        "numpy": "",
    }
)
class MLflowTrainFlow(FlowSpec):
    """Train a simple model and log everything to MLflow."""

    tracking_uri = Parameter(
        "tracking-uri",
        help="MLflow tracking URI (auto-detected from deployment if omitted)",
        default="",
    )

    @step
    def start(self):
        """Generate a toy dataset."""
        import numpy as np

        np.random.seed(42)
        n = 200
        self.X = np.random.randn(n, 3)
        self.y = self.X @ np.array([1.5, -2.0, 0.5]) + np.random.randn(n) * 0.3
        print(f"Generated dataset: {n} samples, {self.X.shape[1]} features")
        self.next(self.train)

    @step
    def train(self):
        """Train a Ridge regression model and log to MLflow."""
        import mlflow
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score

        # Point MLflow at the deployed tracking server
        uri = self.tracking_uri or get_mlflow_url()
        print(f"MLflow tracking URI: {uri}")
        mlflow.set_tracking_uri(uri)
        mlflow.set_experiment("outerbounds-demo")

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

        alpha = 1.0

        with mlflow.start_run(run_name="ridge-regression"):
            # Train
            model = Ridge(alpha=alpha)
            model.fit(X_train, y_train)

            # Evaluate
            preds = model.predict(X_test)
            mse = mean_squared_error(y_test, preds)
            r2 = r2_score(y_test, preds)

            # Log params + metrics
            mlflow.log_param("alpha", alpha)
            mlflow.log_param("n_samples", len(self.X))
            mlflow.log_param("n_features", self.X.shape[1])
            mlflow.log_metric("mse", mse)
            mlflow.log_metric("r2", r2)

            # Register the model
            mlflow.sklearn.log_model(
                model,
                artifact_path="ridge-model",
                registered_model_name="outerbounds-ridge",
            )

            print(f"Logged run — MSE: {mse:.4f}, R2: {r2:.4f}")
            print("Model registered as 'outerbounds-ridge'")

        self.mse = mse
        self.r2 = r2
        self.next(self.end)

    @step
    def end(self):
        """Print summary."""
        print(f"Done. MSE={self.mse:.4f}, R2={self.r2:.4f}")
        print("Check the MLflow UI to see the experiment and registered model.")


if __name__ == "__main__":
    MLflowTrainFlow()
