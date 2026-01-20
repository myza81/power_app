import re
import pandas as pd
import numpy as np
import streamlit as st
from pages.load_shedding.helper import join_unique_non_empty
from pages.load_shedding.tab4b_sim_dashboard import sim_dashboard
from pages.load_shedding.tab4a_sim_conflict import conflict_assignment
from pages.load_shedding.tab4c_sim_save import save_sim_data, col_sim_validation
from applications.load_shedding.helper import scheme_col_sorted
from css.streamlit_css import custom_metric

SIM_STAGE = "Sim. Stage"


def simulator():
    st.subheader("Load Shedding Assignment Simulator")

    input_container = st.container()
    editor_container = st.container()
    save_sim_container = st.container()
    alarm_container = st.container()
    dashboard_container = st.container()

    ls_obj = st.session_state.get("loadshedding")
    lprofile_obj = st.session_state.get("loadprofile")

    if not ls_obj or not lprofile_obj:
        st.error("Load shedding data not found in session state.")
        return

    raw_master = ls_obj.ls_assignment_masterlist()
    scheme_cols = [
        c for c in raw_master.columns
        if any(k in c for k in ls_obj.LOADSHED_SCHEME)
        and not c.startswith("EMLS")
    ]

    if not scheme_cols:
        st.error("No valid load shedding scheme columns found.")
        return

    with input_container:
        c1, c2, c3 = st.columns(3)

        with c1:
            review_year = st.selectbox(
                "Base Reference",
                options=scheme_cols,
                key="sim_review_year"
            )

            master_df_key = f"master_df_key_{review_year}"
            sim_key = f"sim_data_{review_year}"
            editor_key = f"sim_editor_{review_year}"
            export_sim_key = f"show_export_{review_year}"

            if export_sim_key not in st.session_state:
                st.session_state[export_sim_key] = False

            if master_df_key not in st.session_state:
                valid_candidate, raw_candidate = build_master_df(ls_obj)
                st.session_state[master_df_key] = {
                    "valid_candidate": valid_candidate,
                    "raw_candidate": raw_candidate,
                    "master_df": generate_sim_df(valid_candidate, review_year),
                }

            raw_candidate = st.session_state[master_df_key]["raw_candidate"]
            sim_candidate = st.session_state[master_df_key]["valid_candidate"]
            master_df = st.session_state[master_df_key]["master_df"]

            if sim_key not in st.session_state:
                st.session_state[sim_key] = {
                    "sim_df": master_df.copy(),
                    "last_editor_state": {},
                }

            sim_data = st.session_state[sim_key]
            sim_df = sim_data["sim_df"]

            current_editor_state = st.session_state.get(editor_key, {})
            last_editor_state = sim_data.get("last_editor_state", {})

            current_edits = current_editor_state.get("edited_rows", {})
            last_edits = last_editor_state.get("edited_rows", {})

            if current_edits != last_edits:
                if current_edits:
                    sim_df = update_sim_df_from_editor(
                        sim_df, current_editor_state, review_year
                    )

                sim_data["last_editor_state"] = current_editor_state.copy()
                st.session_state[export_sim_key] = False

            sim_df = conflict_assignment(
                sim_df, sim_candidate, ls_obj, review_year, SIM_STAGE)

            sim_data["sim_df"] = sim_df

        with c2:
            zone_options = sorted(sim_df["Zone"].dropna().unique())
            selected_zones = st.multiselect(
                "Filter by Zone",
                options=zone_options,
                key=f"zone_filter_{review_year}",
            )

        with c3:
            assignment_list = sim_df["Assignment"].tolist()
            assignment_id = st.multiselect(
                label="Assignment Finder",
                options=assignment_list,
                key=f"subs_search_{review_year}",
            )

        view_df = sim_df.copy()
        if selected_zones:
            view_df = view_df[view_df["Zone"].isin(selected_zones)]

        if assignment_id:
            view_df = view_df[view_df["Assignment"].isin(assignment_id)]

        if review_year.startswith("UFLS"):
            stage_options = ls_obj.ufls_setting.columns.tolist()
        elif review_year.startswith("UVLS"):
            stage_options = ls_obj.uvls_setting.columns.tolist()
        else:
            stage_options = []

        row_map_key = f"_row_map_{review_year}"
        st.session_state[row_map_key] = (
            view_df["Assignment"]
            .reset_index(drop=True)
            .to_dict()
        )

    with editor_container:
        editor_table, _, metrics = st.columns([3, 0.01, 1.2])

        with editor_table:
            cols_to_show = ["Zone", "Assignment", review_year,
                            "Load (MW)", "Critical Subs", SIM_STAGE, "Flag"]
            subset_df = view_df[cols_to_show]

            st.data_editor(
                subset_df,
                key=editor_key,
                hide_index=True,
                width="stretch",
                column_config={
                    SIM_STAGE: st.column_config.SelectboxColumn(
                        SIM_STAGE,
                        options=stage_options,
                        help="⚠️ Editable simulation stage",
                    ),
                    "Zone": st.column_config.Column(disabled=True),
                    "Assignment": st.column_config.Column(disabled=True),
                    review_year: st.column_config.Column(
                        f"Ref.: {review_year}", disabled=True
                    ),
                    "Load (MW)": st.column_config.Column(disabled=True),
                    "Critical Subs": st.column_config.Column(disabled=True),
                    "Flag": st.column_config.Column(disabled=True),
                },
            )

            colname_input, save, reset, empty = st.columns(
                [2, 1.5, 1.5, 1.5])

            with colname_input:
                ls_colname = st.text_input(
                    label="Filename",
                    placeholder="Use format e.g, 2025 or 2025v1",
                    label_visibility="collapsed",
                    key=f"simls_colname_{review_year}",
                    help="Enter 4-digit year (2025) for final, or add version like 2025v1 for drafts"
                )

            with save:
                button_disabled = col_sim_validation(ls_colname)

                st.button(
                    label="💾 Save",
                    disabled=button_disabled,
                    on_click=save_sim_data,
                    args=(sim_df, ls_colname, review_year,
                          save_sim_container),
                    key=f"save_sim_{review_year}",
                    width='stretch',
                    help="Invalid format! Please use format e.g., 2025 or 2025v1" if button_disabled else ""
                )

            with reset:
                st.button(
                    label="🔄 Reset",
                    on_click=reset_to_base_reference,
                    args=(master_df, sim_key),
                    key=f"reset_to_base_{review_year}",
                    width='stretch',
                )

            with empty:
                st.button(
                    label="🧹 Clear",
                    on_click=reset_to_empty_sim_df,
                    args=(sim_df, sim_key),
                    key=f"reset_to_empty_{review_year}",
                    width='stretch',
                )

        with metrics:
            display_simulation_metrics(
                sim_df, raw_candidate, lprofile_obj, review_year)

    with alarm_container:
        display_conflicts(view_df, ls_obj, ref_stage_col=SIM_STAGE)

    with dashboard_container:
        sim_dashboard(simulator_df=sim_df,
                      candidate_df=raw_candidate,
                      scheme=review_year[:4])


