import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any

from applications.load_shedding.data_processing.LoadShedding import (
    LoadShedding,
    LS_Data,
)
from applications.load_shedding.data_processing.helper import columns_list
from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric,
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
    unique_ordered = list(dict.fromkeys(values))  # ordered unique

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
    ls_data = st.session_state["ls_data"]
    ufls_assignment = ls_data.ufls_assignment
    ufls_setting = ls_data.ufls_setting
    subs_masterlist = ls_data.subs_meta

    col1_1, col1_2, col1_3 = st.columns(3)
    col2_1, col2_2, col2_3 = st.columns(3)

    with col1_1:
        review_year_list = columns_list(ufls_assignment, unwanted_el=["group_trip_id"])
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(label="UFLS Review", options=review_year_list)

    with col1_2:
        ls_scheme = st.multiselect(label="Scheme", options=["UFLS", "UVLS", "EMLS"], default="UFLS")

    with col1_3:
        zone = column_data_list(
            subs_masterlist,
            "zone",
        )
        zone_selected = st.multiselect(label="Zone Location", options=zone)

    with col2_1:
        subzone = column_data_list(
            subs_masterlist,
            "gm_subzone",
        )
        subzone_selected = st.multiselect(label="GM Subzone", options=subzone)

    with col2_2:
        ufls_staging_list = column_data_list(
            ufls_setting,
            "stage",
        )
        stage_selected = st.multiselect(
            label="Operating Stage", options=ufls_staging_list
        )

    with col2_3:
        trip_assignment = st.multiselect(
            label="Tripping Assignment",
            options=["Local Load", "Pocket Load"],
        )

    # Main logic
    if "load_profile" not in st.session_state:
        st.info("Please upload or set a load profile first.")
        return

    load_shed = LoadShedding(
        review_year=review_year,
        scheme=ls_scheme,
        load_profile=load_profile_df,
    )
    st.session_state["loadshedding"] = load_shed


    filtered_data = load_shed.filtered_data(
        filters={
            "UFLS": stage_selected,
            "UVLS": stage_selected,
            "EMLS": stage_selected,
            "mnemonic": [],
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
        }
    )

    st.subheader("Active Load Sheddding Assignment")
    if isinstance(filtered_data, pd.DataFrame):
        search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search keyword here...", 
                key="active_ls_search_box",
            )
        filtered_df = df_search_filter(filtered_data, search_query)
        st.dataframe(
            filtered_df, 
            column_order=["zone", "gm_subzone", "substation_name", "mnemonic", "kV", "UFLS", "UVLS", "EMLS", "breaker_id", "ls_dp","group_trip_id", "Pload (MW)"],
            width="stretch"
        )
        

        SCHEME_COLUMNS = ['UFLS', 'UVLS', "EMLS"]
        for scheme in SCHEME_COLUMNS:
            if scheme in filtered_data.columns:
                display_ls_metrics(
                    scheme=scheme, 
                    df=filtered_data, 
                    load_profile = load_profile_df
                )               
        
    else:
        st.write(filtered_data)

    # data viewer temp
    # data = LS_Data(load_profile=load_profile_df)
    # st.write(load_shed.mlist_load())
