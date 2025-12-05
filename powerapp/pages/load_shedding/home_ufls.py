import streamlit as st
from applications.data_processing.read_data import read_raw_data
from applications.load_shedding.data_processing.LoadShedding import (
    LS_Data,
)
from applications.load_shedding.data_processing.load_profile import (
    load_profile_enrichment,
)
from pages.load_shedding.tab1_data_viewer import display_load_profile, ls_data_viewer
from pages.load_shedding.tab3_critical_list import critical_list


st.set_page_config(layout="wide", page_title="UFLS")

if "load_profile" not in st.session_state:
    st.session_state["load_profile"] = None

if "ls_data" not in st.session_state:
    st.session_state["ls_data"] = None

if "loadshedding" not in st.session_state:
    st.session_state["loadshedding"] = None

# --- Side Bar --- #
st.sidebar.header("📁 Upload Latest Load Profile.")
load_profile_uploader = st.sidebar.file_uploader("Choose file", type=["csv", "xlsx", "xls"])

# --- Main UI --- #
st.title("Defense Scheme - Load Shedding")

load_profile_df = st.session_state["load_profile"]

if load_profile_uploader is not None:
    file_bytes = load_profile_uploader.read()
    load_file = read_raw_data(file_bytes, load_profile_uploader.name)
    load_profile_df = load_profile_enrichment(load_file)
    st.session_state["load_profile"] = load_profile_df

if load_profile_df is not None:
    ls_data = LS_Data(load_profile=load_profile_df)
    st.session_state["ls_data"] = ls_data

    tab1, tab2, tab3 = st.tabs(
        ["Data Viewer", "Reviewer", "Critical Load List"]
    )

    with tab1:
        display_load_profile()
        ls_data_viewer()
    with tab3:
        critical_list()
    
