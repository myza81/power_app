import streamlit as st
from applications.data_processing.read_data import read_raw_data

st.set_page_config(layout="wide", page_title="UFLS")

if "load_profile" not in st.session_state:
    st.session_state["load_profile"] = None

# --- Side Bar --- #
st.sidebar.header("📁 Upload Latest Load Profile.")
load_profile_uploader = st.sidebar.file_uploader("", type=["csv", "xlsx", "xls"])

# --- Main UI --- #
st.title("Defense Scheme - Load Shedding")

load_profile = st.session_state["load_profile"]
if load_profile_uploader is not None:
    file_bytes = load_profile_uploader.read()
    load_profile = read_raw_data(file_bytes, load_profile_uploader.name)
    st.session_state["load_profile"] = load_profile

if load_profile is not None:
    show_table = st.checkbox("**Show Load Profile Raw Data**", value=False)
    if show_table:
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
        ["UFLS", "UVLS", "EMLS", "Critical Load List", "Reviewer"]
    )

    if load_profile is not None:

        with tab1:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                review_year = st.selectbox(label="UFLS Review", options = ["2024", "2025"])

            with col2:
                zone_loc = st.selectbox(
                    label="Zone Location",
                    options=["All", "South", "KlangValley", "North", "East"],
                )

            with col3:
                gm_subzone = st.selectbox(
                    label="GM Subzone",
                    options=["All", "South", "KlangValley", "North", "East"],
                )

            with col4:
                stage = st.selectbox(
                    label="Operating Stage",
                    options=["All", "Stage 1", "Stage 2", "Stage 3", "Stage 4"],
                )

            with col5:
                trip_assignment = st.selectbox(
                    label="Tripping Assignment",
                    options=["All", "Local Load", "Pocket Load"],
                )