def reset_to_empty_sim_df(sim_df, sim_key):
    cleared_df = sim_df.copy()
    cleared_df[SIM_STAGE] = None
    cleared_df["conflict_assignment"] = ""

    st.session_state[sim_key]["sim_df"] = cleared_df


def reset_to_base_reference(master_df, sim_key):
    st.session_state[sim_key]["sim_df"] = master_df.copy()


def display_simulation_metrics(sim_df, raw_candidate, lprofile_obj, review_year):

    sim_ls = pd.merge(
        raw_candidate,
        sim_df[["Assignment", SIM_STAGE]],
        left_on="assignment_id",
        right_on="Assignment",
        how="left"
    )

    # Calculate stage quantum
    stg_quantum = sim_ls.groupby(
        [SIM_STAGE, "zone"], as_index=False
    ).agg({"Load (MW)": "sum"})

    # Get available stages
    stage = scheme_col_sorted(
        sim_ls.loc[sim_ls[SIM_STAGE].notna()],
        SIM_STAGE
    )[SIM_STAGE]

    # Stage selector
    oper_stage = st.selectbox(
        "Filter by Sim. Oper. Stage",
        options=stage.unique().tolist(),
        key=f"sim_oper_stage_{review_year}"
    )

    if oper_stage is not None:
        # Calculate quantum
        quantum_df = stg_quantum.groupby(
            [SIM_STAGE], as_index=False
        ).agg({"Load (MW)": "sum"})

        quantum = quantum_df.loc[quantum_df[SIM_STAGE]
                                 == oper_stage, "Load (MW)"]
        quantum_val = quantum.values[0] if not quantum.empty else 0

        # Grid load percentage
        grid_load = lprofile_obj.totalMW()
        pct = (quantum_val / grid_load * 100) if grid_load > 0 else 0

        # Display metric
        custom_metric(
            label=f"{oper_stage.title()} Quantum:",
            value1=f"{quantum_val:,.0f}MW",
            value2=f"<span style='font-size: 14px;'>({pct:,.1f}% of {grid_load:,.0f}MW)</span>",
        )

        st.markdown("**Zone Breakdown:**")
        for zone in sim_ls["zone"].dropna().unique().tolist():
            sim_zone = stg_quantum.loc[stg_quantum["zone"] == zone]
            sim_zone_stg = sim_zone.loc[sim_zone[SIM_STAGE]
                                        == oper_stage]
            mw_zone_stg = sim_zone_stg["Load (MW)"].values[0] if not sim_zone_stg.empty else 0

            zone_load = lprofile_obj.regional_loadprofile(zone)
            zone_load_pct = (mw_zone_stg / zone_load *
                             100) if zone_load > 0 else 0

            st.markdown(
                f'<span style="color: inherit; font-size: 14px; font-weight: 400">{zone}: </span>'
                f'<span style="color: inherit; font-size: 16px; font-weight: 600">'
                f'{mw_zone_stg:,.0f}MW ({zone_load_pct:,.1f}% of {zone_load:,.0f}MW)</span>',
                unsafe_allow_html=True,
            )


