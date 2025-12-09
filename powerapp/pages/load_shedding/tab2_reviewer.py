import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any
from datetime import date

from applications.load_shedding.data_processing.helper import columns_list
from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric,
    df_search_filter,
)
from pages.load_shedding.helper import display_ls_metrics


def ls_reviewer():
    load_profile_df = st.session_state["load_profile"]
    total_mw = load_profile_df["Pload (MW)"].sum()
    north_MW = load_profile_metric(load_profile_df, "North")
    kValley_MW = load_profile_metric(load_profile_df, "KlangValley")
    south_MW = load_profile_metric(load_profile_df, "South")
    east_MW = load_profile_metric(load_profile_df, "East")

    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting

    TARGET_UFLS = 0.5
    TARGET_UVLS = 0.2
    TARGET_EMLS = 0.3

    ########## debugging info ##########

    # st.dataframe(loadshedding.loadshedding_assignments())
    # st.dataframe(loadshedding.dp_grpId_loadquantum())
    # st.divider()

    ########## debugging info ##########

    ## section 1: Load Quantum Target Metrics ##
    st.subheader("Load Quantum Target Metrics")

    ## sub-section 1: Review Year Input ##
    tab2_s1_col1, tab2_s1_col2 = st.columns(2)

    with tab2_s1_col1:
        current_year = date.today().year
        review_year = st.number_input(
            label="Review Year",
            min_value=current_year,
            max_value=current_year + 10,
            value=current_year,
            step=1,
            format="%d",
            key="review_year_ls_reviewer",
        )

    with tab2_s1_col2:
        ls_scheme = st.selectbox(label="Scheme", options=[
                                 "UFLS", "UVLS", "EMLS"], index=0)

    ## sub-section 2: Review Year Input ##
    tab2_s2_col1, tab2_s2_col2, tab2_s2_col3 = st.columns([2.5, 4, 4])

    target = TARGET_UFLS if ls_scheme == "UFLS" else TARGET_UVLS if ls_scheme == "UVLS" else TARGET_EMLS

    with tab2_s2_col1:
        st.metric(
            f"Total Latest MD: {int(total_mw):,} MW",
            f"Target {ls_scheme}: {int(target*total_mw):,} MW ({int((target*total_mw/total_mw)*100)}%)",
        )

    with tab2_s2_col2:
        colf2_1, colf2_2 = st.columns(2)
        with colf2_1:
            st.metric(
                label=f"North: {int(north_MW):,} MW",
                value=f"Target: {int(target*north_MW):,} MW ({int((target*north_MW/north_MW)*100)}%)",
            )
            st.metric(
                label=f"Klang Valley: {int(kValley_MW):,} MW",
                value=f"Target: {int(target*kValley_MW):,} MW ({int((target*kValley_MW/kValley_MW)*100)}%)",
            )

        with colf2_2:
            st.metric(
                label=f"South: {int(south_MW):,} MW",
                value=f"Target: {int(target*south_MW):,} MW ({int((target*south_MW/south_MW)*100)}%)",
            )
            st.metric(
                label=f"East: {int(east_MW):,} MW",
                value=f"Target: {int(target*east_MW):,} MW ({int((target*east_MW/east_MW)*100)}%)",
            )

    with tab2_s2_col3:
        pass
    st.divider()

    ## sub-section 3: Available Load Shedding Quantum Capacity ##
    st.subheader("Available Load Shedding Quantum Capacity")

    show_table = st.checkbox("**Show Available Load Shedding Quantum Capacity Data**", value=False)

    if show_table:
        available_assignment = loadshedding.automatic_loadshedding_rly()
        remove_duplicate = available_assignment.drop_duplicates(
            subset=['local_trip_id', 'mnemonic', 'feeder_id'], keep='first')

        # df_id_duplicates = available_assignment[available_assignment.duplicated(subset=['local_trip_id', 'mnemonic', 'feeder_id'], keep=False)]
        # st.dataframe(df_id_duplicates)

        avail_qunatum_mw = remove_duplicate["Pload (MW)"].sum()

        north_avail_MW = load_profile_metric(remove_duplicate, "North")
        kValley_avail_MW = load_profile_metric(remove_duplicate, "KlangValley")
        south_avail_MW = load_profile_metric(remove_duplicate, "South")
        east_avail_MW = load_profile_metric(remove_duplicate, "East")

        tab2_s3_col1, tab2_s3_col2, tab2_s3_col3 = st.columns([2.5, 4, 4])

        with tab2_s3_col1:
            st.metric(
                label=f"Available Potential Quantum: ",
                value=f"{int(avail_qunatum_mw):,} MW ({int((avail_qunatum_mw/total_mw)*100)}%)",
            )

        with tab2_s3_col2:
            col_s3_1, col_s3_2 = st.columns(2)
            with col_s3_1:
                st.metric(
                    label=f"North: ",
                    value=f"{int(north_avail_MW):,} MW ({int((north_avail_MW/north_MW)*100)}%)",
                )
                st.metric(
                    label=f"Klang Valley: ",
                    value=f"{int(kValley_avail_MW):,} MW ({int((kValley_avail_MW/kValley_MW)*100)}%)",
                )

            with col_s3_2:
                st.metric(
                    label=f"South: ",
                    value=f"{int(south_avail_MW):,} MW ({int((south_avail_MW/south_MW)*100)}%)",
                )
                st.metric(
                    label=f"East: ",
                    value=f"{int(east_avail_MW):,} MW ({int((east_avail_MW/east_MW)*100)}%)",
                )

        with tab2_s3_col3:
            pass

        st.divider()
