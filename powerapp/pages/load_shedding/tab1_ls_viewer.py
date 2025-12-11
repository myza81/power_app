import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Any

from applications.load_shedding.helper import (columns_list, column_data_list)
from applications.data_processing.read_data import df_search_filter
from pages.load_shedding.helper import display_ls_metrics


def ls_data_viewer() -> None:
    load_profile_df = st.session_state["load_profile"] 
    loadshedding = st.session_state["loadshedding"]

    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    subs_metadata = loadshedding.subs_metadata_enrichment()
    zone_mapping = loadshedding.zone_mapping
    loadshedding_dp = loadshedding.merged_dp()

    LOADSHED_SCHEME = ["UFLS", "UVLS", "EMLS"]

    st.subheader("Active Load Sheddding Assignment")

    show_table = st.checkbox("**Show Active Load Shedding Assignment List**", value=False)

    if show_table:
        col1_1, col1_2, col1_3 = st.columns(3)
        col2_1, col2_2, col2_3 = st.columns(3)

        with col1_1:
            review_year_list = columns_list(ufls_assignment, unwanted_el=["assignment_id"])
            review_year_list.sort(reverse=True)
            review_year = st.selectbox(label="Review Year", options=review_year_list)

        with col1_2:
            ls_scheme = st.multiselect(label="Scheme", options=LOADSHED_SCHEME, default="UFLS")
            selected_ls_scheme = LOADSHED_SCHEME if ls_scheme == [] else ls_scheme

        with col1_3:
            zone = list(set(zone_mapping.values()))
            zone_selected = st.multiselect(label="Regional Zone", options=zone)

        with col2_1:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(label="Grid Maintenace Subzone", options=subzone)

        with col2_2:
            ls_stage_options = ufls_setting.columns.tolist()
            if len(selected_ls_scheme) == 1 and selected_ls_scheme[0] == "UVLS":
                ls_stage_options = uvls_setting.columns.tolist()

            stage_selected = st.multiselect(
                label="Operating Stage", options=ls_stage_options
            )

        with col2_3:
            ls_dp = list(set(loadshedding_dp["ls_dp"]))
            trip_assignment = st.multiselect(
                label="Tripping Assignment",
                options=ls_dp,
            )

        filters ={
            "review_year": review_year,
            "scheme": selected_ls_scheme,
            "op_stage": stage_selected,
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
            "ls_dp": trip_assignment,
        }

        if "load_profile" not in st.session_state:
            st.info("Please upload or set a load profile first.")
            return

        masterlist_ls = loadshedding.ls_assignment_masterlist()
        filtered_data = loadshedding.filtered_data(filters=filters, df=masterlist_ls)

        if not filtered_data.empty:
            col3_1, col3_2, col3_3 = st.columns(3)

            with col3_1:
                search_query = st.text_input(
                    label="Search for a Keyword:",
                    placeholder="Enter your search keyword here...", 
                    key="active_ls_search_box",
                )
                filtered_df = df_search_filter(filtered_data, search_query)                
            
            ls_cols = [col for col in filtered_df.columns if any(
                keyword in col for keyword in LOADSHED_SCHEME)]
            other_cols = ["zone", "gm_subzone", "substation_name", "mnemonic", "kV", "breaker_id", "ls_dp", "assignment_id", "Pload (MW)"]
            insertion_point = other_cols.index("kV") + 1
            col_seq = other_cols[:insertion_point] + ls_cols + other_cols[insertion_point:]

            st.dataframe(
                filtered_df, column_order=col_seq, width="stretch", hide_index=True
            )

            SCHEME_COLUMNS = ls_cols
            for scheme in SCHEME_COLUMNS:
                if scheme in filtered_df.columns:
                    display_ls_metrics(
                        scheme=scheme, df=filtered_df, load_profile=load_profile_df
                    )
        else:
            st.info("No active load shedding assignment found for the selected filters.")
