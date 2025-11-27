import streamlit as st
import pandas as pd

from applications.data_processing.read_data import find_correct_header
from applications.data_processing.modal_dialog import add_metadata

# import tab1_data_viewer, tab2_data_plotting
from pages.generator_response.tab1_data_viewer import data_viewer
from pages.generator_response.tab2_data_plotting import data_plotting


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
    required_keywords = ["freq"]
    optional_groups = [["date", "timestamp"], ['mw', "v1", "i1"]]
    file_name = uploaded_file.name

    # 1. Check if a NEW file has been uploaded (or if this is the first file)
    if (
        "current_file_name" not in st.session_state
        or st.session_state["current_file_name"] != file_name
    ):
        # 2. Reset / Clear old state data (Optional: clear the entire dictionary if you don't need history)
        if "current_file_data" in st.session_state:
            del st.session_state["current_file_data"]

        # 3. Update the tracker to the new file's name
        st.session_state["current_file_name"] = file_name

    try:
        result = find_correct_header(uploaded_file, required_keywords, optional_groups)
        raw_df, corrected_df, missing_keyword = result

        if raw_df is not None:

            if isinstance(corrected_df, ValueError):
                # Keyword not found → show warning but still continue
                st.sidebar.error(f"⚠️ {corrected_df}")
                with tab1:
                    data_viewer(raw_df=raw_df)

            else:
                # Keywords found → use the detected header
                if "current_file_data" not in st.session_state:
                    st.session_state["current_file_data"] = {}
                
                st.session_state["current_file_data"] = corrected_df
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
                    data_viewer(raw_df=raw_df, correct_df=corrected_df)

                with tab2:
                    
                    data_plotting()
        else:
            st.sidebar.warning("⚠️ File uploaded, but data appears empty or invalid.")

    except ValueError as e:
        st.sidebar.error(f"❌ {e}")
        st.stop()

    except Exception as e:
        # Catch all other unexpected issues
        st.sidebar.error(f"❌ Unexpected error: {e}")
        st.stop()
