import streamlit as st 
import pandas as pd

from powerapp.applications.generator_response.calculation.mw_mvar import (
    calculate_mw_mvar,
)

# from powerapp.applications.generator_response.data_serialization.data_normalisation import get_riched_df


@st.dialog("📋 File Details & Normalization Parameters", width="medium")
def add_metadata():
    file_name = st.session_state["current_file_name"]
    st.markdown(f"**File:** `{file_name}`")

    substation_name = st.text_input(
        "Substation Mnemonic",
        placeholder="e.g., JMJG",
        key="substation_input",
        help="Substation Mnemonic for the uploaded file.",
    )
    bay_name = st.text_input(
        "Bay Name or Breaker no",
        placeholder="e.g., M10",
        key="bay_input",
        help="Bay unit number.",
    )
    source_file_option = st.selectbox(
        "Source File Type",
        ["Phasor CSV", "BEN CSV", "Comtrade"],
        index=0,
        key="source_type_select",
        help="Select the source file format.",
    )

    metadata_submitted = False

    with st.form("normalization_form", clear_on_submit=True):
        metadata_submitted = st.form_submit_button(
            "🔧 Normalize Data",
            type="primary",
            width="stretch",
            help="Add metadata for the uploaded file",
        )

    if metadata_submitted:

        (raw_df, correct_df) = st.session_state["current_file_data"]
        riched_df = get_riched_df(correct_df, source_file_option)

        if substation_name not in st.session_state:
            st.session_state[substation_name] = {}

        if bay_name not in st.session_state[substation_name]:
            st.session_state[substation_name][bay_name] = {}

        st.session_state[substation_name][bay_name] = {
            "file_name": st.session_state["current_file_name"],
            "raw_data": raw_df,
            "correct_df": correct_df,
            "riched_df": riched_df,
        }


def get_riched_df(df, source_data):
    if source_data == "phasor":
        return phasor_data(df, source_data)
    elif source_data == "ben":
        return


def phasor_data(df, source_data):
    clean_df = df.copy()
    timestamp = clean_df["Date"] + " " + clean_df["Time (Asia/Singapore)"]
    clean_df["Timestamp"] = pd.to_datetime(timestamp, format="%m/%d/%y %H:%M:%S.%f")
    calc = calculate_mw_mvar(clean_df, source_data)
    clean_df["MW"] = calc.get("MW")
    clean_df["Mvar"] = calc.get("Mvar")

    return clean_df
