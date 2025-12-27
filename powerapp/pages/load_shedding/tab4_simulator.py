import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any
from datetime import date
from applications.data_processing.read_data import df_search_filter
from applications.load_shedding.helper import columns_list
from applications.load_shedding.load_profile import (
    load_profile_metric,
)
from pages.load_shedding.helper import display_ls_metrics, join_unique_non_empty


def simulator():
    load_shed_assignment()


def load_shed_assignment():
    # 1. Initialize Objects
    ls_obj = st.session_state.get("loadshedding")
    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    # 2. Get available years for the selectbox
    raw_master = ls_obj.ls_assignment_masterlist()
    all_scheme = [
        col
        for col in raw_master.columns
        if any(k in col for k in ls_obj.LOADSHED_SCHEME)
    ]
    review_list = [col for col in all_scheme if not col.startswith("EMLS")]

    if not review_list:
        st.error("No valid review years found.")
        return

    # 3. UI Controls
    st.subheader("Load Shedding Assignment Simulator")
    c1, c2 = st.columns(2)

    with c1:
        review_year = st.selectbox(
            "Base Reference", options=review_list, key="sel_review_year"
        )

    # 4. RESET LOGIC - FIXED: Use a separate key to track initialization
    reset_key = f"sim_initialized_{review_year}"

    if reset_key not in st.session_state:
        # Fresh Data Pull
        masterlist = ls_obj.ls_assignment_masterlist()
        incomer_relay = ls_obj.incomer_relay()
        unique_schemes = ls_obj.pocket_relay()[
            ["assignment_id", "scheme"]
        ].drop_duplicates(subset=["assignment_id"])

        # Create combined candidate list
        valid_candidate = (
            pd.merge(masterlist, unique_schemes, on="assignment_id", how="left")
            .pipe(
                lambda df: pd.concat([df, incomer_relay], ignore_index=True, sort=False)
            )
            .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
            .query("scheme != 'emls'")
        )

        # Build Master Simulation Dataframe
        sim_df = valid_candidate.copy().rename(
            columns={
                "zone": "Zone",
                "assignment_id": "Assignment",
                "critical_list": "Flag",
            }
        )

        # Apply flag logic
        sim_df["Flag"] = sim_df["Flag"].mask(
            sim_df["Flag"].notna(), "Critical Delivery Point"
        )

        # Check if review_year exists in columns
        if review_year not in sim_df.columns:
            st.error(f"Column '{review_year}' not found in data.")
            return

        # Initial sync
        sim_df["Simulator Operating Stage"] = sim_df[review_year]

        # Save with a unique key for this year
        st.session_state[f"master_sim_df_{review_year}"] = sim_df
        st.session_state[reset_key] = True
        st.session_state["current_review_year"] = review_year
        st.rerun()  # Rerun to ensure session state is properly set

    # 5. Get the correct master DataFrame for current year
    master_key = f"master_sim_df_{review_year}"
    if master_key not in st.session_state:
        st.error("Simulation data not properly initialized.")
        return

    master_sim_df = st.session_state[master_key]

    # Zone Filter
    with c2:
        zone_options = sorted(master_sim_df["Zone"].dropna().unique())
        selected_zones = st.multiselect(
            "Filter by Zone", options=zone_options, key=f"zone_filter_{review_year}"
        )

    # 6. PREPARE VIEW - preserve original index
    view_df = master_sim_df.copy()

    if selected_zones:
        # Store original indices before filtering
        view_df = view_df[view_df["Zone"].isin(selected_zones)].copy()
        view_df["_original_index"] = view_df.index  # Store for reference

    # 7. Configure Dropdown Options
    ls_stage = {
        "UFLS": ls_obj.ufls_setting.columns.tolist(),
        "UVLS": ls_obj.uvls_setting.columns.tolist(),
    }

    # Safer prefix extraction
    year_prefix = ""
    if isinstance(review_year, str) and len(review_year) >= 4:
        year_prefix = review_year[:4]

    current_options = ls_stage.get(year_prefix, [])

    # Ensure review_year column exists
    if review_year not in view_df.columns:
        st.error(f"Column '{review_year}' not found in view data.")
        return

    # 8. DATA EDITOR
    editor_key = f"assignment_simulator_{review_year}"
    
    if review_year:
        edited_df = st.data_editor(
            view_df[
                ["Zone", "Assignment", review_year, "Simulator Operating Stage", "Flag"]
            ],
            key=editor_key,
            on_change=lambda: handle_simulator_change(review_year),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Simulator Operating Stage": st.column_config.SelectboxColumn(
                    "Simulator Operating Stage",
                    options=current_options,
                    help="Select the operating stage for this assignment",
                    width="medium",
                    required=True,
                ),
                "Zone": st.column_config.Column(disabled=True),
                "Assignment": st.column_config.Column(disabled=True),
                review_year: st.column_config.Column("Original Reference", disabled=True),
                "Flag": st.column_config.Column(disabled=True),
            },
        )

    # 9. Update master data if changes were made
    if editor_key in st.session_state:
        # Get the edited data from session state
        editor_state = st.session_state[editor_key]

        if "edited_rows" in editor_state or "added_rows" in editor_state:
            # Update the master DataFrame with changes
            update_master_from_editor(master_sim_df, editor_state, review_year)


