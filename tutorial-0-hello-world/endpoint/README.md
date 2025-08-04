# hello World *Endpoints*

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