import streamlit as st
import pandas as pd
import numpy as np
from applications.data_processing.read_data import read_raw_data


from applications.load_shedding.data_processing.LoadShedding import (
    LoadShedding,
    LS_Data,
)
from applications.load_shedding.data_processing.load_profile import (
    load_profile_enrichment,
    load_profile_metric,
    df_search_filter,
)
from pages.load_shedding.tab1_data_viewer import ls_data_viewer
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

    show_table = st.checkbox("**Show Load Profile Data**", value=False)
    if show_table:
        total_mw = load_profile_df["Pload (MW)"].sum()
        total_mvar = load_profile_df["Qload (Mvar)"].sum()
        north_MW = load_profile_metric(load_profile_df, "North")
        kValley_MW = load_profile_metric(load_profile_df, "KlangValley")
        south_MW = load_profile_metric(load_profile_df, "South")
        east_MW = load_profile_metric(load_profile_df, "East")

        col_f1, col_f2 = st.columns(2)
        col_f1.metric(
            f"Active Power MD",
            f"{int(total_mw):,} MW",
        )

        with col_f2:
            colf2_1, colf2_2 = st.columns(2)
            with colf2_1:
                st.metric(
                    label="North",
                    value=f"{int(north_MW):,} MW",
                )
                st.metric(
                    label="Klang Valley",
                    value=f"{int(kValley_MW):,} MW",
                )
            with colf2_2:
                st.metric(
                    label="South",
                    value=f"{int(south_MW):,} MW",
                )
                st.metric(
                    label="East",
                    value=f"{int(east_MW):,} MW",
                )

        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search term here...",  
            key="search_box", 
        )

        filtered_df = df_search_filter(load_profile_df, search_query)

        if filtered_df.empty and search_query:
            st.warning(f"No results found for the query: **'{search_query}'**")
            max_rows = 0
            rows_to_display = 0
        else:
            max_rows = len(filtered_df)
            rows_to_display = st.slider(
                "Select number of rows to display:",
                min_value=1,
                max_value=max_rows,
                value=min(5, max_rows) if max_rows > 1 else 1,
                step=1,
                help=f"Currently filtering from {len(load_profile_df)} total rows. {max_rows} rows match the search query.",
            )
            st.dataframe(filtered_df.head(rows_to_display), width="stretch")

    tab1, tab2, tab3 = st.tabs(
        ["Data Viewer", "Reviewer", "Critical Load List"]
    )

    with tab1:
        ls_data_viewer()
    with tab3:
        critical_list()
    
