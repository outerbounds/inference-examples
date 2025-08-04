# Streamlit Sample App

This is a sample Streamlit application that demonstrates basic functionality including data display, interactive widgets, and charts while using Metaflow client. 

## Development

First, install the required dependencies:
```
pip install -r requirements.txt
```

To run the app locally:
```
streamlit run main.py
```

The app will be available at http://localhost:8501

## Deployment

To deploy the app using Outerbounds:
```sh
outerbounds app deploy --name mf-st-app --port 8501 -- streamlit run visualize.py
```

Note: Streamlit uses port 8501 by default. Make sure to use this port when deploying. 