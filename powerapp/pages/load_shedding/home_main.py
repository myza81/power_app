import streamlit as st
from applications.data_processing.read_data import read_raw_data
from applications.load_shedding.LoadShedding import LoadShedding
from applications.load_shedding.LoadProfile import LoadProfile
from pages.load_shedding.tab1a_loadprofile import loadprofile_main
from pages.load_shedding.tab1b_assignment import loadshedding_assignment
from pages.load_shedding.tab1c_analytics import ls_analytics
from pages.load_shedding.tab2_reviewer import ls_reviewer
from pages.load_shedding.tab3_critical_list import critical_list
from pages.load_shedding.tab3_overlap_ls import overlap_ls
from pages.load_shedding.tab1d_ls_subset import loadshedding_subset
from pages.load_shedding.tab4_debug import debug

st.set_page_config(layout="wide", page_title="UFLS")

if "loadprofile" not in st.session_state:
    st.session_state["loadprofile"] = None

if "loadshedding" not in st.session_state:
    st.session_state["loadshedding"] = None


st.sidebar.header("📁 Upload Latest Load Profile.")
load_profile_uploader = st.sidebar.file_uploader(
    "Choose file", type=["csv", "xlsx", "xls"])

st.title("Defense Scheme - Load Shedding")

if load_profile_uploader is not None:
    file_bytes = load_profile_uploader.read()
    load_file = read_raw_data(file_bytes, load_profile_uploader.name)
    loadprofile = LoadProfile(load_profile=load_file)
    st.session_state["loadprofile"] = loadprofile
    st.session_state["loadshedding"] = LoadShedding(load_df=loadprofile.df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Load Profile",
        "Assignments",
        "Analytics",
        "Simulator",
        "Critical Load List",
        "Debugging"
    ])

    with tab1:
        loadprofile_main()
        st.divider()
    with tab2:
        loadshedding_assignment()
        st.divider()
    with tab3:
        ls_analytics()
        st.divider()
        # loadshedding_subset()
    with tab4:
        # ls_reviewer()
        st.divider()
    with tab5:
        # critical_list()
        st.divider()
        # overlap_ls()

    with tab6:
        debug()

else:
    st.info("Please upload or set a load profile first.")
