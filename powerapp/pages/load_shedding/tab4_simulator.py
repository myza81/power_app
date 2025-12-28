import pandas as pd
import streamlit as st
from pages.load_shedding.helper import join_unique_non_empty
from pages.load_shedding.tab4a_sim_dashboard import sim_dashboard


def simulator():
    st.subheader("Load Shedding Assignment Simulator")

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

    c1, c2 = st.columns(2)

    with c1:
        review_year = st.selectbox(
            "Base Reference",
            options=scheme_cols,
            key="sim_review_year"
        )

    sim_key = f"sim_data_{review_year}"

    if sim_key not in st.session_state:
        sim_df, valid_candidate, raw_candidate = build_master_sim_df(
            ls_obj, review_year)

        st.session_state[sim_key] = {
            "sim_df": sim_df,
            "raw_candidate": raw_candidate,
        }

    master_df = st.session_state[sim_key]["sim_df"]

    raw_candidate = st.session_state[sim_key]["raw_candidate"]

    with c2:
        zone_options = sorted(master_df["Zone"].dropna().unique())
        selected_zones = st.multiselect(
            "Filter by Zone",
            options=zone_options,
            key=f"zone_filter_{review_year}",
        )
    editor_key = f"assignment_simulator_{review_year}"

    if editor_key in st.session_state:
        editor_state = st.session_state[editor_key]
        if editor_state.get("edited_rows"):
            update_master_from_editor(master_df, editor_state, review_year)

    view_df = master_df.copy()

    if selected_zones:
        view_df = view_df[view_df["Zone"].isin(selected_zones)]

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

    editor_container = st.container()
    result_container = st.container()

    with editor_container:
        edited_df = st.data_editor(
            view_df[
                ["Zone", "Assignment", review_year,
                    "Simulator Operating Stage", "Load (MW)", "Flag"]
            ],
            key=editor_key,
            hide_index=True,
            width='stretch',
            column_config={
                "Simulator Operating Stage": st.column_config.SelectboxColumn(
                    "Simulator Operating Stage",
                    options=stage_options,
                    help="Select the operating stage",
                ),
                "Zone": st.column_config.Column(disabled=True),
                "Assignment": st.column_config.Column(disabled=True),
                review_year: st.column_config.Column(
                    f"Reference: {review_year}", disabled=True
                ),
                "Load (MW)": st.column_config.Column(disabled=True),
                "Flag": st.column_config.Column(disabled=True),
            },
        )

        if editor_key in st.session_state:
            editor_state = st.session_state[editor_key]

            if "edited_rows" in editor_state or "added_rows" in editor_state:
                update_master_from_editor(master_df, editor_state, review_year)

    with result_container:
        sim_dashboard(simulator_df=master_df,
                      candidate_df=raw_candidate, scheme=review_year[:4])


def build_master_sim_df(ls_obj, review_year):
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
    join_cols = scheme_cols + ["mnemonic", "kV", "feeder_id", "breaker_id",
                               "state", "gm_subzone", "substation_name", "coordinate", "zone", "critical_list", "scheme"]
    sum_cols = ["Load (MW)"]
    agg_dict = (
        {col: join_unique_non_empty for col in join_cols}
        | {col: "sum" for col in sum_cols}
    )

    raw_candidate = (
        pd.merge(masterlist, scheme_map, on="assignment_id", how="left")
        .pipe(lambda df: pd.concat([df, incomer], ignore_index=True, sort=False))
        .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
    )

    valid_candidate = raw_candidate.groupby(
        grp_cols, dropna=False).agg(agg_dict).reset_index()

    # valid_candidate = (
    #     pd.merge(masterlist, scheme_map, on="assignment_id", how="left")
    #     .pipe(lambda df: pd.concat([df, incomer], ignore_index=True, sort=False))
    #     .drop_duplicates(subset=["feeder_id", "assignment_id", "local_trip_id"])
    #     .groupby(grp_cols, dropna=False)
    #     .agg(agg_dict)
    #     .reset_index()
    # )

    valid_candidate = valid_candidate[
        valid_candidate["scheme"].str.lower() != "emls"
    ]

    sim_df = (
        valid_candidate[["zone", "assignment_id",
                         review_year, "critical_list", "Load (MW)"]]
        .rename(columns={
            "zone": "Zone",
            "assignment_id": "Assignment",
            "critical_list": "Flag",
        })
        .copy()
    )

    sim_df["Flag"] = sim_df["Flag"].where(
        sim_df["Flag"].isna(), "Critical List"
    )

    if review_year not in sim_df.columns:
        raise ValueError(f"Column '{review_year}' not found in data.")

    sim_df["Simulator Operating Stage"] = sim_df[review_year]

    return sim_df, valid_candidate, raw_candidate


def update_master_from_editor(master_df, editor_state, review_year):

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

        if "Simulator Operating Stage" in changes:
            new_stage = changes["Simulator Operating Stage"]

            master_df.loc[
                master_df["Assignment"] == assignment,
                "Simulator Operating Stage"
            ] = new_stage

    editor_state["edited_rows"] = {}