# Define the callback function
def handle_simulator_change(review_year):
    """Handle changes to the simulator editor"""
    editor_key = f"assignment_simulator_{review_year}"
    master_key = f"master_sim_df_{review_year}"

    if editor_key in st.session_state and master_key in st.session_state:
        editor_state = st.session_state[editor_key]
        master_df = st.session_state[master_key].copy()

        # Apply changes from editor to master
        if "edited_rows" in editor_state:
            for idx, changes in editor_state["edited_rows"].items():
                if idx < len(master_df):
                    for col, value in changes.items():
                        master_df.at[idx, col] = value

        # Update session state
        st.session_state[master_key] = master_df


# Helper function to update master data
def update_master_from_editor(master_df, editor_state, review_year):
    """Update master dataframe with editor changes"""
    # Implementation depends on your specific update logic
    pass


# def load_shed_assignment():
#     # 1. Initialize Objects
#     ls_obj = st.session_state.get("loadshedding")
#     if not ls_obj:
#         st.error("Load shedding data not found in session state.")
#         return

#     # 2. Get available years for the selectbox (raw data check)
#     raw_master = ls_obj.ls_assignment_masterlist()
#     all_scheme = [
#         col
#         for col in raw_master.columns
#         if any(k in col for k in ls_obj.LOADSHED_SCHEME)
#     ]
#     review_list = [col for col in all_scheme if not col.startswith("EMLS")]

#     # 3. UI Controls
#     st.subheader("Load Shedding Assignment Simulator")
#     c1, c2 = st.columns(2)

#     with c1:
#         # Trigger for resetting data
#         review_year = st.selectbox(
#             "Base Reference", options=review_list, key="sel_review_year"
#         )

#     # 4. RESET LOGIC: Rebuild master data if year changes
#     if (
#         "current_sim_year" not in st.session_state
#         or st.session_state["current_sim_year"] != review_year
#     ):
#         st.session_state["current_sim_year"] = review_year

#         # Fresh Data Pull
#         masterlist = ls_obj.ls_assignment_masterlist()
#         incomer_relay = ls_obj.incomer_relay()
#         unique_schemes = ls_obj.pocket_relay()[
#             ["assignment_id", "scheme"]
#         ].drop_duplicates(subset=["assignment_id"])

#         # Create combined candidate list
#         valid_candidate = (
#             pd.merge(masterlist, unique_schemes, on="assignment_id", how="left")
#             .pipe(
#                 lambda df: pd.concat([df, incomer_relay], ignore_index=True, sort=False)
#             )
#             .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
#             .query("scheme != 'emls'")
#         )

#         # Build Master Simulation Dataframe
#         sim_df = valid_candidate.copy().rename(
#             columns={
#                 "zone": "Zone",
#                 "assignment_id": "Assignment",
#                 "critical_list": "Flag",
#             }
#         )
#         # Apply your logic: Flag cells that aren't empty
#         sim_df["Flag"] = sim_df["Flag"].mask(
#             sim_df["Flag"].notna(), "Critical Delivery Point"
#         )

#         # Initial sync of the editable column with the selected year
#         sim_df["Simulator Operating Stage"] = sim_df[review_year]

#         # SAVE TO SESSION STATE (This is our persistent Source of Truth)
#         st.session_state["master_sim_df"] = sim_df

