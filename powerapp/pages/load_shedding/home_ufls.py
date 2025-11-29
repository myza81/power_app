import streamlit as st
from applications.data_processing.read_data import read_raw_data
from pages.load_shedding.tab1_data_viewer import ls_data_viewer
from applications.load_shedding.data_processing.LoadShedding import (
    # LoadShedding,
    LS_Data,
)


st.set_page_config(layout="wide", page_title="UFLS")

if "load_profile" not in st.session_state:
    st.session_state["load_profile"] = None

if "ls_data" not in st.session_state:
    st.session_state["ls_data"] = None

# --- Side Bar --- #
st.sidebar.header("📁 Upload Latest Load Profile.")
load_profile_uploader = st.sidebar.file_uploader("Choose file", type=["csv", "xlsx", "xls"])

# --- Main UI --- #
st.title("Defense Scheme - Load Shedding")

load_profile = st.session_state["load_profile"]
if load_profile_uploader is not None:
    file_bytes = load_profile_uploader.read()
    load_profile = read_raw_data(file_bytes, load_profile_uploader.name)
    st.session_state["load_profile"] = load_profile

if load_profile is not None:

    ls_data = LS_Data(load_profile=load_profile)
    st.session_state["ls_data"] = ls_data

    show_table = st.checkbox("**Show Load Profile Raw Data**", value=False)
    if show_table:
        total_mw = load_profile["Pload (MW)"].sum()
        total_mvar = load_profile["Qload (Mvar)"].sum()

        col_f1, col_f2 = st.columns(2)
        col_f1.metric(
            f"Active Power MD",
            f"{int(total_mw):,} MW",
        )
        # col_f2.metric(
        #     f"Reactive Power MD",
        #     f"{int(total_mvar):,} MVar",
        # )

        max_rows = len(load_profile)
        rows_to_display = st.slider(
            "Select number of rows to display:",
            min_value=5,
            max_value=max_rows,
            value=min(5, max_rows),
            step=1,
            help="Use this slider to change how many rows of the raw data are visible.",
        )
        st.dataframe(load_profile.head(rows_to_display), width="content")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Data Viewer", "UVLS", "EMLS", "Critical Load List", "Reviewer"]
    )

    with tab1:
        ls_data_viewer()
