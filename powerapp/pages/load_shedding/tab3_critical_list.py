import pandas as pd
import streamlit as st
from applications.load_shedding.data_processing.load_profile import (
    df_search_filter,
)
from applications.load_shedding.data_processing.helper import columns_list


def critical_list():
    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    zone_mapping = loadshedding.zone_mapping

    ########## debugging info ##########

    # st.dataframe(loadshedding.ls_assignment_masterlist())
    # st.dataframe(loadshedding.flaglist_ls_assignment_mapping())
    # st.divider()

    ########## debugging info ##########

    ## sub-section 1: Overlap Critical Load List ##
    st.subheader(
        "Overlap Critical Load List with Existing Load Shedding Scheme")
    
    filters, search_query = flaglist_filter_section(
        ufls_assignment=ufls_assignment,
        ufls_setting=ufls_setting,
        uvls_setting=uvls_setting,
        zone_mapping=zone_mapping,
        key_prefix="overlap_flaglist"
    )

    masterlist_ls = loadshedding.ls_assignment_masterlist()
    overlap_list = masterlist_ls.loc[(masterlist_ls['critical_list'] == 'dn') | (
            masterlist_ls['critical_list'] == 'gso')]
    
    filtered_data = loadshedding.filtered_data(filters=filters, df=overlap_list)

    if not filtered_data.empty:

        filtered_df = df_search_filter(filtered_data, search_query)

        ls_cols = [col for col in filtered_df.columns if any(
        keyword in col for keyword in ["UFLS", "UVLS", "EMLS"])]
        other_cols = ['mnemonic', 'kV', "assignment_id", "short_text"]
        col_seq = ls_cols + other_cols

        st.dataframe(
            filtered_df,
            column_order=col_seq,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No active load shedding assignment found for the selected filters.")

    st.divider()
    
    ## sub-section 2: All Critical Load List ##
    st.subheader("List of Critical Load from GSO & DSO")
    show_all_warning_list = st.checkbox(
        "**Show All Critical Load (Non-overlap & Overlap)**", value=False)

    if show_all_warning_list:
        filters, search_query = flaglist_filter_section(
            ufls_assignment=ufls_assignment,
            ufls_setting=ufls_setting,
            uvls_setting=uvls_setting,
            zone_mapping=zone_mapping,
            key_prefix="flaglist"
        )
        
        dp = loadshedding.dp_grpId_loadquantum()

        flaglist = dp.loc[(dp['critical_list'] == 'dn') | (
                dp['critical_list'] == 'gso')][['mnemonic', 'kV', 'feeder_id', 'local_trip_id', 'critical_list', 'short_text', 'long_text']]
        
        remove_duplicate = flaglist.drop_duplicates(
            subset=['local_trip_id', 'mnemonic', 'feeder_id'], keep='first')
        st.write(remove_duplicate)

    #     filtered_data = loadshedding.filtered_data(filters=filters, df=remove_duplicate)

    #     if not filtered_data.empty:      
    #         if not flaglist.empty:
    #             filtered_df = df_search_filter(flaglist, search_query)
    #             # st.dataframe(
    #             #     filtered_df,
    #             #     column_order=['mnemonic', 'kV', "assignment_id", "short_text", "critical_list"],
    #             #     width="stretch",
    #             #     hide_index=True
    #             # )
    #         else:
    #             pass
    #             # st.write(overlap_list)
    #     else:
    #         st.info("No active load shedding assignment found for the selected filters.")

    #     # flag_list = loadshedding.flaglist()

    #     # filtered_df = df_search_filter(flag_list, search_query)
    #     # st.dataframe(
    #     #     filtered_df,
    #     #     column_order=["local_trip_id", "short_text", "category"],
    #     #     width="stretch"
    #     # )



def flaglist_filter_section(
    ufls_assignment,
    ufls_setting,
    uvls_setting,
    zone_mapping,
    key_prefix="overlap_flaglist",
):
    """
    Creates a reusable Streamlit filter UI for load shedding reviews.

    Parameters:
        ufls_assignment (pd.DataFrame): UFLS assignment data.
        ufls_setting (pd.DataFrame): UFLS setting table.
        uvls_setting (pd.DataFrame): UVLS setting table.
        zone_mapping (dict): Mapping of substations to zones.
        key_prefix (str): Unique prefix to avoid Streamlit widget key collisions.

    Returns:
        dict: A dictionary of all selected filter values.
    """

    # --- Layout setup ---
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # --- Column 1: Review Year ---
    with col1:
        review_year_list = ufls_assignment.columns.drop("assignment_id", errors="ignore").tolist()
        review_year_list.sort(reverse=True)
        review_year = st.selectbox(
            label="Review Year",
            options=review_year_list,
            key=f"{key_prefix}_review_year",
        )

    # --- Column 2: Scheme ---
    with col2:
        ls_scheme = st.multiselect(
            label="Scheme",
            options=["UFLS", "UVLS", "EMLS"],
            key=f"{key_prefix}_scheme",
        )

    # --- Column 3: Operating Stage ---
    with col3:
        ls_stage_options = ufls_setting.columns.tolist()
        if len(ls_scheme) == 1 and ls_scheme[0] == "UVLS":
            ls_stage_options = uvls_setting.columns.tolist()

        stage_selected = st.multiselect(
            label="Operating Stage",
            options=ls_stage_options,
            key=f"{key_prefix}_stage",
        )

    # --- Column 4: Zone ---
    with col4:
        zone = sorted(set(zone_mapping.values()))
        zone_selected = st.multiselect(
            label="Zone Location",
            options=zone,
            key=f"{key_prefix}_zone",
        )

    # --- Column 5: Search Box ---
    with col5:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key=f"{key_prefix}_search_box",
        )

    # --- Combine results ---
    filters = {
        "review_year": review_year,
        "scheme": ls_scheme,
        "UFLS": stage_selected,
        "UVLS": stage_selected,
        "EMLS": stage_selected,
        "zone": zone_selected,
    }

    return (filters, search_query)