#     # 5. Zone Filter
#     with c2:
#         zone_options = sorted(
#             st.session_state["master_sim_df"]["Zone"].dropna().unique()
#         )
#         selected_zones = st.multiselect("Filter by Zone", options=zone_options)

#     # 6. PREPARE VIEW (Filtering rows but PRESERVING index)
#     # Important: Do NOT use reset_index() here
#     view_df = st.session_state["master_sim_df"].copy()

#     if selected_zones:
#         view_df = view_df[view_df["Zone"].isin(selected_zones)]

#     # 7. Configure Dropdown Options for the Editor
#     ls_stage = {
#         "UFLS": ls_obj.ufls_setting.columns.tolist(),
#         "UVLS": ls_obj.uvls_setting.columns.tolist(),
#     }


#     current_options = ls_stage.get(review_year[:4], [])

#     # 8. DATA EDITOR
#     st.data_editor(
#         # Pass only the necessary columns for the view
#         view_df[
#             ["Zone", "Assignment", review_year, "Simulator Operating Stage", "Flag"]
#         ],
#         key="assignment_simulator_key",
#         on_change=handle_simulator_change,
#         hide_index=True,
#         use_container_width=True,
#         column_config={
#             "Simulator Operating Stage": st.column_config.SelectboxColumn(
#                 "Simulator Operating Stage",
#                 options=current_options,
#                 help="Select the operating stage for this assignment",
#                 width="medium",
#             ),
#             "Zone": st.column_config.Column(disabled=True),
#             "Assignment": st.column_config.Column(disabled=True),
#             review_year: st.column_config.Column("Original Reference", disabled=True),
#             "Flag": st.column_config.Column(disabled=True),
#         },
#     )

#     # Optional: Debug view to see the master data updating in real-time
#     # st.write("Master Data Preview (Row 0-5):", st.session_state["master_sim_df"].head())


# def handle_simulator_change():
#     state = st.session_state.get("assignment_simulator_key")
#     if not state:
#         return

#     active_year = st.session_state.get("sel_review_year")

#     # Access the master dataframe directly
#     master_df = st.session_state["master_sim_df"]

#     for row_idx, edits in state["edited_rows"].items():
#         # row_idx here is the ACTUAL index from the original dataframe
#         for col_name, new_val in edits.items():
#             # 1. Update the master record using the index
#             master_df.at[row_idx, col_name] = new_val

#             # 2. If the user edited the 'Stage', sync it to the specific year column
#             if col_name == "Simulator Operating Stage" and active_year:
#                 master_df.at[row_idx, active_year] = new_val

#     # Save it back to session state to be safe
#     st.session_state["master_sim_df"] = master_df


# def load_shed_assignment():

#     # 1. Initialize data
#     ls_obj = st.session_state.get("loadshedding")

#     if not ls_obj:
#         st.error("Load shedding data not found in session state.")
#         return

#     masterlist = ls_obj.ls_assignment_masterlist()
#     incomer_relay = ls_obj.incomer_relay()
#     ls_stage = {
#         "UFLS": ls_obj.ufls_setting.columns.tolist(),
#         "UVLS": ls_obj.uvls_setting.columns.tolist(),
#     }

#     unique_schemes = ls_obj.pocket_relay()[["assignment_id", "scheme"]].drop_duplicates(
#         subset=["assignment_id"]
#     )

#     valid_candidate = (
#         pd.merge(masterlist, unique_schemes, on="assignment_id", how="left")
#         .pipe(lambda df: pd.concat([df, incomer_relay], ignore_index=True, sort=False))
#         .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
#         .query("scheme != 'emls'")
#     )

#     all_scheme = [
#         col
#         for col in valid_candidate.columns
#         if any(keyword in col for keyword in ls_obj.LOADSHED_SCHEME)
#     ]
#     review_list = [col for col in all_scheme if not col.startswith("EMLS")]

#     st.subheader("Load Sheddding Assignment Simulator")

#     c1, c2, c3 = st.columns(3)

#     with c1:
#         review_year = st.selectbox("Base Referrence", options=review_list, key="simulator_review_year")

#     with c2:
#         zones = st.multiselect(
#             "Zone",
#             options=valid_candidate["zone"].dropna().unique(),
#             key="simulator_zones",
#         )

