
# Running vLLM with your custom LLM 

```sh
outerbounds app deploy --config-file app-config.yaml
```

Downloads your LLM weights from either S3 or S3 compatible storage like CAIOS and serves it via vLLM. Note that you will need to have secrets configured on the platform for Coreweave storage access. 

## Interacting with the deployed API Endpoint

[client.py](client.py) is an implementation that showcases how to interact with the deployed vllm endpoint using the OpenAI client.Copy the URL of the endpoint created in the previous step and call it via the OpenAI client like: 
```
python client.py --url "https://api-c-oik87o.dev-yellow.outerbounds.xyz" --prompt "what day is it today"
```

### Accessing the Model

```sh
# Replace the server url with your own
python scoring_client.py --online --server-url "https://api-c-72jrq9.dev-yellow.outerbounds.xyz" --text1 "I used to live in india" --text2 "paris is a city in texas"
```