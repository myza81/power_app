import streamlit as st 
import pandas as pd

from applications.data_processing.dataframe import get_riched_df

SOURCE_METADATA = ["Phasor CSV", "BEN CSV", "Comtrade"]

@st.dialog("📋 File Details & Normalization Parameters", width="medium")
def add_metadata():
    
    file_name = st.session_state.get("current_file_name")
    if not file_name:
        st.warning("⚠️ No file loaded. Please upload a file first.")
        st.stop()

    st.markdown(f"**File:** `{file_name}`")

    substation_name = st.text_input(
        "Substation Mnemonic",
        placeholder="e.g., JMJG",
        key="substation_input",
        on_change=to_uppercase,
        args=("substation_input",),
    )
    bay_name = st.text_input(
        "Bay Name or Breaker no",
        placeholder="e.g., M10",
        key="bay_input",
        on_change=to_uppercase,
        args=("bay_input",),
    )
    source_file_option = st.selectbox(
        "Source File Type",
        SOURCE_METADATA,
        index=0,
        key="source_type_select",
        # help="Select the source file format.",
    )

    # metadata_submitted = False

    with st.form("normalization_form"):
        metadata_submitted = st.form_submit_button(
            "🔧  Add Metadata",
            type="primary",
            width="stretch",
            help="Add metadata for the uploaded file",
        )

    if metadata_submitted:
        substation_name = substation_name.upper().strip()
        bay_name = bay_name.upper().strip()

        correct_df = st.session_state["current_file_data"]
        if correct_df is None:
            st.error("❌ No valid file data in session.")
            st.stop()

        data_source = source_file_option.lower().replace(' ', '_')
        riched_df = get_riched_df(correct_df, data_source)

        uploaded = st.session_state.setdefault("uploaded_file", {})
        sub_dict = uploaded.setdefault(substation_name, {})
        sub_dict[bay_name] = {
            "file_name": file_name,
            "riched_df": riched_df,
        }

        st.rerun()


def to_uppercase(input_key):
    # Retrieve the raw input from the key and convert it to uppercase
    raw_input = st.session_state[input_key]
    upper_input = raw_input.upper()

    # If the converted value is different from the current value, 
    # update the session state to force the text box to display the uppercase version.
    if raw_input != upper_input:
        st.session_state[input_key] = upper_input