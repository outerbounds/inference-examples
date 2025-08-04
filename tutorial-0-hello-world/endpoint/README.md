# Hello World API Deployment

A simple Flask app that returns a "Hello, World!" at "/". This deployment will only be accessible via API endpoints. To consume it in your browser, see [the UI app example](../app/).

Deploy a flask API Server **Endpoint**

## Development
```
pip install -r requirements.txt
```

```
python main.py
```

## Deployment

```sh
outerbounds app deploy --name basic-endpoint --port 8000 --auth-type API -- python main.py
```

## Consuming the API endpoint: 

Here's an example of consuming the generated endpoint: 

```python
import requests 

def auth():
    from metaflow.metaflow_config_funcs import init_config
    conf = init_config()
    if conf:
        headers = {'x-api-key': conf['METAFLOW_SERVICE_AUTH_KEY']}
    else:
        headers = json.loads(os.environ['METAFLOW_SERVICE_HEADERS'])
    return headers

endpoint_url = "your-url-goes-here"

resp = requests.get(endpoint_url, headers = auth())
print(resp)
```