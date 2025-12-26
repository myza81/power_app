import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any
from datetime import date
from applications.data_processing.read_data import df_search_filter
from applications.load_shedding.helper import columns_list
from applications.load_shedding.load_profile import (
    load_profile_metric,
)
from pages.load_shedding.helper import display_ls_metrics


def simulator():
    # 1. State Initialization
    load_obj = st.session_state.get("loadprofile")
    total_mw = load_obj.totalMW()

    ls_obj = st.session_state.get("loadshedding")
    masterlist = ls_obj.ls_assignment_masterlist
    


    ufls_setting = ls_obj.ufls_setting
    uvls_setting = ls_obj.uvls_setting

    TARGET_UFLS = 0.5
    TARGET_UVLS = 0.2
    TARGET_EMLS = 0.3




    # loadprofile = st.session_state["loadprofile"]
    # total_mw = loadprofile.totalMW()
    # north_mw = loadprofile.regional_loadprofile("North")
    # kvalley_mw = loadprofile.regional_loadprofile("KlangValley")
    # south_mw = loadprofile.regional_loadprofile("South")
    # east_mw = loadprofile.regional_loadprofile("East")

    # loadshedding = st.session_state["loadshedding"]
    
    

    # ########## debugging info ##########

    # # st.dataframe(loadshedding.loadshedding_assignments())
    # # st.dataframe(loadshedding.dp_grpId_loadquantum())
    # # st.divider()

    # ########## debugging info ##########

    # ## section 1: Load Quantum Target Metrics ##
    # st.subheader("Load Quantum Target Metrics")

    # ## sub-section 1: Review Year Input ##
    # tab2_s1_col1, tab2_s1_col2 = st.columns(2)

    # with tab2_s1_col1:
    #     current_year = date.today().year
    #     review_year = st.number_input(
    #         label="Review Year",
    #         min_value=current_year,
    #         max_value=current_year + 10,
    #         value=current_year,
    #         step=1,
    #         format="%d",
    #         key="review_year_ls_reviewer",
    #     )

    # with tab2_s1_col2:
    #     ls_scheme = st.selectbox(
    #         label="Scheme", options=["UFLS", "UVLS", "EMLS"], index=0
    #     )

    # ######################################
    # ## sub-section 2: Review Year Input ##
    # ######################################

    # tab2_s2_col1, tab2_s2_col2, tab2_s2_col3 = st.columns([2.5, 4, 4])

    # target = (
    #     TARGET_UFLS
    #     if ls_scheme == "UFLS"
    #     else TARGET_UVLS if ls_scheme == "UVLS" else TARGET_EMLS
    # )

    # with tab2_s2_col1:
    #     st.metric(
    #         f"Total Latest MD: {total_mw:,} MW",
    #         f"Target {ls_scheme}: {int(target*total_mw):,} MW ({int((target*total_mw/total_mw)*100)}%)",
    #     )

    # with tab2_s2_col2:
    #     colf2_1, colf2_2 = st.columns(2)
    #     with colf2_1:
    #         st.metric(
    #             label=f"North: {north_mw:,} MW",
    #             value=f"Target: {int(target*north_mw):,} MW ({int((target*north_mw/north_mw)*100)}%)",
    #         )
    #         st.metric(
    #             label=f"Klang Valley: {kvalley_mw:,} MW",
    #             value=f"Target: {int(target*kvalley_mw):,} MW ({int((target*kvalley_mw/kvalley_mw)*100)}%)",
    #         )

    #     with colf2_2:
    #         st.metric(
    #             label=f"South: {south_mw:,} MW",
    #             value=f"Target: {int(target*south_mw):,} MW ({int((target*south_mw/south_mw)*100)}%)",
    #         )
    #         st.metric(
    #             label=f"East: {east_mw:,} MW",
    #             value=f"Target: {int(target*east_mw):,} MW ({int((target*east_mw/east_mw)*100)}%)",
    #         )

    # with tab2_s2_col3:
    #     pass
    # st.divider()

    # #############################################################
    # ## sub-section 3: Available Load Shedding Quantum Capacity ##
    # #############################################################
    # available_assignment = loadshedding.automatic_loadshedding_rly()
    # remove_duplicate = available_assignment.drop_duplicates(
    #     subset=["local_trip_id", "mnemonic", "feeder_id"], keep="first"
    # )

    # st.subheader("Available Load Shedding Quantum Capacity")

    # show_table = st.checkbox(
    #     "**Show Available Load Shedding Quantum Capacity Data**", value=False
    # )

    # if show_table:

    #     avail_quantum_mw = remove_duplicate["Pload (MW)"].sum()
    #     north_avail_MW = load_profile_metric(remove_duplicate, "North")
    #     kValley_avail_MW = load_profile_metric(remove_duplicate, "KlangValley")
    #     south_avail_MW = load_profile_metric(remove_duplicate, "South")
    #     east_avail_MW = load_profile_metric(remove_duplicate, "East")

    #     tab2_s3_col1, tab2_s3_col2, tab2_s3_col3 = st.columns([2.5, 2.5, 4])

    #     with tab2_s3_col1:
    #         st.metric(
    #             label=f"Available Potential Quantum: ",
    #             value=f"{int(avail_quantum_mw):,} MW ({int((avail_quantum_mw/total_mw)*100)}%)",
    #         )

    #     with tab2_s3_col2:
    #         col_s3_1, col_s3_2 = st.columns(2)
    #         with col_s3_1:
    #             st.metric(
    #                 label=f"North: ",
    #                 value=f"{int(north_avail_MW):,} MW ({int((north_avail_MW/north_mw)*100)}%)",
    #             )
    #             st.metric(
    #                 label=f"Klang Valley: ",
    #                 value=f"{int(kValley_avail_MW):,} MW ({int((kValley_avail_MW/kvalley_mw)*100)}%)",
    #             )

    #         with col_s3_2:
    #             st.metric(
    #                 label=f"South: ",
    #                 value=f"{int(south_avail_MW):,} MW ({int((south_avail_MW/south_mw)*100)}%)",
    #             )
    #             st.metric(
    #                 label=f"East: ",
    #                 value=f"{int(east_avail_MW):,} MW ({int((east_avail_MW/east_mw)*100)}%)",
    #             )

    #     with tab2_s3_col3:
    #         pass

    #     #### filter options
    #     col2_s3_col1, col2_s3_col2, col2_s3_col3 = st.columns(3)

    #     with col2_s3_col1:
    #         zone = list(set(zone_mapping.values()))
    #         zone_selected = st.multiselect(
    #             label="Zone Location", 
    #             options=zone, 
    #             key="avail_loadshed_zone"
    #         )
    #     with col2_s3_col2:
    #         search_query = st.text_input(
    #             label="Search for a Keyword:",
    #             placeholder="Enter your search keyword here...",
    #             key="avail_loadshed_search_box",
    #         )

    #     filters = {
    #         # "review_year": review_year,
    #         # "scheme": selected_ls_scheme,
    #         # "op_stage": stage_selected,
    #         "zone": zone_selected,
    #         # "gm_subzone": subzone_selected,
    #         # "ls_dp": trip_assignment,
    #     }

    #     filtered_data = loadshedding.filtered_data(
    #         filters=filters, df=available_assignment
    #     )

    #     st.dataframe(filtered_data)

    # st.divider()

    # #############################################################
    # ## sub-section 4: Available Load Shedding Quantum Capacity ##
    # #############################################################
    # st.subheader("Simulator")

    # ls_assignment_masterlist = loadshedding.ls_assignment_masterlist()

    # tab2_s4_col1, tab2_s4_col2, tab2_s4_col3 = st.columns([2.5, 2.5, 4])

    # with tab2_s4_col1:
    #     ls_cols = [
    #         col
    #         for col in ls_assignment_masterlist.columns
    #         if any(keyword in col for keyword in ["UFLS", "UVLS", "EMLS"])
    #     ]
    #     current_datetime = pd.to_datetime("now")
    #     current_year = current_datetime.year
    #     prev_year = current_year - 1
    #     target_col = f"UFLS_{prev_year}"
    #     default_selection = None

    #     if target_col in ls_cols:
    #         default_selection = target_col
    #     else:
    #         for col in ls_cols:
    #             if "UFLS" in col:
    #                 default_selection = col
    #                 break
    #     if default_selection and default_selection in ls_cols:
    #         default_index = ls_cols.index(default_selection)
    #     else:
    #         default_index = 0

    #     based_template = st.selectbox(
    #         label="Based Template",
    #         options=ls_cols,
    #         key="simulator_based_template",
    #         index=default_index,
    #     )

    #     drop_ls = [col for col in ls_cols if col != based_template]
    #     based_ls_df = ls_assignment_masterlist.drop(columns=drop_ls, axis=1).reset_index(
    #         drop=True
    #     )
    #     based_available_assignment = pd.merge(
    #         available_assignment,
    #         based_ls_df,
    #         on=[
    #             "assignment_id",
    #             "local_trip_id",
    #             "mnemonic",
    #             "feeder_id",
    #             "breaker_id",
    #             "kV",
    #             "zone",
    #             "gm_subzone",
    #             "group_trip_id",
    #             "ls_dp",
    #             "critical_list",
    #             "short_text",
    #             "long_text",
    #             "Pload (MW)",
    #             "Qload (Mvar)",
    #             "substation_name",
    #         ],
    #         how="outer",
    #     )
    #     assignment_df = based_available_assignment[
    #         [
    #             "assignment_id",
    #             "local_trip_id",
    #             "Pload (MW)",
    #             based_template,
    #             "critical_list",
    #             "zone",
    #         ]
    #     ]
    #     grp_df = assignment_df.groupby(
    #         ["assignment_id", based_template], as_index=False
    #     ).agg(
    #         {
    #             "Pload (MW)": "sum",
    #             "local_trip_id": lambda x: ", ".join(x.astype(str).unique()),
    #             "critical_list": lambda x: ", ".join(x.astype(str).unique()),
    #             "zone": lambda x: ", ".join(x.astype(str).unique()),
    #         }
    #     )

    # st.dataframe(grp_df)
