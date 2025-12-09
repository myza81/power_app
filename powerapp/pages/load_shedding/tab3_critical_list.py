import pandas as pd
import streamlit as st
from applications.load_shedding.data_processing.load_profile import (
    df_search_filter,
)
from applications.load_shedding.data_processing.helper import (
    columns_list, column_data_list
)


def critical_list():
    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    zone_mapping = loadshedding.zone_mapping
    subs_metadata = loadshedding.subs_metadata_enrichment()
    dp_flaglist = loadshedding.merged_dp_with_flaglist()

    #########################################################
    ##      sub-section 1: List of Critical Load          ##
    #########################################################
    st.subheader("List of Critical Load from GSO & DSO")
    show_all_warning_list = st.checkbox(
        "**Show All Critical Load (Non-overlap & Overlap)**", value=False)

    if show_all_warning_list:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # --- Column 1: Review Year ---
        with col1:
            zone = sorted(set(zone_mapping.values()))
            zone_selected = st.multiselect(
                label="Zone Location",
                options=zone,
                key="flaglist_zone",
            )

        # --- Column 2: Scheme ---
        with col2:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(
                label="GM Subzone",
                options=subzone,
                key="flaglist_subzone",
            )

        # --- Column 3: critical_list ---
        with col3:
            critical_list = list(set(dp_flaglist["critical_list"]))
            selected_critical_list = st.multiselect(
                label="Critical List by",
                options=critical_list,
                key="flaglist_critical_list",
            )

        # --- Column 4: ls_dp ---
        with col4:
            ls_dp = list(set(dp_flaglist["ls_dp"]))
            trip_assignment = st.multiselect(
                label="Tripping Assignment",
                options=ls_dp,
                key="flaglist_ls_dp",
            )

        # --- Column 5: Search Box ---
        with col5:
            search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search keyword here...",
                key="flaglist_search_box",
            )

        filters = {
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
            "critical_list": selected_critical_list,
            "ls_dp": trip_assignment,
        }

        dp = loadshedding.dp_grpId_loadquantum()

        flaglist = dp.loc[(dp['critical_list'] == 'dn') | (
                dp['critical_list'] == 'gso')]

        if not flaglist.empty:
            remove_duplicate = flaglist.drop_duplicates(
            subset=['local_trip_id', 'mnemonic', 'feeder_id'], keep='first')

            filtered_data = loadshedding.filtered_data(filters=filters, df=remove_duplicate)

            if not filtered_data.empty:      

                filtered_df = df_search_filter(filtered_data, search_query)
                st.dataframe(
                        filtered_df,
                        column_order=['mnemonic', 'kV', "assignment_id", "short_text", "critical_list"],
                        width="stretch",
                        hide_index=True
                    )
            else:
                st.info("No active load shedding assignment found for the selected filters.")

        else:
            st.info("No active load shedding assignment found for the selected filters.")
        
        st.write(len(remove_duplicate))

    st.divider()
        
    #########################################################
    ##      sub-section 2: Overlap Critical Load List       ##
    #########################################################
    st.subheader(
        "Overlap Critical Load List with Existing Load Shedding Scheme")
    
    show_overlap_list = st.checkbox(
        "**Show Overlap Critical Load List**", value=False)
    
    if show_overlap_list:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # --- Column 1: Review Year ---
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

        # --- Column 2: Scheme ---
        with col2:
            ls_scheme = st.multiselect(
                label="Scheme",
                options=["UFLS", "UVLS", "EMLS"],
                key="overlap_flaglist_scheme",
            )

        # --- Column 3: Operating Stage ---
        with col3:
            ls_stage_options = ufls_setting.columns.tolist()
            if len(ls_scheme) == 1 and ls_scheme[0] == "UVLS":
                ls_stage_options = uvls_setting.columns.tolist()

            stage_selected = st.multiselect(
                label="Operating Stage",
                options=ls_stage_options,
                key="overlap_flaglist_stage",
            )

        # --- Column 4: Zone ---
        with col4:
            zone = sorted(set(zone_mapping.values()))
            zone_selected = st.multiselect(
                label="Zone Location",
                options=zone,
                key="overlap_flaglist_zone",
            )

        # --- Column 5: Search Box ---
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
            "scheme": ls_scheme,
            "op_stage": stage_selected,
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
        }

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

    

    
    


