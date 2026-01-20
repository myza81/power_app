import streamlit as st
from applications.data_processing.read_data import read_raw_data
from applications.load_shedding.LoadShedding import LoadShedding
from applications.load_shedding.LoadProfile import LoadProfile
from pages.load_shedding.tab1_loadprofile import loadprofile_main
from pages.load_shedding.tab2_assignment import ls_assignment_main
from pages.load_shedding.tab3_analytics import ls_analytics_main
from pages.load_shedding.tab4_simulator import simulator
from pages.load_shedding.tab5_critical_list import critical_list


st.set_page_config(layout="wide", page_title="UFLS")

if "loadprofile" not in st.session_state:
    st.session_state["loadprofile"] = None

if "loadshedding" not in st.session_state:
    st.session_state["loadshedding"] = None

if "simulator" not in st.session_state:
    st.session_state["simulator"] = None


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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Load Profile",
        "Assignments",
        "Analytics",
        "Simulator",
        "Critical Load List",
    ])

    with tab1:
        loadprofile_main()

    with tab2:
        ls_assignment_main()

    with tab3:
        ls_analytics_main()

    with tab4:
        simulator()
        pass

    with tab5:
        critical_list()

else:
    st.info("Please upload or set a load profile first.")
