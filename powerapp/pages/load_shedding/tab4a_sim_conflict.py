import re
import pandas as pd
import numpy as np
import streamlit as st
from pages.load_shedding.helper import find_latest_assignment
from collections import defaultdict


def _join_warning(row):
    parts = [p for p in row if p]
    return "Warning: " + " & ".join(parts)


# def raise_flags(df, ls_latest_cols, ref_scheme, SIM_STAGE):
def raise_flags(df, raw_candidate, ls_latest_cols, ref_scheme, SIM_STAGE):

    nonOverlap_ufls_stages = ["stage_1", "stage_2", "stage_3"]
    critical_ufls_stages = [
        "stage_1",
        "stage_2",
        "stage_3",
        "stage_11",
        "stage_12",
        "stage_13",
    ]
    noncritical_ufls_stages = [
        "stage_4",
        "stage_5",
        "stage_6",
        "stage_7",
        "stage_8",
        "stage_9",
        "stage_10",
    ]

    if "conflict_assignment" not in df.columns:
        df["conflict_assignment"] = ""

    # 1. Logic for Overlap Detection
    if ref_scheme == "UFLS":
        stage_mask = df[SIM_STAGE].isin(nonOverlap_ufls_stages)
        has_values_mask = df[ls_latest_cols].notna().any(axis=1)
    else:
        ufls_cols = [
            col
            for col in ls_latest_cols
            if col.startswith("UFLS") and col in df.columns
        ]

        if not ufls_cols:
            return df

        stage_mask = df[ufls_cols[0]].isin(nonOverlap_ufls_stages)
        has_values_mask = df[SIM_STAGE].notna()

    overlap = stage_mask & has_values_mask

    # 2. Extract Overlap Details
    if overlap.any():
        subset = df.loc[overlap, ls_latest_cols]
        df.loc[overlap, "conflict_assignment"] = subset.apply(
            lambda row: "[Overlap] - "
            + ", ".join(
                f"{col} ({val})"
                for col, val in row.dropna().items()
                if str(val).strip() != ""
            ),
            axis=1,
        )

    # 3. Critical Check
    critical_mask = df[SIM_STAGE].isin(critical_ufls_stages) & df[
        "Critical Subs"
    ].str.contains("Yes", na=False)

    alert_critical = df[SIM_STAGE].isin(noncritical_ufls_stages) & df[
        "Critical Subs"
    ].str.contains("Yes", na=False)

    # 4. Pocket & Local assignment overlap
    local_conflicts = detect_local_trip_conflict(
        sim_df=df,
        raw_candidate=raw_candidate,
        sim_stage_col=SIM_STAGE,
    )

    if local_conflicts:
        for assign_id, local_ids in local_conflicts.items():
            msg = ""
            value_to_keys = defaultdict(list)
            for key, values in local_conflicts.items():
                for val in values:
                    value_to_keys[val].append(key)

            for value, keys in value_to_keys.items():
                if len(keys) > 1:
                    keys_str = " and ".join([f'"{k}"' for k in keys])
                    msg = (
                        "[Local Trip Conflict] - "
                        f"Similar load assignment ({value}) with assignment_id: {keys_str}"
                    )

            mask = df["Assignment"] == assign_id

            existing = (
                df.loc[mask, "conflict_assignment"]
                .fillna("")
                .str.strip()
            )

            df.loc[mask, "conflict_assignment"] = np.where(
                existing.eq(""),
                msg,
                np.where(
                    existing.str.contains(re.escape(msg)),
                    existing,
                    existing + " | " + msg
                )
            )

    # 5. Final Flagging (Vectorized approach)
    flag_warning_mask = critical_mask | overlap
    flag_alert_mask = alert_critical

    local_conflict_mask = df["conflict_assignment"].str.contains(
        "Local Trip Conflict", na=False
    )

    flag_warning_mask = flag_warning_mask | local_conflict_mask

    # Default everything to OK
    df["Flag"] = "OK"

    # Update only those that meet the flag_mask
    if flag_warning_mask.any():
        conflict_info = (
            df.loc[flag_warning_mask, "conflict_assignment"].fillna(
                "").str.strip()
        )

        critical_info = np.where(
            critical_mask[flag_warning_mask], "[Critical Sub]", "")

        df.loc[flag_warning_mask, "Flag"] = pd.DataFrame(
            {"a": conflict_info, "b": critical_info}
        ).apply(_join_warning, axis=1)

    if flag_alert_mask.any():
        alert_info = np.where(
            alert_critical[flag_alert_mask], "[Critical Sub]", "")

        df.loc[flag_alert_mask, "Flag"] = "Alert: " + alert_info

    return df


def conflict_assignment(
    sim_df, raw_candidate, ls_obj, base_scheme, SIM_STAGE
):

    if base_scheme[:4] not in ls_obj.LOADSHED_SCHEME:
        return sim_df

    ref_scheme = base_scheme[:4]

    all_ls_columns = [
        col for col in sim_df.columns
        if any(col.startswith(scheme) for scheme in ls_obj.LOADSHED_SCHEME)
    ]

    lshedding_columns = [
        col
        for col in all_ls_columns
        if not col.startswith(ref_scheme)
    ]

    columns_to_keep = set([base_scheme]) | set(lshedding_columns)
    columns_to_drop = set(all_ls_columns) - columns_to_keep

    sim_dataframe = sim_df.copy()
    if columns_to_drop:
        sim_dataframe = sim_dataframe.drop(columns=list(columns_to_drop))

    ls_latest_cols = find_latest_assignment(lshedding_columns)

    df_merge = raise_flags(
        sim_dataframe,
        raw_candidate,
        ls_latest_cols,
        ref_scheme,
        SIM_STAGE
    )

    df_merge = df_merge.drop(columns=ls_latest_cols)

    return df_merge


def detect_local_trip_conflict(
    sim_df: pd.DataFrame,
    raw_candidate: pd.DataFrame,
    sim_stage_col: str,
    assignment_col: str = "Assignment",
    raw_assignment_col: str = "assignment_id",
    local_trip_col: str = "local_trip_id",
):

    active_assignments = sim_df.loc[
        sim_df[sim_stage_col].notna(), assignment_col
    ]

    if active_assignments.empty:
        return {}

    active_raw = raw_candidate[
        raw_candidate[raw_assignment_col].isin(active_assignments)
        & raw_candidate[local_trip_col].notna()
    ]

    if active_raw.empty:
        return {}

    overlapping_local = (
        active_raw
        .groupby(local_trip_col)[raw_assignment_col]
        .nunique()
        .gt(1)
    )

    conflict_local_ids = overlapping_local[overlapping_local].index.tolist()

    if not conflict_local_ids:
        return {}

    conflict_map = {}

    for assign_id, grp in active_raw.groupby(raw_assignment_col):
        conflicted_ids = (
            grp.loc[
                grp[local_trip_col].isin(conflict_local_ids),
                local_trip_col
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        if conflicted_ids:
            conflict_map[assign_id] = conflicted_ids

    return conflict_map
