import pandas as pd
import streamlit as st

from pages.load_shedding.helper import join_unique_non_empty, find_latest_assignment
from pages.load_shedding.tab4b_sim_dashboard import sim_dashboard
from applications.load_shedding.helper import scheme_col_sorted
from css.streamlit_css import custom_metric
from pages.load_shedding.tab4a_sim_conflict import stage_conflict


def simulator():
    st.subheader("Load Shedding Assignment Simulator")

    # Load required objects from session state
    ls_obj = st.session_state.get("loadshedding")
    lprofile_obj = st.session_state.get("loadprofile")
    
    if not ls_obj or not lprofile_obj:
        st.error("Load shedding data not found in session state.")
        return

    # Get scheme columns
    raw_master = ls_obj.ls_assignment_masterlist()
    scheme_cols = [
        c for c in raw_master.columns
        if any(k in c for k in ls_obj.LOADSHED_SCHEME)
        and not c.startswith("EMLS")
    ]

    if not scheme_cols:
        st.error("No valid load shedding scheme columns found.")
        return

    # UI Controls
    c1, c2 = st.columns(2)
    
    with c1:
        review_year = st.selectbox(
            "Base Reference",
            options=scheme_cols,
            key="sim_review_year"
        )

    # Session state keys
    sim_key = f"sim_data_{review_year}"
    editor_key = f"assignment_simulator_{review_year}"

    # Initialize session state for this review year
    if sim_key not in st.session_state:
        sim_df, valid_candidate, raw_candidate = build_master_sim_df(
            ls_obj, review_year
        )
        
        st.session_state[sim_key] = {
            "sim_df": sim_df,
            "raw_candidate": raw_candidate,
            "valid_candidate": valid_candidate,
            "last_editor_state": {},  # Track previous editor state
            "needs_conflict_update": True  # Flag for conflict recalculation
        }
    else:
        # Ensure existing session state has all required keys
        sim_data = st.session_state[sim_key]
        
        # Add missing keys to existing session state
        if "last_editor_state" not in sim_data:
            sim_data["last_editor_state"] = {}
        
        if "needs_conflict_update" not in sim_data:
            sim_data["needs_conflict_update"] = True
    
    # Get data from session state
    sim_data = st.session_state[sim_key]
    master_df = sim_data["sim_df"].copy()  # Work on a copy
    raw_candidate = sim_data["raw_candidate"]
    valid_candidate = sim_data["valid_candidate"]
    
    # Get current editor state
    current_editor_state = st.session_state.get(editor_key, {})
    last_editor_state = sim_data.get("last_editor_state", {})
    
    # Check if editor was modified
    editor_modified = False
    current_edits = current_editor_state.get("edited_rows", {})
    last_edits = last_editor_state.get("edited_rows", {})
    
    if current_edits != last_edits:
        editor_modified = True
        # Apply editor changes immediately
        if current_edits:
            update_master_from_editor(master_df, current_editor_state, review_year)
            
        # Update tracker
        sim_data["last_editor_state"] = current_editor_state.copy()
        sim_data["needs_conflict_update"] = True
    
    # Get the needs_conflict_update flag with safe default
    needs_update = sim_data.get("needs_conflict_update", True)
    
    # Always update conflict detection if needed
    if needs_update:
        # Run conflict detection on current data
        master_df = stage_conflict(master_df, valid_candidate, ls_obj, review_year)
        
        # Update session state
        sim_data["sim_df"] = master_df
        sim_data["needs_conflict_update"] = False
    
    # Update session state with the modified DataFrame
    st.session_state[sim_key]["sim_df"] = master_df
    
    # Zone filter
    with c2:
        zone_options = sorted(master_df["Zone"].dropna().unique())
        selected_zones = st.multiselect(
            "Filter by Zone",
            options=zone_options,
            key=f"zone_filter_{review_year}",
        )
    
    # Prepare view DataFrame (filtered if zones selected)
    view_df = master_df.copy()
    if selected_zones:
        view_df = view_df[view_df["Zone"].isin(selected_zones)]
    
    # Stage options for dropdown
    if review_year.startswith("UFLS"):
        stage_options = ls_obj.ufls_setting.columns.tolist()
    elif review_year.startswith("UVLS"):
        stage_options = ls_obj.uvls_setting.columns.tolist()
    else:
        stage_options = []
    
    # Store row mapping for editor updates
    row_map_key = f"_row_map_{review_year}"
    st.session_state[row_map_key] = (
        view_df["Assignment"]
        .reset_index(drop=True)
        .to_dict()
    )
    
    # Layout containers
    editor_container = st.container()
    alarm_container = st.container()
    result_container = st.container()
    
    with editor_container:
        editor_table, metrics = st.columns([3, 1])
        
        with editor_table:
            # Display data editor
            edited_df = st.data_editor(
                view_df[
                    ["Zone", "Assignment", review_year,
                     "Sim. Oper. Stage", "Load (MW)", "Flag"]
                ],
                key=editor_key,
                hide_index=True,
                width='stretch',
                column_config={
                    "Sim. Oper. Stage": st.column_config.SelectboxColumn(
                        "Sim. Oper. Stage",
                        options=stage_options,
                        help="Select the operating stage",
                    ),
                    "Zone": st.column_config.Column(disabled=True),
                    "Assignment": st.column_config.Column(disabled=True),
                    review_year: st.column_config.Column(
                        f"Ref.: {review_year}", disabled=True
                    ),
                    "Load (MW)": st.column_config.Column(disabled=True),
                    "Flag": st.column_config.Column(disabled=True),
                },
            )
            
            # Add a refresh button for immediate conflict update
            save_btn, reset_sim_stg, refresh_col2 = st.columns([2, 2, 2])
            
            # with reset_sim_stg:
            #     if st.button("↪️ Reset Sim. Oper. Stage", 
            #                 key=f"reset_sim_oper_stg{review_year}",
            #                 type="secondary",
            #                 use_container_width=True):
                    
            #         # Store reset flag in a DIFFERENT key
            #         st.session_state[f"reset_flag_{editor_key}"] = True
            #         st.rerun()

            # # At the beginning of your function, check for reset flag
            # if st.session_state.get(f"reset_flag_{editor_key}", False):
            #     # Perform reset operations
            #     master_df["Sim. Oper. Stage"] = None
            #     master_df["Flag"] = master_df["Flag"].str.replace(r'Conflict:.*', '', regex=True).str.strip()
            #     master_df["Conflict_Columns"] = ''
                
            #     # Update session state
            #     st.session_state[sim_key]["sim_df"] = master_df
                
            #     # Clear the reset flag
            #     st.session_state[f"reset_flag_{editor_key}"] = False
                        
            with refresh_col2:
                if st.button("🔄 Update Conflicts", 
                        key=f"refresh_conflicts_{review_year}",
                        type="secondary",
                        use_container_width=True):
                    # Force conflict recalculation
                    sim_data["needs_conflict_update"] = True
                    st.rerun()
        
        with metrics:
            # Calculate and display metrics
            display_simulation_metrics(master_df, raw_candidate, lprofile_obj, review_year)
    
    with alarm_container:
        # Display conflicts
        display_conflicts(view_df, review_year)
    
    with result_container:
        # Show dashboard
        sim_dashboard(simulator_df=master_df,
                     candidate_df=raw_candidate, 
                     scheme=review_year[:4])
