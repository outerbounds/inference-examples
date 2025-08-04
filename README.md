# Inference Tutorials on Outerbounds

This repository contains a set of examples to get started with running inference services on Outerbounds. 

In the Outerbounds universe, each inference services is called a "Deployment". For the remainder of this doc, when we say "Deployments", we mean inference services. 

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

You can run the same command over & over as you make changes to your code, dependencies or configuration of the deployment. 
    
Some notes about the command: 

1. Provide whatever port you expect to run your deployment on. 
2. The part after `--` should be what you would use if you were looking to run your deployment locally. 
3. By default, a Deployment is accessible via the browser. If you provide `--auth-type API`, then the Deployment will not be accessible via your browser, and instead via an API endpoint. See [accessing your API endpoint]() on details about how to access an API endpoint. 

You can configure your deployment either using CLI flags or using a config schema. For more details, take a look at [Configuration](./configuration.md). 

### Listing all Deployments

You can run `outerbounds app list` to list all Deployments currently running on the platform. 

### Deleting your deployment 

You can delete your deployment using `outerbounds app delete --name my-first-app`, which will prompt you for confirmation and then proceed to delete your deployment. 

## Outerbounds UI

Currently, the Outerbounds UI provides you a view only mode for looking at your deployments, their configurations, logs and metrics around their health. On the left pane, look for the "Deployments" tab under "Projects". 

## Accessing your API endpoint

# Advanced Usage 

Configuration wise, the Outerbounds CLI exposes a number of options for you to configure the behavior of your deployment. You will find the complete list in [Configuration](./configuration.md). 