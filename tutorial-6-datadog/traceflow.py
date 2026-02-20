import time
from metaflow import FlowSpec, step, environment, pypi_base
from metaflow.apps import AppDeployer

DATADOG_DEPLOYMENT_NAME = "datadog-agent"

# Fetch the URL of the deployed Datadog agent instance
def get_datadog_agent_url(): 
    dd_deployments = AppDeployer().list_deployments(name=DATADOG_DEPLOYMENT_NAME)
    if len(dd_deployments) == 0:
        raise ValueError(f"No Datadog agent deployment found with name {DATADOG_DEPLOYMENT_NAME}")
    dd_deployment = dd_deployments[0]

    return dd_deployment.internal_url

DD_ENV_VARS = {
    "DD_TRACE_AGENT_URL": get_datadog_agent_url(),
    "DD_SERVICE": "metaflow",
    "DD_ENV": "dev",
}

@pypi_base(packages={"ddtrace": ""})
class DatadogTraceFlow(FlowSpec):
    @environment(vars=DD_ENV_VARS)
    @step
    def start(self):
        # Its important to import the traces *AFTER* the environment variables are set
        from ddtrace import tracer

        # 1. Start a root span
        with tracer.trace("web.request", service="dd-trial-app", resource="GET /home") as span:
            span.set_tag("env", "development")
            print("Starting parent span...")
            
            time.sleep(0.5) # Simulate network latency
            
            # 2. Start a child span (e.g., a database query)
            with tracer.trace("database.query", service="dd-trial-app", resource="SELECT * FROM users") as child_span:
                print("Starting child span (DB query)...")
                child_span.set_tag("db.table", "users")
                
                time.sleep(0.2) # Simulate DB processing
                
            print("Finished traces.")
        self.next(self.end)

    @step
    def end(self):
        pass


if __name__ == "__main__":
    DatadogTraceFlow()