def display_simulation_metrics(master_df, raw_candidate, lprofile_obj, review_year):
    """Display simulation metrics in the right column"""
    
    # Merge to get simulation data
    sim_ls = pd.merge(
        raw_candidate,
        master_df[["Assignment", "Sim. Oper. Stage"]],
        left_on="assignment_id",
        right_on="Assignment",
        how="left"
    )
    
    # Calculate stage quantum
    stg_quantum = sim_ls.groupby(
        ["Sim. Oper. Stage", "zone"], as_index=False
    ).agg({"Load (MW)": "sum"})
    
    # Get available stages
    stage = scheme_col_sorted(
        sim_ls.loc[sim_ls["Sim. Oper. Stage"].notna()], 
        "Sim. Oper. Stage"
    )["Sim. Oper. Stage"]
    
    # Stage selector
    oper_stage = st.selectbox(
        "Filter by Sim. Oper. Stage",
        options=stage.unique().tolist(),
        key=f"sim_oper_stage_{review_year}"
    )
    
    # Calculate quantum
    quantum_df = stg_quantum.groupby(
        ["Sim. Oper. Stage"], as_index=False
    ).agg({"Load (MW)": "sum"})
    
    quantum = quantum_df.loc[quantum_df["Sim. Oper. Stage"] == oper_stage, "Load (MW)"]
    quantum_val = quantum.values[0] if not quantum.empty else 0
    
    # Grid load percentage
    grid_load = lprofile_obj.totalMW()
    pct = (quantum_val / grid_load * 100) if grid_load > 0 else 0
    
    # Display metric
    custom_metric(
        label=f"{oper_stage.title()} Quantum:",
        value=f"{quantum_val:,.0f} MW <span style='font-size: 14px;'>({pct:,.1f}% of {grid_load:,.0f}MW)</span>",
    )
    
    # Zone-wise breakdown
    st.markdown("**Zone Breakdown:**")
    for zone in sim_ls["zone"].dropna().unique().tolist():
        sim_zone = stg_quantum.loc[stg_quantum["zone"] == zone]
        sim_zone_stg = sim_zone.loc[sim_zone["Sim. Oper. Stage"] == oper_stage]
        mw_zone_stg = sim_zone_stg["Load (MW)"].values[0] if not sim_zone_stg.empty else 0
        
        zone_load = lprofile_obj.regional_loadprofile(zone)
        zone_load_pct = (mw_zone_stg / zone_load * 100) if zone_load > 0 else 0
        
        st.markdown(
            f'<span style="color: inherit; font-size: 14px; font-weight: 400">{zone}: </span>'
            f'<span style="color: inherit; font-size: 16px; font-weight: 600">'
            f'{mw_zone_stg:,.0f} MW ({zone_load_pct:,.1f}% of {zone_load:,.0f}MW)</span>',
            unsafe_allow_html=True,
        )


