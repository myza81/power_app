import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any

from applications.load_shedding.data_processing.LoadShedding import (
    LoadShedding,
    LS_Data,
)


def columns_list(
    df: Optional[pd.DataFrame],
    unwanted_el: Optional[Sequence[str]] = None,
    add_el: Optional[Sequence[Tuple[int, str]]] = None,
) -> List[str]:
    
    if df is None:
        return []

    cols = df.columns.tolist()

    if unwanted_el:
        cols = [c for c in cols if c not in unwanted_el]

    if add_el:
        for idx, name in add_el:
            idx = max(0, min(idx, len(cols)))
            cols.insert(idx, name)

    return cols


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
    # ls_data = LS_Data(load_profile=load_profile)
    ls_data = st.session_state["ls_data"]
    ufls_assignment = ls_data.ufls_assignment
    ufls_setting = ls_data.ufls_setting
    subs_masterlist = ls_data.substation_masterlist

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        ls_scheme = st.selectbox(label="Scheme", options=["UFLS", "UVLS", "EMLS"])

    with col2:
        review_year_list = columns_list(ufls_assignment, unwanted_el=["group_trip_id"])
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(label="UFLS Review", options=review_year_list)

    with col3:
        zone = column_data_list(
            subs_masterlist,
            "geo_region",
            add_el=[{"idx": 0, "data": "All"}],
        )
        zone_loc = st.selectbox(label="Zone Location", options=zone)

    with col4:
        subzone = column_data_list(
            subs_masterlist,
            "gm_subzone",
            add_el=[{"idx": 0, "data": "All"}],
        )
        gm_subzone = st.selectbox(label="GM Subzone", options=subzone)

    with col5:
        ufls_staging_list = column_data_list(
            ufls_setting,
            "stage",
            add_el=[{"idx": 0, "data": "All"}],
        )
        stage = st.selectbox(label="Operating Stage", options=ufls_staging_list)

    with col6:
        trip_assignment = st.selectbox(
            label="Tripping Assignment",
            options=["All", "Local Load", "Pocket Load"],
        )

    # Main logic
    if "load_profile" not in st.session_state:
        st.info("Please upload or set a load profile first.")
        return

    load_shed = LoadShedding(
        review_year=review_year,
        load_profile=st.session_state["load_profile"],
        scheme=ls_scheme,
    )

    st.subheader("Active LS Assignment")
    st.write(load_shed.ls_active())