#     # st.markdown("valid_candidate")
#     # st.dataframe(valid_candidate)

#     simulator_df = (
#         valid_candidate[["zone","assignment_id", review_year, "critical_list"]]
#         .drop_duplicates(subset=["assignment_id"], keep="first")
#         .rename(columns={"zone": "Zone","assignment_id": "Assignment", "critical_list": "Flag"})
#         .reset_index()
#     )
#     simulator_df["Flag"] = simulator_df["Flag"].mask(
#         simulator_df["Flag"].notna(), "Critical Delivery Point"
#     )

#     simulator_df["Simulator Operating Stage"] = simulator_df[review_year]
#     simulator_df = simulator_df[
#         ["Zone", "Assignment", review_year, "Simulator Operating Stage", "Flag"]
#     ]

#     st.session_state["simulator"] = simulator_df

#     # 2. The Correct Callback Logic
#     def handle_change():
#         # Retrieve the state of the editor
#         state = st.session_state.assignment_simulator_key

#         # IMPORTANT: Update the source dataframe with ALL edits
#         for row_idx, edits in state["edited_rows"].items():
#             for col_name, new_val in edits.items():
#                 # Update the source of truth
#                 st.session_state.simulator.at[row_idx, col_name] = new_val

#                 # --- APPLY YOUR LOGIC CONDITIONS HERE ---
#                 # if col_name == "Status" and new_val == "Completed":
#                 #     st.session_state.simulator.at[row_idx, "Notes"] = (
#                 #         "Auto-filled: Done!"
#                 #     )
#                 # ----------------------------------------

#     # 3. Display the Data Editor
#     st.data_editor(
#         st.session_state["simulator"],
#         key="assignment_simulator_key",
#         on_change=handle_change,
#         column_config={
#             "Simulator Operating Stage": st.column_config.SelectboxColumn(
#                 "Simulator Operating Stage",
#                 options=ls_stage[review_year[:4]],
#             ),
#             "Zone": st.column_config.Column(disabled=True),
#             "Assignment": st.column_config.Column(disabled=True),
#             review_year: st.column_config.Column(disabled=True),
#             "Flag": st.column_config.Column(disabled=True),
#         },
#         hide_index=True,
#     )

#     # 1. State Initialization
#     # load_obj = st.session_state.get("loadprofile")
#     # total_mw = load_obj.totalMW()

#     # ls_obj = st.session_state.get("loadshedding")
#     # masterlist = ls_obj.ls_assignment_masterlist

#     # ufls_setting = ls_obj.ufls_setting
#     # uvls_setting = ls_obj.uvls_setting

#     # TARGET_UFLS = 0.5
#     # TARGET_UVLS = 0.2
#     # TARGET_EMLS = 0.3

#     # loadprofile = st.session_state["loadprofile"]
#     # total_mw = loadprofile.totalMW()
#     # north_mw = loadprofile.regional_loadprofile("North")
#     # kvalley_mw = loadprofile.regional_loadprofile("KlangValley")
#     # south_mw = loadprofile.regional_loadprofile("South")
#     # east_mw = loadprofile.regional_loadprofile("East")

#     # loadshedding = st.session_state["loadshedding"]

#     # ########## debugging info ##########

#     # # st.dataframe(loadshedding.loadshedding_assignments())
#     # # st.dataframe(loadshedding.dp_grpId_loadquantum())
#     # # st.divider()

#     # ########## debugging info ##########

#     # ## section 1: Load Quantum Target Metrics ##
#     # st.subheader("Load Quantum Target Metrics")

#     # ## sub-section 1: Review Year Input ##
#     # tab2_s1_col1, tab2_s1_col2 = st.columns(2)

#     # with tab2_s1_col1:
#     #     current_year = date.today().year
#     #     review_year = st.number_input(
#     #         label="Review Year",
#     #         min_value=current_year,
#     #         max_value=current_year + 10,
#     #         value=current_year,
#     #         step=1,
#     #         format="%d",
#     #         key="review_year_ls_reviewer",
#     #     )

#     # with tab2_s1_col2:
#     #     ls_scheme = st.selectbox(
#     #         label="Scheme", options=["UFLS", "UVLS", "EMLS"], index=0
#     #     )

