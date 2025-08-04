import streamlit as st
import pandas as pd
import numpy as np

st.title("Streamlit Sample App")

st.write(
    """
This is a sample Streamlit app that demonstrates basic functionality.
You can use this as a template for your own apps!
"""
)

# Create a sample dataframe
df = pd.DataFrame(
    {"first column": list(range(1, 6)), "second column": np.random.randn(5)}
)

# Display the dataframe
st.write("Here's a sample DataFrame:")
st.dataframe(df)

# Add an interactive slider
number = st.slider("Select a number:", 0, 100, 50)
st.write(f"You selected: {number}")

# Add a chart
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.line_chart(chart_data)