def display_conflicts(view_df, ls_obj, ref_stage_col):

    warning_rows = view_df[view_df["Flag"].str.contains("Warning", na=False)]
    alert_rows = view_df[view_df["Flag"].str.contains("Alert", na=False)]

    ls_assign_mlist = ls_obj.ls_assignment_masterlist()

    if not warning_rows.empty:
        render_conflict_block(
            warning_rows, ls_assign_mlist,
            f"**{len(warning_rows)} Warning Detected**",
            ref_stage_col
        )

    if not alert_rows.empty:
        render_conflict_block(
            alert_rows, ls_assign_mlist,
            f"**{len(alert_rows)} Alert Detected**",
            ref_stage_col
        )

    if warning_rows.empty and alert_rows.empty:
        st.success("✅ **No conflicts detected!**")
        st.balloons()


def build_master_df(ls_obj):

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

    return valid_candidate, raw_candidate


def generate_sim_df(valid_candidate, review_year):

    sim_df = (
        valid_candidate[
            ['assignment_id', review_year,
             'mnemonic', 'kV', 'feeder_id', 'breaker_id', 'state', 'gm_subzone',
             'substation_name', 'coordinate', 'zone', 'critical_list', 'Load (MW)']
        ]
        .rename(columns={
            "zone": "Zone",
            "assignment_id": "Assignment",
            "critical_list": "Critical Subs",
        })
        .copy()
    )

    sim_df["Critical Subs"] = np.where(
        sim_df["Critical Subs"].isna(), "No", "Yes")

    # Validate review_year column exists
    if review_year not in sim_df.columns:
        raise ValueError(f"Column '{review_year}' not found in data.")

    # Initialize simulation stage column
    sim_df[SIM_STAGE] = sim_df[review_year]

    return sim_df


def update_sim_df_from_editor(sim_df, editor_state, review_year):
    row_map = st.session_state.get(f"_row_map_{review_year}", {})
    edited_rows = editor_state.get("edited_rows", {})

    if not row_map or not edited_rows:
        return sim_df

    updated_df = sim_df.copy()

    for row_idx, changes in edited_rows.items():
        assignment = row_map.get(row_idx)
        if assignment and SIM_STAGE in changes:
            updated_df.loc[
                updated_df["Assignment"] == assignment,
                SIM_STAGE
            ] = changes[SIM_STAGE]
    editor_state["edited_rows"] = {}
    return updated_df


def render_conflict_block(rows, ls_assign_mlist, label, ref_stage_col):
    with st.status(label=label, state="error", expanded=True):
        for _, row in rows.iterrows():
            assignment = row["Assignment"]
            stage = row[ref_stage_col]
            with st.expander(f"**{assignment}** ({stage})", icon="⚠️"):
                render_conflict_details(
                    row, assignment, ls_assign_mlist, ref_stage_col)


def render_conflict_details(row, assignment, ls_assign_mlist, ref_stage_col):

    display_type = "Simulator Stage" if ref_stage_col == SIM_STAGE else "Operating Stage"

    col1, col2 = st.columns([2, 1])

    with col1:
        assignment_df = ls_assign_mlist.loc[
            ls_assign_mlist["assignment_id"] == assignment
        ]

        subs_name = assignment_df.groupby(
            [
                "mnemonic",
                "substation_name",
                "gm_subzone",
                "zone",
                "state",
                "critical_list",
                "short_text",
            ],
            as_index=False,
            dropna=False,
        ).agg({
            "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
            "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
        })

        # Build substation & flag text
        if len(subs_name) == 1:
            substation_name = subs_name["substation_name"].iloc[0]
            short_text = subs_name["short_text"].iloc[0]
            flag_text = f"{substation_name} ({short_text})"

        else:
            critical_subs = subs_name.loc[
                subs_name["critical_list"].notna()
            ]

            if not critical_subs.empty:
                substation_name = ", ".join(
                    critical_subs["substation_name"].astype(str).unique()
                )

                flag_text = ", ".join(
                    critical_subs.apply(
                        lambda x: f"{x['substation_name']} ({x['short_text']})",
                        axis=1,
                    )
                )
            else:
                substation_name = "N/A"
                flag_text = "N/A"

        st.write(f"**Substation:** {substation_name}")
        st.write(f"**Zone:** {row.get('Zone', 'N/A')}")
        st.write(f"**Assignment:** {assignment}")
        st.write(f"**{display_type}:** {row.get(ref_stage_col, 'N/A')}")
        st.write(f"**Load:** {row.get('Load (MW)', 'N/A')} MW")

    with col2:
        flag = row.get("Flag", "N/A")

        if flag.startswith("Warning"):
            if "Critical Sub" in str(flag):
                st.error(f"**Flag:** {flag} – {flag_text}")
            else:
                st.error(f"**Flag:** {flag}")

        elif flag.startswith("Alert"):
            if "Critical Sub" in str(flag):
                st.warning(f"**Flag:** {flag} – {flag_text}")
            else:
                st.warning(f"**Flag:** {flag}")