#     # ######################################
#     # ## sub-section 2: Review Year Input ##
#     # ######################################

#     # tab2_s2_col1, tab2_s2_col2, tab2_s2_col3 = st.columns([2.5, 4, 4])

#     # target = (
#     #     TARGET_UFLS
#     #     if ls_scheme == "UFLS"
#     #     else TARGET_UVLS if ls_scheme == "UVLS" else TARGET_EMLS
#     # )

#     # with tab2_s2_col1:
#     #     st.metric(
#     #         f"Total Latest MD: {total_mw:,} MW",
#     #         f"Target {ls_scheme}: {int(target*total_mw):,} MW ({int((target*total_mw/total_mw)*100)}%)",
#     #     )

#     # with tab2_s2_col2:
#     #     colf2_1, colf2_2 = st.columns(2)
#     #     with colf2_1:
#     #         st.metric(
#     #             label=f"North: {north_mw:,} MW",
#     #             value=f"Target: {int(target*north_mw):,} MW ({int((target*north_mw/north_mw)*100)}%)",
#     #         )
#     #         st.metric(
#     #             label=f"Klang Valley: {kvalley_mw:,} MW",
#     #             value=f"Target: {int(target*kvalley_mw):,} MW ({int((target*kvalley_mw/kvalley_mw)*100)}%)",
#     #         )

#     #     with colf2_2:
#     #         st.metric(
#     #             label=f"South: {south_mw:,} MW",
#     #             value=f"Target: {int(target*south_mw):,} MW ({int((target*south_mw/south_mw)*100)}%)",
#     #         )
#     #         st.metric(
#     #             label=f"East: {east_mw:,} MW",
#     #             value=f"Target: {int(target*east_mw):,} MW ({int((target*east_mw/east_mw)*100)}%)",
#     #         )

#     # with tab2_s2_col3:
#     #     pass
#     # st.divider()

#     # #############################################################
#     # ## sub-section 3: Available Load Shedding Quantum Capacity ##
#     # #############################################################
#     # available_assignment = loadshedding.automatic_loadshedding_rly()
#     # remove_duplicate = available_assignment.drop_duplicates(
#     #     subset=["local_trip_id", "mnemonic", "feeder_id"], keep="first"
#     # )

#     # st.subheader("Available Load Shedding Quantum Capacity")

#     # show_table = st.checkbox(
#     #     "**Show Available Load Shedding Quantum Capacity Data**", value=False
#     # )

#     # if show_table:

#     #     avail_quantum_mw = remove_duplicate["Pload (MW)"].sum()
#     #     north_avail_MW = load_profile_metric(remove_duplicate, "North")
#     #     kValley_avail_MW = load_profile_metric(remove_duplicate, "KlangValley")
#     #     south_avail_MW = load_profile_metric(remove_duplicate, "South")
#     #     east_avail_MW = load_profile_metric(remove_duplicate, "East")

#     #     tab2_s3_col1, tab2_s3_col2, tab2_s3_col3 = st.columns([2.5, 2.5, 4])

#     #     with tab2_s3_col1:
#     #         st.metric(
#     #             label=f"Available Potential Quantum: ",
#     #             value=f"{int(avail_quantum_mw):,} MW ({int((avail_quantum_mw/total_mw)*100)}%)",
#     #         )

#     #     with tab2_s3_col2:
#     #         col_s3_1, col_s3_2 = st.columns(2)
#     #         with col_s3_1:
#     #             st.metric(
#     #                 label=f"North: ",
#     #                 value=f"{int(north_avail_MW):,} MW ({int((north_avail_MW/north_mw)*100)}%)",
#     #             )
#     #             st.metric(
#     #                 label=f"Klang Valley: ",
#     #                 value=f"{int(kValley_avail_MW):,} MW ({int((kValley_avail_MW/kvalley_mw)*100)}%)",
#     #             )

#     #         with col_s3_2:
#     #             st.metric(
#     #                 label=f"South: ",
#     #                 value=f"{int(south_avail_MW):,} MW ({int((south_avail_MW/south_mw)*100)}%)",
#     #             )
#     #             st.metric(
#     #                 label=f"East: ",
#     #                 value=f"{int(east_avail_MW):,} MW ({int((east_avail_MW/east_mw)*100)}%)",
#     #             )

