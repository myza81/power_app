import streamlit as st
import pandas as pd

from applications.generator_response.data_serialization.read_data import find_correct_header
from applications.generator_response.data_serialization.modal_dialog import add_metadata

# import tab1_data_viewer, tab2_data_plotting
from pages.generator_response.tab1_data_viewer import data_viewer


st.set_page_config(layout="wide", page_title="Generator Response")

# --- Side Bar --- #
st.sidebar.header("📁 File Loader")
st.sidebar.write("Upload a CSV or Excel file to view its contents.")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

# --- Main UI --- #
st.title("Generator Response")
st.markdown("Use the tabs below to navigate between different views.")
tab1, tab2 = st.tabs(["Data Viewer", "Data Plotting"])


# --- File Handling Logic --- #
if uploaded_file is not None:
    keywords = ["date", "frequency"]
    file_name = uploaded_file.name

    # 1. Check if a NEW file has been uploaded (or if this is the first file)
    if (
        "current_file_name" not in st.session_state
        or st.session_state["current_file_name"] != file_name
    ):
        # 2. Reset / Clear old state data (Optional: clear the entire dictionary if you don't need history)
        if "current_file_data" in st.session_state:
            # Clear all cached file data when a new file is uploaded
            del st.session_state["current_file_data"]

        # 3. Update the tracker to the new file's name
        st.session_state["current_file_name"] = file_name

    try:
        uploaded_df = find_correct_header(uploaded_file, keywords)

        if uploaded_df is not None:

            if "current_file_data" not in st.session_state:
                st.session_state["current_file_data"] = {}

            st.session_state["current_file_data"] = uploaded_df

            # if file_name not in st.session_state["uploaded_file"]:
            #     st.session_state["uploaded_file"][file_name] = {}
            #     st.session_state["uploaded_file"][file_name] = uploaded_df

            st.sidebar.success(f"✅ {file_name} uploaded successfully!")

            ## --- Button to add metadata into file --- ##
            normalize_btn = st.sidebar.button(
                "🔧 Normalize Data",
                type="primary",
                width="stretch",
                help="Click to process and normalize the uploaded data",
            )

            if normalize_btn:
                try:
                    add_metadata()
                except Exception as e:
                    st.error(f"❌ Failed to normalize data: {e}")
            ## --- END Button to add metadata into file --- ##

            with tab1:
                data_viewer()
        else:
            st.sidebar.warning("⚠️ File uploaded, but data appears empty or invalid.")

    except Exception as e:
        st.sidebar.error(f"❌ Failed to process file: {e}")
        st.stop()
