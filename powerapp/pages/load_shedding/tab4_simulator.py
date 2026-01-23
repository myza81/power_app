import re
import pandas as pd
import numpy as np
import streamlit as st
from pages.load_shedding.helper import join_unique_non_empty
from pages.load_shedding.tab4b_sim_dashboard import sim_dashboard
from pages.load_shedding.tab4a_sim_conflict import conflict_assignment
from pages.load_shedding.tab4c_sim_save import save_sim_data, col_sim_validation
from applications.load_shedding.helper import scheme_col_sorted
from css.streamlit_css import custom_metric, custom_metric_one_line, custom_metric_two_line, scrollable_text_area, scrollable_text_box

SIM_STAGE = "Sim. Stage"


def simulator():
    st.subheader("Load Shedding Assignment Simulator")

    input_container = st.container()
    editor_container = st.container()
    save_sim_container = st.container()
    alarm_container = st.container()
    dashboard_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
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
        input_box, _, textarea = st.columns([3, 0.01, 1.2])

        with input_box:
            base_rev, sim_rev = st.columns(2)
            filter_zone, assign_find = st.columns(2)

        with base_rev:
            base_scheme = st.selectbox(
                "Base Reference",
                options=scheme_cols,
                key="base_review_year"
            )
        with sim_rev:
            sim_scheme = st.selectbox(
                "Simulator Base",
                options=scheme_cols,
                key="sim_review_year"
            )

        master_df_key = f"master_df_key_{base_scheme}_{sim_scheme}"
        sim_key = f"sim_data_{base_scheme}_{sim_scheme}"
        editor_key = f"sim_editor_{base_scheme}_{sim_scheme}"
        export_sim_key = f"show_export_{base_scheme}_{sim_scheme}"

        df_raw_cand, _, _ = potential_ls_candidate(ls_obj)

        if export_sim_key not in st.session_state:
            st.session_state[export_sim_key] = False

        if master_df_key not in st.session_state:

            st.session_state[master_df_key] = {
                "raw_candidate": df_raw_cand,
                "master_df": generate_sim_df(df_raw_cand, base_scheme, sim_scheme),
            }

        raw_candidate = st.session_state[master_df_key]["raw_candidate"]
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
                    sim_df, current_editor_state, base_scheme
                )

            sim_data["last_editor_state"] = current_editor_state.copy()
            st.session_state[export_sim_key] = False

        sim_df = conflict_assignment(
            sim_df, ls_obj, base_scheme, SIM_STAGE)

        sim_data["sim_df"] = sim_df

        with filter_zone:
            zone_options = sorted(sim_df["Zone"].dropna().unique())
            selected_zones = st.multiselect(
                "Filter by Zone",
                options=zone_options,
                key=f"zone_filter_{base_scheme}",
            )

        with assign_find:
            assignment_list = sim_df["Assignment"].tolist()
            assignment_id = st.multiselect(
                label="Assignment Finder",
                options=assignment_list,
                key=f"subs_search_{base_scheme}",
            )

        with textarea:
            all_texts = []
            for item in assignment_id:
                subs_meta = df_raw_cand.loc[df_raw_cand["assignment_id"] == item]

                if not subs_meta.empty:
                    df = subs_meta.groupby(
                        ["state", "zone", "gm_subzone", "mnemonic",
                            "dp_type", "kV", "substation_name", "coordinate"],
                        as_index=False,
                        dropna=False
                    ).agg({
                        "Load (MW)": "sum",
                        "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
                        "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
                    })

                if not df.empty:
                    for _, row in df.iterrows():
                        state = row["state"]
                        zone = row["zone"]
                        subs_name = row["substation_name"]
                        mnemonic = row["mnemonic"]
                        dp_type = row["dp_type"]
                        feeder = row["feeder_id"]
                        mw = row["Load (MW)"]
                        kv = row["kV"]

                        text = (
                            f"Assignment ID: {item}\n"
                            f"Zone: {zone} | State: {state}\n"
                            f"Substation: {subs_name} ({kv}kV)\n"
                            f"Mnemonic: {mnemonic}\n"
                            f"Type: {dp_type}\n"
                            f"Feeders: {feeder}\n"
                            f"Total Load: {mw:.1f} MW\n"
                            f"{'-' * 50}\n"
                        )
                        all_texts.append(text)

            combined_text = "".join(all_texts)

            if combined_text:
                st.write("📂 Assignment Information:")
                scrollable_text_box(
                    text=combined_text,
                    height=110,
                    bg_color="#C8C8C8",
                    text_color="#2D2D2F",
                    font_size="13px"
                )

        view_df = sim_df.copy()
        if selected_zones:
            view_df = view_df[view_df["Zone"].isin(selected_zones)]

        if assignment_id:
            view_df = view_df[view_df["Assignment"].isin(assignment_id)]

        if base_scheme.startswith("UFLS"):
            stage_options = ls_obj.ufls_setting.columns.tolist()
        elif base_scheme.startswith("UVLS"):
            stage_options = ls_obj.uvls_setting.columns.tolist()
        else:
            stage_options = []

        row_map_key = f"_row_map_{base_scheme}"
        st.session_state[row_map_key] = (
            view_df["Assignment"]
            .reset_index(drop=True)
            .to_dict()
        )

    with editor_container:
        editor_table, _, metrics = st.columns([3, 0.01, 1.2])

        with editor_table:
            # st.write(view_df)
            cols_to_show = ["Zone", "Assignment", base_scheme,
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
                    base_scheme: st.column_config.Column(
                        f"Ref.: {base_scheme}", disabled=True
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
                    key=f"simls_colname_{base_scheme}",
                    help="Enter 4-digit year (2025) for final, or add version like 2025v1 for drafts"
                )

            with save:
                button_disabled = col_sim_validation(ls_colname)
                df_sim = sim_df[["Assignment", SIM_STAGE]]
                df_sim = df_sim.rename(
                    columns={"Assignment": "assignment_id", SIM_STAGE: ls_colname})

                st.button(
                    label="💾 Save",
                    disabled=button_disabled,
                    on_click=save_sim_data,
                    args=(df_sim, ls_colname, base_scheme,
                          save_sim_container),
                    key=f"save_sim_{base_scheme}",
                    width='stretch',
                    help="Invalid format! Please use format e.g., 2025 or 2025v1" if button_disabled else ""
                )

            with reset:
                st.button(
                    label="🔄 Reset",
                    on_click=reset_to_base_reference,
                    args=(master_df, sim_key),
                    key=f"reset_to_base_{base_scheme}",
                    width='stretch',
                )

            with empty:
                st.button(
                    label="🧹 Clear",
                    on_click=reset_to_empty_sim_df,
                    args=(sim_df, sim_key),
                    key=f"reset_to_empty_{base_scheme}",
                    width='stretch',
                )

        with metrics:
            display_simulation_metrics(
                sim_df, raw_candidate, ls_obj, base_scheme)

    with alarm_container:
        display_conflicts(view_df, ls_obj, ref_stage_col=SIM_STAGE)

    with dashboard_container:
        sim_dashboard(simulator_df=sim_df,
                      candidate_df=raw_candidate,
                      scheme=base_scheme[:4])


def reset_to_empty_sim_df(sim_df, sim_key):
    cleared_df = sim_df.copy()
    cleared_df[SIM_STAGE] = None
    cleared_df["conflict_assignment"] = ""

    st.session_state[sim_key]["sim_df"] = cleared_df


def reset_to_base_reference(master_df, sim_key):
    st.session_state[sim_key]["sim_df"] = master_df.copy()


def display_simulation_metrics(sim_df, raw_candidate, ls_obj, base_scheme):

    load_df = ls_obj.loadprofile_df()

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
        key=f"sim_oper_stage_{base_scheme}"
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
        totalMW = load_df["Load (MW)"].sum()
        pct = (quantum_val / totalMW * 100) if totalMW > 0 else 0

        # Display metric
        custom_metric(
            label=f"{oper_stage.title()} Quantum:",
            value1=f"{quantum_val:,.0f}MW",
            value2=f"<span style='font-size: 14px;'>({pct:,.1f}% of {totalMW:,.0f}MW)</span>",
        )

        # st.markdown("**Zone Breakdown:**")
        for zone in sim_ls["zone"].dropna().unique().tolist():
            sim_zone = stg_quantum.loc[stg_quantum["zone"] == zone]
            sim_zone_stg = sim_zone.loc[sim_zone[SIM_STAGE]
                                        == oper_stage]
            mw_zone_stg = sim_zone_stg["Load (MW)"].values[0] if not sim_zone_stg.empty else 0

            zone_load = ls_obj.zone_load_profile(zone)
            zone_load_pct = (mw_zone_stg / zone_load *
                             100) if zone_load > 0 else 0

            custom_metric_two_line(
                title=f"",
                values_obj1={
                    f"🇱🇷 {zone}": f"{mw_zone_stg:,.0f}MW",
                },
                values_obj2={
                    f"": f"({zone_load_pct:,.1f}% of {zone_load:,.0f}MW)",
                },
                title_size="18px",
                item_color="#6b7280",
                item_size="14px",
                item_weight=700,
                value1_size="15px",
                value1_weight=700,
                value1_color="#2E86C1",
                value2_size="14px",
                value2_weight=700,
                value2_color="#6b7280",
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


def potential_ls_candidate(ls_obj):
    masterlist = ls_obj.ls_assignment_masterlist().copy()
    incomer = ls_obj.incomer_relay()

    id_col = incomer["local_trip_id"].fillna("na").astype(str)
    conditions = [
        id_col.str.contains("132|275"),
        id_col.str.contains("230"),
        id_col.str.contains("11|22|33"),
        id_col.str.contains("na"),
    ]
    choices = ["LPC", "Interconnector", "Local_Load", ""]

    incomer["dp_type"] = np.select(conditions, choices, default="Pocket")

    ls_cols = [
        col for col in masterlist.columns
        if str(col).lower().startswith(tuple(k.lower() for k in ls_obj.LOADSHED_SCHEME))
    ]

    auto_ls_cols = [
        col for col in ls_cols if not str(col).lower().startswith('emls')
    ]

    auto_ls_master = masterlist.dropna(subset=auto_ls_cols, how="all")
    required_cols = ["assignment_id", "local_trip_id", "state", "zone",
                     "gm_subzone", "mnemonic", "critical_list", "dp_type", 'kV', 'breaker_id', 'substation_name', 'coordinate']

    df_all = pd.merge(
        auto_ls_master,
        incomer,
        on=required_cols + ["Load (MW)", "feeder_id"],
        how="outer"
    )

    df_raw_cand = df_all.groupby(
        ls_cols + required_cols,
        dropna=False,
        as_index=False
    ).agg({
        "Load (MW)": "sum",
        "feeder_id": lambda x: ", ".join(x.astype(str).unique())
    })

    critical_list = df_raw_cand.loc[df_raw_cand["critical_list"].notna()]
    critical_assign_ids = critical_list["assignment_id"].unique().tolist()

    cand_with_crit = df_raw_cand.loc[df_raw_cand["assignment_id"].isin(
        critical_assign_ids)]

    cand_without_crit = df_raw_cand.loc[
        ~df_raw_cand["assignment_id"].isin(critical_assign_ids)
    ]

    return df_raw_cand, cand_with_crit, cand_without_crit


def generate_sim_df(df, base_scheme, sim_scheme):

    sim_review_cols = [base_scheme, sim_scheme]

    for col in sim_review_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in dataframe. "
                             f"Available columns: {list(df.columns)}")

    sim_review_cols = list(set(sim_review_cols))

    group_cols = ["assignment_id"]
    sum_cols = ["Load (MW)"]

    all_cols = set(df.columns)
    sum_group_cols = set(sum_cols + group_cols)
    join_cols = list(all_cols - sum_group_cols)

    agg_dict = {}
    for col in join_cols:
        agg_dict[col] = join_unique_non_empty
    for col in sum_cols:
        agg_dict[col] = "sum"

    df = df.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

    rename_dict = {
        "zone": "Zone",
        "assignment_id": "Assignment",
        "critical_list": "Critical Subs",
    }

    sim_df = df.rename(columns={k: v for k, v in rename_dict.items()
                                if k in df.columns})

    if "Critical Subs" in sim_df.columns:
        sim_df["Critical Subs"] = np.where(
            sim_df["Critical Subs"].isna() |
            (sim_df["Critical Subs"].astype(
                str).str.strip().isin(["", "nan", "NaN"])),
            "No", "Yes"
        )

    sim_df[SIM_STAGE] = sim_df[sim_scheme]

    return sim_df


def update_sim_df_from_editor(sim_df, editor_state, base_scheme):
    row_map = st.session_state.get(f"_row_map_{base_scheme}", {})
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
    with st.status(label=label, state="error", expanded=False):
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
        st.write(f"**State:** {row.get('state', 'N/A')}")
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
