# Hello World UI Deployment

A simple Flask app that returns a "Hello, World!" at "/". This deployment will only be accessible via your browser. To consume it as an API instead, see [the endpoint example](../endpoint).

## Development
```
pip install -r requirements.txt
```

```
python main.py
```

## Deployment

```sh
outerbounds app deploy --name basic-app --port 8000 -- python main.py
```

This command will print out a URL that you can click on to access the endpoint on your browser. 