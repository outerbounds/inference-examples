from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.route("/api/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