# def flaglist_filter_section(
#     ufls_assignment,
#     ufls_setting,
#     uvls_setting,
#     zone_mapping,
#     filter_keys,
#     key_prefix="overlap_flaglist",
# ):
#     """
#     Creates a reusable Streamlit filter UI for load shedding reviews.

#     Parameters:
#         ufls_assignment (pd.DataFrame): UFLS assignment data.
#         ufls_setting (pd.DataFrame): UFLS setting table.
#         uvls_setting (pd.DataFrame): UVLS setting table.
#         zone_mapping (dict): Mapping of substations to zones.
#         key_prefix (str): Unique prefix to avoid Streamlit widget key collisions.

#     Returns:
#         dict: A dictionary of all selected filter values.
#     """
#     COLS_PER_ROW = 3
#     num_keys = len(filter_keys)

#     for i in range(0, num_keys, COLS_PER_ROW):
#         current_keys = filter_keys[i : i + COLS_PER_ROW]
#         cols = st.columns(len(current_keys))

#         for j, key in enumerate(current_keys):
#             with cols[j]:
#                 st.text(f"Filter for: {key}")

#     def year_review():
#         review_year_list = ufls_assignment.columns.drop(
#             "assignment_id", errors="ignore"
#         ).tolist()
#         review_year_list.sort(reverse=True)
#         review_year = st.selectbox(
#             label="Review Year",
#             options=review_year_list,
#             key=f"{key_prefix}_review_year",
#         )
#         return review_year

#     filter_opt = {
#         "year_review": year_review(),
#     }

#     # --- Layout setup ---
#     col1, col2, col3 = st.columns(3)
#     col4, col5, col6 = st.columns(3)

#     # --- Column 1: Review Year ---
#     with col1:
#         review_year_list = ufls_assignment.columns.drop("assignment_id", errors="ignore").tolist()
#         review_year_list.sort(reverse=True)
#         review_year = st.selectbox(
#             label="Review Year",
#             options=review_year_list,
#             key=f"{key_prefix}_review_year",
#         )

#     # --- Column 2: Scheme ---
#     with col2:
#         ls_scheme = st.multiselect(
#             label="Scheme",
#             options=["UFLS", "UVLS", "EMLS"],
#             key=f"{key_prefix}_scheme",
#         )

#     # --- Column 3: Operating Stage ---
#     with col3:
#         ls_stage_options = ufls_setting.columns.tolist()
#         if len(ls_scheme) == 1 and ls_scheme[0] == "UVLS":
#             ls_stage_options = uvls_setting.columns.tolist()

#         stage_selected = st.multiselect(
#             label="Operating Stage",
#             options=ls_stage_options,
#             key=f"{key_prefix}_stage",
#         )

#     # --- Column 4: Zone ---
#     with col4:
#         zone = sorted(set(zone_mapping.values()))
#         zone_selected = st.multiselect(
#             label="Zone Location",
#             options=zone,
#             key=f"{key_prefix}_zone",
#         )

#     # --- Column 5: Search Box ---
#     with col5:
#         search_query = st.text_input(
#             label="Search for a Keyword:",
#             placeholder="Enter your search keyword here...",
#             key=f"{key_prefix}_search_box",
#         )

#     # --- Combine results ---
#     filters = {
#         "review_year": review_year,
#         "scheme": ls_scheme,
#         "op_stage": stage_selected,
#         "mnemonic": [],
#         "zone": zone_selected,
#     }

#     return (filters, search_query)
