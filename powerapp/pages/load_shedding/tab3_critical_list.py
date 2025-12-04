import pandas as pd
import streamlit as st
from applications.load_shedding.data_processing.load_profile import (
    df_search_filter,
)


def critical_list():
    load_profile_df = st.session_state["load_profile"]
    loadshedding = st.session_state["loadshedding"]
    defeated_list = loadshedding.warning_list()
    all_ls_with_warning = loadshedding.warning_list_with_active_ls()

    if isinstance(all_ls_with_warning, pd.DataFrame):
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="overlap_warning_list_search_box",
        )
        filtered_df = df_search_filter(all_ls_with_warning, search_query)

        st.dataframe(
            filtered_df,
            column_order=["group_trip_id", "UFLS",
                          "UVLS", "EMLS", "remark", "category"],
            width="stretch"
        )
    else:
        st.write(all_ls_with_warning)

    show_all_warning_list = st.checkbox(
        "**Show All Critical Load**", value=False)
    if show_all_warning_list:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="warning_list_search_box",
        )
        filtered_df = df_search_filter(defeated_list, search_query)
        st.dataframe(
            filtered_df,
            column_order=["group_trip_id", "date", "remark", "category"],
            width="stretch"
        )

