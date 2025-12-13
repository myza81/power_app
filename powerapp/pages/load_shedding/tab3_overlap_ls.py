import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
from applications.load_shedding.load_profile import df_search_filter
from applications.load_shedding.helper import (
    column_data_list, scheme_col_sorted)
from pages.load_shedding.tab3_dashboard import critical_list_dashboard


def overlap_ls():
    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    zone_mapping = loadshedding.zone_mapping
    subs_metadata = loadshedding.subs_metadata_enrichment()
    dp_flaglist = loadshedding.merged_dp_with_flaglist()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    st.subheader(
        "Overlap Critical Load List with Existing Load Shedding Scheme")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        review_year_list = ufls_assignment.columns.drop(
            "assignment_id", errors="ignore"
        ).tolist()
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(
            label="Review Year",
            options=review_year_list,
            key="overlap_flaglist_review_year",
        )

    with col2:
        ls_scheme = st.multiselect(
            label="Scheme",
            options=LS_SCHEME,
            key="overlap_flaglist_scheme",
            default="UFLS",
        )
        selected_ls_scheme = LS_SCHEME if ls_scheme == [] else ls_scheme

    with col3:
        ls_stage_options = ufls_setting.columns.tolist()
        if len(selected_ls_scheme) == 1 and selected_ls_scheme[0] == "UVLS":
            ls_stage_options = uvls_setting.columns.tolist()

        stage_selected = st.multiselect(
            label="Operating Stage",
            options=ls_stage_options,
            key="overlap_flaglist_stage",
        )

    with col4:
        zone = sorted(set(zone_mapping.values()))
        zone_selected = st.multiselect(
            label="Regional Zone",
            options=zone,
            key="overlap_flaglist_zone",
        )

    with col5:
        subzone = column_data_list(
            subs_metadata,
            "gm_subzone",
        )
        subzone_selected = st.multiselect(
            label="GM Subzone",
            options=subzone,
            key="overlap_flaglist_subzone",
        )

    with col6:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="overlap_flaglist_search_box",
        )

    filters = {
        "review_year": review_year,
        "scheme": selected_ls_scheme,
        "op_stage": stage_selected,
        "zone": zone_selected,
        "gm_subzone": subzone_selected,
    }

    masterlist_ls = loadshedding.ls_assignment_masterlist()
    overlap_list = masterlist_ls.loc[
        (masterlist_ls["critical_list"] == "dn")
        | (masterlist_ls["critical_list"] == "gso")
    ]

    filtered_data = loadshedding.filtered_data(
        filters=filters, df=overlap_list)

    if not filtered_data.empty:
        selected_inp_scheme = [
            f"{scheme}_{review_year}" for scheme in selected_ls_scheme
        ]

        missing_scheme = set(selected_inp_scheme).difference(
            set(filtered_data.columns)
        )
        available_scheme_set = set(selected_inp_scheme).intersection(
            set(filtered_data.columns)
        )

        filtered_df = df_search_filter(filtered_data, search_query)

        ls_cols = [
            col
            for col in filtered_df.columns
            if any(keyword in col for keyword in LS_SCHEME)
        ]

        filtered_df = filtered_df.rename(
            columns={
                "substation_name": "Substation",
                "mnemonic": "Mnemonic",
                "kV": "Voltage Level",
                "short_text": "Remark"
            }
        )

        other_cols = ["Substation", "Mnemonic",
                      "Voltage Level", "Remark", "assignment_id"]
        columns_order = ls_cols + other_cols

        sorted_df = scheme_col_sorted(filtered_df, available_scheme_set)

        df_final_display = sorted_df.reindex(columns=columns_order)

        ### table ##################
        show_overlap_list = st.checkbox(
            "**Show List of Overlap Critical Load List Table**", value=False)

        if show_overlap_list:
            st.markdown(
                f'<span style="color: inherit; font-size: 20px; font-weight: 600"> List of Overlap Critical Load List:</span>',
                unsafe_allow_html=True
            )
            st.dataframe(
                df_final_display, width="stretch", hide_index=True
            )

        ### dashbaord ##################
        data = {
            "review_year": review_year,
            "selected_ls_scheme": selected_ls_scheme,
            "overlap_list": overlap_list,
            "masterlist_ls": masterlist_ls
        }

        critical_list_dashboard(data)

        if missing_scheme:
            for scheme in missing_scheme:
                st.info(
                    f"No active load shedding {scheme} assignment found for the selected filters."
                )
    else:
        st.info(
            "No active load shedding assignment found for the selected filters."
        )
