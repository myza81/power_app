import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Any

from applications.load_shedding.data_processing.LoadShedding import (
    LoadShedding,
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

def display_load_profile():
    
    show_table = st.checkbox("**Show Load Profile Data**", value=False)
    
    if show_table:
        load_profile_df = st.session_state["load_profile"] 
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

def ls_data_viewer() -> None:
    load_profile_df = st.session_state["load_profile"] 
    ls_data = st.session_state["ls_data"]
    ufls_assignment = ls_data.ufls_assignment
    ufls_setting = ls_data.ufls_setting
    subs_masterlist = ls_data.subs_meta
    zone_mapping = ls_data.zone_mapping

    col1_1, col1_2, col1_3 = st.columns(3)
    col2_1, col2_2, col2_3 = st.columns(3)

    with col1_1:
        review_year_list = columns_list(ufls_assignment, unwanted_el=["group_trip_id"])
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(label="UFLS Review", options=review_year_list)

    with col1_2:
        ls_scheme = st.multiselect(label="Scheme", options=["UFLS", "UVLS", "EMLS"], default="UFLS")

    with col1_3:
        zone = list(set(zone_mapping.values()))
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