#     #     with tab2_s3_col3:
#     #         pass

#     #     #### filter options
#     #     col2_s3_col1, col2_s3_col2, col2_s3_col3 = st.columns(3)

#     #     with col2_s3_col1:
#     #         zone = list(set(zone_mapping.values()))
#     #         zone_selected = st.multiselect(
#     #             label="Zone Location",
#     #             options=zone,
#     #             key="avail_loadshed_zone"
#     #         )
#     #     with col2_s3_col2:
#     #         search_query = st.text_input(
#     #             label="Search for a Keyword:",
#     #             placeholder="Enter your search keyword here...",
#     #             key="avail_loadshed_search_box",
#     #         )

#     #     filters = {
#     #         # "review_year": review_year,
#     #         # "scheme": selected_ls_scheme,
#     #         # "op_stage": stage_selected,
#     #         "zone": zone_selected,
#     #         # "gm_subzone": subzone_selected,
#     #         # "ls_dp": trip_assignment,
#     #     }

#     #     filtered_data = loadshedding.filtered_data(
#     #         filters=filters, df=available_assignment
#     #     )

#     #     st.dataframe(filtered_data)

#     # st.divider()

#     # #############################################################
#     # ## sub-section 4: Available Load Shedding Quantum Capacity ##
#     # #############################################################
#     # st.subheader("Simulator")

#     # ls_assignment_masterlist = loadshedding.ls_assignment_masterlist()

#     # tab2_s4_col1, tab2_s4_col2, tab2_s4_col3 = st.columns([2.5, 2.5, 4])

#     # with tab2_s4_col1:
#     #     ls_cols = [
#     #         col
#     #         for col in ls_assignment_masterlist.columns
#     #         if any(keyword in col for keyword in ["UFLS", "UVLS", "EMLS"])
#     #     ]
#     #     current_datetime = pd.to_datetime("now")
#     #     current_year = current_datetime.year
#     #     prev_year = current_year - 1
#     #     target_col = f"UFLS_{prev_year}"
#     #     default_selection = None

#     #     if target_col in ls_cols:
#     #         default_selection = target_col
#     #     else:
#     #         for col in ls_cols:
#     #             if "UFLS" in col:
#     #                 default_selection = col
#     #                 break
#     #     if default_selection and default_selection in ls_cols:
#     #         default_index = ls_cols.index(default_selection)
#     #     else:
#     #         default_index = 0

#     #     based_template = st.selectbox(
#     #         label="Based Template",
#     #         options=ls_cols,
#     #         key="simulator_based_template",
#     #         index=default_index,
#     #     )

#     #     drop_ls = [col for col in ls_cols if col != based_template]
#     #     based_ls_df = ls_assignment_masterlist.drop(columns=drop_ls, axis=1).reset_index(
#     #         drop=True
#     #     )
#     #     based_available_assignment = pd.merge(
#     #         available_assignment,
#     #         based_ls_df,
#     #         on=[
#     #             "assignment_id",
#     #             "local_trip_id",
#     #             "mnemonic",
#     #             "feeder_id",
#     #             "breaker_id",
#     #             "kV",
#     #             "zone",
#     #             "gm_subzone",
#     #             "group_trip_id",
#     #             "ls_dp",
#     #             "critical_list",
#     #             "short_text",
#     #             "long_text",
#     #             "Pload (MW)",
#     #             "Qload (Mvar)",
#     #             "substation_name",
#     #         ],
#     #         how="outer",
#     #     )
#     #     assignment_df = based_available_assignment[
#     #         [
#     #             "assignment_id",
#     #             "local_trip_id",
#     #             "Pload (MW)",
#     #             based_template,
#     #             "critical_list",
#     #             "zone",
#     #         ]
#     #     ]
#     #     grp_df = assignment_df.groupby(
#     #         ["assignment_id", based_template], as_index=False
#     #     ).agg(
#     #         {
#     #             "Pload (MW)": "sum",
#     #             "local_trip_id": lambda x: ", ".join(x.astype(str).unique()),
#     #             "critical_list": lambda x: ", ".join(x.astype(str).unique()),
#     #             "zone": lambda x: ", ".join(x.astype(str).unique()),
#     #         }
#     #     )

#     # st.dataframe(grp_df)
