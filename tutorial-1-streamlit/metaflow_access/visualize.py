"""
Dataframe visualizer Streamlit app that takes Metaflow Flows/paths etc and then figures out 
the artifacts that are dataframes and displays them in a table.
"""

import streamlit as st
import pandas as pd
from metaflow import Flow, namespace, Task
from typing import List, Dict, Any
from datetime import datetime

namespace(None)


def get_top_runs(flow_name: str, n: int = 5) -> List[Dict[str, Any]]:
    """Get the top N most recent runs for a given flow with additional metadata."""
    flow = Flow(flow_name)
    runs = []
    for run in flow.runs():
        created_at = run.created_at
        runs.append(
            {
                "run_id": run.id,
                "created_at": created_at,
                "status": run.finished,
                "tags": run.tags,
            }
        )
    # Sort by created_at descending and take top N
    return sorted(runs, key=lambda x: x["created_at"], reverse=True)[:n]


def get_dataframe_from_pathspec(
    flow_name: str, pathspec: str
) -> Dict[str, pd.DataFrame]:
    """
    Retrieve DataFrame artifacts from a specific pathspec.
    Returns a dictionary of artifact name to dataframe.
    """
    try:
        task = Task(pathspec)
        dataframes = {}

        for key, value in task.data.items():
            if isinstance(value, pd.DataFrame):
                dataframes[key] = value

        return dataframes
    except Exception as e:
        st.error(f"Error accessing pathspec: {str(e)}")
        return {}


def get_dataframe_artifacts(flow_name: str, run_id: str) -> Dict[str, pd.DataFrame]:
    """
    Retrieve all dataframe artifacts from a specific flow run.
    Returns a dictionary of artifact name to dataframe.
    """
    run = Flow(flow_name)[run_id]
    dataframes = {}

    for step in run:
        for task in step:
            for data_art in task:
                if isinstance(data_art.data, pd.DataFrame):
                    dataframes[data_art.pathspec] = data_art.data

    return dataframes


# Set up the Streamlit page
st.set_page_config(page_title="Metaflow DataFrame Visualizer", layout="wide")
st.title("Metaflow DataFrame Visualizer")

# Input flow name
flow_name = st.text_input(
    "Enter Flow Name", key="flow_name", value="ECommerceAnalysisFlow"
)

if flow_name:
    # Selection mode
    selection_mode = st.radio(
        "Select access mode",
        ["Recent Runs", "Custom Pathspec"],
        help="Choose whether to select from recent runs or enter a specific pathspec",
    )

    dataframes = {}

    if selection_mode == "Recent Runs":
        top_runs = get_top_runs(flow_name)
        if top_runs:
            # Create a more informative selection box
            run_options = [
                f"Run: {run['run_id']} | {run['created_at'].strftime('%Y-%m-%d %H:%M:%S')} | {run['status']} | {run['tags']}"
                for run in top_runs
            ]
            selected_run_index = st.selectbox(
                "Select a recent run",
                range(len(run_options)),
                format_func=lambda x: run_options[x],
            )

            if selected_run_index is not None:
                selected_run = top_runs[selected_run_index]
                dataframes = get_dataframe_artifacts(flow_name, selected_run["run_id"])
        else:
            st.warning(f"No runs found for flow: {flow_name}")

    else:  # Custom Pathspec
        pathspec = st.text_input(
            "Enter pathspec",
            help="Format: run_id/step_name/task_id (e.g., 'run_123/start/1')",
        )
        if pathspec:
            dataframes = get_dataframe_from_pathspec(flow_name, pathspec)

    # Display DataFrames
    if dataframes:
        # Create tabs for each dataframe
        tabs = st.tabs(list(dataframes.keys()))

        for tab, (name, df) in zip(tabs, dataframes.items()):
            with tab:
                st.subheader(f"Artifact: {name}")
                st.dataframe(df, use_container_width=True)

                # Show basic DataFrame info
                st.write("DataFrame Info:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"Shape: {df.shape}")
                with col2:
                    st.write(f"Columns: {', '.join(df.columns)}")
                with col3:
                    st.write(
                        f"Memory Usage: {df.memory_usage().sum() / 1024**2:.2f} MB"
                    )

                # Add download button for each DataFrame
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{name.replace('/', '_')}.csv",
                    mime="text/csv",
                )
    elif selection_mode == "Recent Runs" and not top_runs:
        pass  # Warning already shown
    elif selection_mode == "Custom Pathspec" and pathspec:
        st.info("No DataFrame artifacts found in this pathspec.")
else:
    st.info("Please enter a flow name to begin.")
