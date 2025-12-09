import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Any

from applications.load_shedding.data_processing.helper import columns_list
from applications.load_shedding.data_processing.load_profile import (
    df_search_filter,
)
from pages.load_shedding.helper import display_ls_metrics


def column_data_list(
    df: Optional[pd.DataFrame],
    column_name: str,
    unwanted_el: Optional[Sequence[Any]] = None,
    add_el: Optional[Sequence[dict]] = None,
) -> List[Any]:

    if df is None or column_name not in df.columns:
        return []

    values = df[column_name].tolist()
    unique_ordered = list(dict.fromkeys(values))

    if unwanted_el:
        unique_ordered = [v for v in unique_ordered if v not in unwanted_el]

    if add_el:
        for el in add_el:
            idx = el.get("idx", 0)
            data = el.get("data")
            idx = max(0, min(idx, len(unique_ordered)))
            unique_ordered.insert(idx, data)

    return unique_ordered


def ls_data_viewer() -> None:
    load_profile_df = st.session_state["load_profile"] 
    loadshedding = st.session_state["loadshedding"]

    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    subs_metadata = loadshedding.subs_metadata_enrichment()
    zone_mapping = loadshedding.zone_mapping
    loadshedding_dp = loadshedding.merged_dp()

    st.subheader("Active Load Sheddding Assignment")

    ########## debugging info ##########

    # st.dataframe(loadshedding.merged_dp_with_flaglist())
    # st.dataframe(loadshedding.loadshedding_assignments())
    # st.divider()

    ########## debugging info ##########

    show_table = st.checkbox("**Show Active Load Shedding Assignment List**", value=False)

    if show_table:
        col1_1, col1_2, col1_3 = st.columns(3)
        col2_1, col2_2, col2_3 = st.columns(3)

        with col1_1:
            review_year_list = columns_list(ufls_assignment, unwanted_el=["assignment_id"])
            review_year_list.sort(reverse=True)
            review_year = st.selectbox(label="Review Year", options=review_year_list)

        with col1_2:
            ls_scheme = st.multiselect(label="Scheme", options=["UFLS", "UVLS", "EMLS"], default="UFLS")

        with col1_3:
            zone = list(set(zone_mapping.values()))
            zone_selected = st.multiselect(label="Zone Location", options=zone)

        with col2_1:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(label="GM Subzone", options=subzone)

        with col2_2:
            ls_stage_options = ufls_setting.columns.tolist()
            if len(ls_scheme) == 1 and ls_scheme[0] == "UVLS":
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
            "scheme": ls_scheme,
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
            search_query = st.text_input(
                    label="Search for a Keyword:",
                    placeholder="Enter your search keyword here...", 
                    key="active_ls_search_box",
                )
            filtered_df = df_search_filter(filtered_data, search_query)
            ls_cols = [col for col in filtered_df.columns if any(
                keyword in col for keyword in ["UFLS", "UVLS", "EMLS"])]
            other_cols = ["zone", "gm_subzone", "substation_name", "mnemonic", "kV", "breaker_id", "ls_dp", "assignment_id", "Pload (MW)"]
            insertion_point = other_cols.index("kV") + 1
            col_seq = other_cols[:insertion_point] + ls_cols + other_cols[insertion_point:]

            st.dataframe(
                filtered_df, column_order=col_seq, width="stretch", hide_index=True
            )

            SCHEME_COLUMNS = ls_cols
            for scheme in SCHEME_COLUMNS:
                if scheme in filtered_data.columns:
                    display_ls_metrics(
                        scheme=scheme, 
                        df=filtered_data, 
                        load_profile = load_profile_df
                    )               
        else:
            st.info("No active load shedding assignment found for the selected filters.")
