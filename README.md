# Inference Tutorials on Outerbounds

This repository contains a set of examples to get started with running inference services on Outerbounds. 

In the Outerbounds universe, each inference service is called a "Deployment". For the remainder of this doc, when we say "Deployments", we mean inference services. 

## Outerbounds CLI 

You can launch and manage Deployments on Outerbounds using the `outerbounds` CLI. To get started: 

`pip install -U outerbounds`

The version of `outerbounds` you have should be `>=0.5.2`. 

### Creating a Deployment 

Outerbounds allows you to deploy services of any type using your favorite framework like Flask/FastAPI/Streamlit etc. Assume the following: 

1. The logic of your deployment resides in a folder called `my-app`. 
2. The way you launch your app is by doing: `python my-start.py --arg1 value_1 --arg2 value_2`. 
3. Your app runs on port 8000. 
4. You have a requirements.txt in your top level folder. 

Then, you can launch this service on Outerbounds by doing the following: 

1. `cd my-app`. 
2. `outerbounds app deploy --name my-first-app --port 8000 [--auth-type API] -- python my-start.py --arg1 value_1 --arg2 value_2`. 

The command will build an image with your dependencies using Fast Bakery and launch your deployment. It will also print out a URL where you can access your deployment. 

```
2025-05-27 17:10:33.977 🚀 Deploying vllm-app to the Outerbounds platform...
2025-05-27 17:10:33.977 📦 Packaging Directory : /home/ubuntu/inference-examples/examples/vllm
2025-05-27 17:10:34.246 🍞 Baking Docker Image
2025-05-27 17:10:34.246 🐳 Using The Docker Image : registry.hub.docker.com/vllm/vllm-openai:latest
2025-05-27 17:10:34.696 💾 Code Package Saved to : s3://obp-sk0bzb-metaflow/metaflow/mf.obp-apps/08/0864b61b456daf0532c1022f3d20f6cb01e40ade
2025-05-27 17:10:34.699 🚀 Deploying endpoint to the platform...
2025-05-27 17:10:35.735 🔧 🛠️ Updating Endpoint c-oik87o
2025-05-27 17:10:35.735 💊 Endpoint c-oik87o is ready to serve traffic on the URL: https://api-c-oik87o.dev-yellow.outerbounds.xyz
2025-05-27 17:10:35.735 💊 Endpoint vllm-app (c-oik87o) deployed successfully! You can access it at https://api-c-oik87o.dev-yellow.outerbounds.xyz
```

You can run the same command over & over as you make changes to your code, dependencies or configuration of the deployment. 
    
Some notes about the command: 

1. Provide whatever port you expect to run your deployment on. 
2. The part after `--` should be what you would use if you were looking to run your deployment locally. 
3. By default, a Deployment is accessible via the browser. If you provide `--auth-type API`, then the Deployment will not be accessible via your browser, and instead via an API endpoint. See [accessing your API endpoint](#endpoint-access) on details about how to access an API endpoint. 

You can configure your deployment either using CLI flags or using a config schema. For more details, take a look at [Configuration](./configuration.md). 

### Listing all Deployments

You can run `outerbounds app list` to list all Deployments currently running on the platform. 

### Deleting your deployment 

You can delete your deployment using `outerbounds app delete --name my-first-app`, which will prompt you for confirmation and then proceed to delete your deployment. 

## Outerbounds UI

Currently, the Outerbounds UI provides you a view only mode for looking at your deployments, their configurations, logs and metrics around their health. On the left pane, look for the "Deployments" tab under "Projects". 

## <a id="endpoint-access"></a>Accessing your API endpoint

You can access your deployed endpoint programatically either locally (if you have a metaflow config) or via a Metaflow task running locally, `--with kubernetes` or with `argo-workflows`. 

To any request you make to the endpoint, you need to attach the headers returned from this function. 

```python 
def auth():
    from metaflow.metaflow_config_funcs import init_config
    conf = init_config()
    if conf:
        headers = {'x-api-key': conf['METAFLOW_SERVICE_AUTH_KEY']}
    else:
        headers = json.loads(os.environ['METAFLOW_SERVICE_HEADERS'])
    return headers
```

# Advanced Usage 

Configuration wise, the Outerbounds CLI exposes a number of options for you to configure the behavior of your deployment. You will find the complete list in [Configuration](./configuration.md). 