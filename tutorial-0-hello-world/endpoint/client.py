# coding: utf-8
import requests
import os

def auth():
    from metaflow.metaflow_config_funcs import init_config
    conf = init_config()
    if conf:
        headers = {'x-api-key': conf['METAFLOW_SERVICE_AUTH_KEY']}
    else:
        headers = json.loads(os.environ['METAFLOW_SERVICE_HEADERS'])
    return headers


headers = auth()
# TODO: Change to your own endpoint
url = "https://api-c-egy05g.dev-yellow.outerbounds.xyz"
print(requests.get(url, headers=headers).text)