def display_conflicts(view_df, review_year):
    """Display conflict warnings/alerts"""
    
    # Check for conflicts
    conflict_col = view_df.loc[
        view_df["Conflict_Columns"].notna() & 
        (view_df["Conflict_Columns"] != '')
    ]
    
    if not conflict_col.empty:
        # Show summary
        st.error(f"⚠️ **{len(conflict_col)} Conflicts Detected**")
        
        # Show each conflict
        for index, row in conflict_col.iterrows():
            assignment = row["Assignment"]
            conflict = row["Conflict_Columns"]  
            stage = row["Sim. Oper. Stage"] 
            
            # Use expander for each conflict
            with st.expander(f"**{assignment}** ({stage})", icon="⚠️"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Zone:** {row.get('Zone', 'N/A')}")
                    st.write(f"**Assignment:** {assignment}")
                    st.write(f"**Stage:** {stage}")
                    st.write(f"**Load:** {row.get('Load (MW)', 'N/A')} MW")
                with col2:
                    st.error(f"**Conflict:**")
                    st.error(f"{conflict}")
                    st.warning(f"**Flag:** {row.get('Flag', 'N/A')}")
        
        # Add a clear conflicts button
        if st.button("🗑️ Clear All Conflict Flags", 
                    key=f"clear_conflicts_{review_year}",
                    type="secondary"):
            # This would need to be implemented based on your business logic
            st.info("Conflict clearing functionality would go here")
            st.rerun()
    else:
        st.success("✅ **No conflicts detected!**")
        st.balloons()


def build_master_sim_df(ls_obj, review_year):
    """Build the master simulation DataFrame"""
    
    masterlist = ls_obj.ls_assignment_masterlist()
    incomer = ls_obj.incomer_relay()

    scheme_map = (
        ls_obj.pocket_relay()[["assignment_id", "scheme"]]
        .drop_duplicates(subset=["assignment_id"])
    )

    scheme_cols = [
        c for c in masterlist.columns
        if any(c.startswith(k) for k in ls_obj.LOADSHED_SCHEME)
    ]

    grp_cols = ["assignment_id"]
    join_cols = scheme_cols + [
        "mnemonic", "kV", "feeder_id", "breaker_id",
        "state", "gm_subzone", "substation_name", 
        "coordinate", "zone", "critical_list", "scheme"
    ]
    sum_cols = ["Load (MW)"]
    
    agg_dict = (
        {col: join_unique_non_empty for col in join_cols}
        | {col: "sum" for col in sum_cols}
    )

    # Build raw candidate
    raw_candidate = (
        pd.merge(masterlist, scheme_map, on="assignment_id", how="left")
        .pipe(lambda df: pd.concat([df, incomer], ignore_index=True, sort=False))
        .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
    )

    # Aggregate to valid candidate
    valid_candidate = raw_candidate.groupby(
        grp_cols, dropna=False).agg(agg_dict).reset_index()

    # Filter out EMLS
    valid_candidate = valid_candidate[
        valid_candidate["scheme"].str.lower() != "emls"
    ]

    # Build simulation DataFrame
    sim_df = (
        valid_candidate[
            ["zone", "assignment_id", review_year, "critical_list", "Load (MW)"]
        ]
        .rename(columns={
            "zone": "Zone",
            "assignment_id": "Assignment",
            "critical_list": "Flag",
        })
        .copy()
    )

    # Initialize flag column
    sim_df["Flag"] = sim_df["Flag"].where(
        sim_df["Flag"].isna(), "Critical List"
    )

    # Validate review_year column exists
    if review_year not in sim_df.columns:
        raise ValueError(f"Column '{review_year}' not found in data.")

    # Initialize simulation stage column
    sim_df["Sim. Oper. Stage"] = sim_df[review_year]

    return sim_df, valid_candidate, raw_candidate


def update_master_from_editor(master_df, editor_state, review_year):
    """Update master DataFrame from editor state"""
    
    row_map_key = f"_row_map_{review_year}"
    row_map = st.session_state.get(row_map_key, {})
    
    if not row_map:
        return
    
    edited_rows = editor_state.get("edited_rows", {})
    
    if not edited_rows:
        return
    
    for row_idx, changes in edited_rows.items():
        assignment = row_map.get(row_idx)
        if assignment is None:
            continue
        
        if "Sim. Oper. Stage" in changes:
            new_stage = changes["Sim. Oper. Stage"]
            
            # Update the stage in master_df
            master_df.loc[
                master_df["Assignment"] == assignment,
                "Sim. Oper. Stage"
            ] = new_stage
    
    # Clear the edited rows after processing
    editor_state["edited_rows"] = {}