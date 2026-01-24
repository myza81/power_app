import streamlit as st
import numpy as np
from pages.load_shedding.helper import find_latest_assignment, join_unique_non_empty
from pages.load_shedding.tab4_simulator import display_conflicts, potential_ls_candidate
from pages.load_shedding.tab4a_sim_conflict import raise_flags


def ls_assignment_flag():
    st.subheader("Load Shedding Assignment Flags / Warnings")

    input_container = st.container()
    alarm_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    master_df = ls_obj.ls_assignment_masterlist().copy()
    df_raw_cand, _, _ = potential_ls_candidate(ls_obj)

    scheme_cols = [
        c for c in master_df.columns if any(k in c for k in ls_obj.LOADSHED_SCHEME)
    ]

    with input_container:
        input1, _, _ = st.columns(3)

        with input1:
            scheme = st.selectbox(
                "Scheme", options=scheme_cols, key="analytic_flag_scheme"
            )

        lshedding_columns = [
            col
            for col in master_df.columns
            if any(k in col for k in ls_obj.LOADSHED_SCHEME)
            and not col.startswith(scheme[:4])
        ]

        ls_latest_cols = find_latest_assignment(lshedding_columns)

        grp_cols = ["assignment_id"]
        join_cols = scheme_cols + [
            "mnemonic",
            "kV",
            "feeder_id",
            "breaker_id",
            "state",
            "gm_subzone",
            "substation_name",
            "coordinate",
            "zone",
            "critical_list",
        ]
        sum_cols = ["Load (MW)"]

        agg_dict = {col: join_unique_non_empty for col in join_cols} | {
            col: "sum" for col in sum_cols
        }

        df = master_df.groupby(grp_cols, dropna=False).agg(agg_dict).reset_index()

        df = df.rename(columns={"assignment_id": "Assignment", "zone": "Zone"})
        df["Critical Subs"] = np.where(df["critical_list"].isna(), "No", "Yes")

        df_merge = raise_flags(
            df,
            df_raw_cand,
            ls_latest_cols,
            scheme[:4],
            scheme
        )

    with alarm_container:
        display_conflicts(df_merge, ls_obj, ref_stage_col=scheme)
