# Deploying Datadog Agent on Outerbounds 

While [metaflow-measure](https://github.com/outerbounds/metaflow-measure) is useful when you want to emit datadog metrics, sometimes a use case requires setting up tracing to monitor your flows. To do so within Outerbounds, you can deploy this Datadog agent on the Outerbounds platform and easily emit traces to it. 

## 0. Prerequisites 

1. Make sure you have a resource integration setup on the Outerbounds UI that has your Datadog API key. Choose "Custom" resource integration type, and make sure the "Key" is set to `DD_API_KEY`. 
2. Make sure you have at least one compute pool configured to allow inference workloads. 

## 1. Deploy the Datadog agent

We will use [Outerbounds Deployments](https://docs.outerbounds.com/outerbounds/get-started-inference/) to deploy our Datadog agent. 

1. First, inspect the contents of `config.yaml` and make sure you update the secret name, compute pool name, and certain environment variables according to your setup. 
2. Run `outerbounds app deploy --config-file config.yaml`. This should go ahead an deploy your datadog agent. 

## 2. Emitting traces to your deployed Datadog Agent instance 

See [traceflow.py](./traceflow.py) for an example of how to emit traces to your datadog agent. The flow fetches the URL of the deployed datadog agent and then sends traces to it by configuring the `DD_TRACE_AGENT_URL` env var. We use the [Programmatic Deployer API](https://docs.outerbounds.com/outerbounds/programmatic-deployment-api-reference/) to fetch the URL of the deployed instance.

Run it using: `python traceflow.py --environment=fast-bakery --with kubernetes run`

*Note*: Currently tracing will only work for remote tasks running on your Outerbounds cluster, or if you're running the code from your workstation. The trace sending will fail if running from your local laptop. 