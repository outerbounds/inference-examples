# coding: utf-8
import requests
import os

def get_auth_headers():
    if os.environ.get('METAFLOW_SERVICE_AUTH_KEY'):
        return {"x-api-key": os.environ.get('METAFLOW_SERVICE_AUTH_KEY')}
    from outerbounds_app_client import OuterboundsAppClient
    return OuterboundsAppClient().get_auth_headers()


headers = get_auth_headers()
# TODO: Change to your own endpoint
url = "https://api-c-egy05g.dev-yellow.outerbounds.xyz"
print(requests.get(url, headers=headers).text)
