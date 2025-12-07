import pandas as pd
import streamlit as st
from applications.load_shedding.data_processing.load_profile import (
    df_search_filter,
)
from applications.load_shedding.data_processing.helper import columns_list


def critical_list():
    loadshedding = st.session_state["loadshedding"]
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting

    ########## debugging info ##########

    # st.dataframe(loadshedding.flaglist_overlap_active_loadshedding())
    # st.dataframe(loadshedding.flaglist_ls_assignment_mapping())
    # st.divider()

    ########## debugging info ##########

    st.subheader(
        "Overlap Critical Load List with Existing Load Shedding Scheme")

    tab3_col1, tab3_col2, tab3_col3, tab3_col4 = st.columns(4)

    with tab3_col1:
        review_year_list = columns_list(
            loadshedding.ufls_assignment, unwanted_el=["assignment_id"])
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(
            label="Review Year", options=review_year_list, key="overlap_flaglist_review_year")

    with tab3_col2:
        ls_scheme = st.multiselect(label="Scheme", options=[
                                   "UFLS", "UVLS", "EMLS"], key="overlap_flaglist_scheme")

    with tab3_col3:
        ls_stage_options = ufls_setting.columns.tolist()
        if len(ls_scheme) == 1 and ls_scheme[0] == "UVLS":
            ls_stage_options = uvls_setting.columns.tolist()

        stage_selected = st.multiselect(
            label="Operating Stage", options=ls_stage_options, key="overlap_flaglist_stage"
        )

    with tab3_col4:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="overlap_flaglist_search_box",
        )

    filters = {
        "review_year": review_year,
        "scheme": ls_scheme,
        "UFLS": stage_selected,
        "UVLS": stage_selected,
        "EMLS": stage_selected,
    }

    filtered_data = loadshedding.filtered_data(filters=filters)

    if isinstance(filtered_data, pd.DataFrame):
        overlap_list = filtered_data.loc[(filtered_data['critical_list'] == 'dn') | (
            filtered_data['critical_list'] == 'gso')]
        if not overlap_list.empty:
            filtered_df = df_search_filter(overlap_list, search_query)
            st.dataframe(
                filtered_df,
                column_order=["UFLS", "UVLS",
                              "EMLS", 'mnemonic', 'kV', "assignment_id", "short_text"],
                width="stretch",
                hide_index=True
            )
        else:
            st.write(overlap_list)
    else:
        st.info("No active load shedding assignment found for the selected filters.")

    st.divider()

    show_all_warning_list = st.checkbox(
        "**Show All Critical Load (Non-overlap & Overlap)**", value=False)

    if show_all_warning_list:
        flag_list = loadshedding.flaglist()

        st.subheader("List of Critical Load from GSO & DSO")
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="flaglist_search_box",
        )
        filtered_df = df_search_filter(flag_list, search_query)
        st.dataframe(
            filtered_df,
            column_order=["local_trip_id", "short_text", "category"],
            width="stretch"
        )
