
# Running VLLM API Endpoint

```sh
outerbounds app deploy --config-file app-config.yaml
```

## Experimenting with Different models

```sh
outerbounds app deploy --config-file app-config.yaml --env "MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct"
```
Running the above command will yield an output like : 
```
2025-05-27 17:10:33.977 🚀 Deploying vllm-app to the Outerbounds platform...
2025-05-27 17:10:33.977 📦 Packaging Directory : /home/ubuntu/inference-examples/examples/tutorial-1-streamlit-sample/vllm
2025-05-27 17:10:34.246 🍞 Baking Docker Image
2025-05-27 17:10:34.246 🐳 Using The Docker Image : registry.hub.docker.com/vllm/vllm-openai:latest
2025-05-27 17:10:34.696 💾 Code Package Saved to : s3://obp-sk0bzb-metaflow/metaflow/mf.obp-apps/08/0864b61b456daf0532c1022f3d20f6cb01e40ade
2025-05-27 17:10:34.699 🚀 Deploying endpoint to the platform...
2025-05-27 17:10:35.735 🔧 🛠️ Updating Endpoint c-oik87o
2025-05-27 17:10:35.735 💊 Endpoint c-oik87o is ready to serve traffic on the URL: https://api-c-oik87o.dev-yellow.outerbounds.xyz
2025-05-27 17:10:35.735 💊 Endpoint vllm-app (c-oik87o) deployed successfully! You can access it at https://api-c-oik87o.dev-yellow.outerbounds.xyz
```

## Interacting with the deployed API Endpoint

[client.py](client.py) is an implementation that showcases how to interact with the deployed vllm endpoint using the OpenAI client.Copy the URL of the endpoint created in the previous step and call it via the OpenAI client like: 
```
python client.py --url "https://api-c-oik87o.dev-yellow.outerbounds.xyz" --prompt "what day is it today"
```

## Mordern Bert 

[Config file](./mordern-bert-conf.yaml)
### Deployment 
```
outerbounds app deploy --config-file ./mordern-bert-conf.yaml
```

### Accessing the Model

```sh
# Replace the server url with your own
python scoring_client.py --online --server-url "https://api-c-72jrq9.dev-yellow.outerbounds.xyz" --text1 "I used to live in india" --text2 "paris is a city in texas"
```