import streamlit as st
from applications.load_shedding.helper import scheme_col_sorted
from pages.load_shedding.helper import custom_table, find_latest_assignment


def ls_table(df, scheme):
    ls_obj = st.session_state.get("loadshedding")

    if ls_obj is None:
        return

    ls_oper_zone = df[[scheme, "zone", "Load (MW)"]].groupby(
        [scheme, "zone"],
        as_index=False,
    ).agg({"Load (MW)": "sum"})
    ls_sorted = scheme_col_sorted(ls_oper_zone, scheme)

    flaglist = df.loc[df["critical_list"].notna()].copy()

    c1, _, c2, _, c3 = st.columns([2, 0.2, 2, 0.2, 2])

    with c1:
        ls_table = ls_sorted[[scheme, "Load (MW)"]].groupby(
            [scheme],
            as_index=False
        ).agg({"Load (MW)": "sum"})

        ls_table["Load (MW)"] = ls_table["Load (MW)"].round().astype(int)

        ls_table = scheme_col_sorted(ls_table, scheme)
        html_ls_table = ls_table.to_html(
            index=False, classes="custom-table", escape=False)

        custom_table(
            table_title=f"{scheme} Operating Staging and Load Quantum Table:", table_content=html_ls_table)

    with c2:
        flaglist_table = flaglist[["assignment_id", scheme, "mnemonic"]].groupby(
            [scheme],
            as_index=False
        ).agg({
            "assignment_id": lambda x: ", ".join(x.astype(str).unique()),
            "mnemonic": lambda x: ", ".join(x.astype(str).unique()),
        }).rename(columns={"mnemonic": "Substation(s)", "assignment_id": "Assignments"})[[scheme, "Substation(s)", "Assignments"]]

        flaglist_table = scheme_col_sorted(flaglist_table, scheme)
        html_flaglist_table = flaglist_table.to_html(
            index=False, classes="custom-table", escape=False)

        custom_table(
            table_title=f"{scheme} Overlaps With Critical Substation Table:", table_content=html_flaglist_table)

    with c3:

        masterlist = ls_obj.ls_assignment_masterlist()

        lshedding_columns = [
            col for col in masterlist.columns
            if any(k in col for k in ls_obj.LOADSHED_SCHEME)
            and not col.startswith(scheme[:4])
        ]

        latest_assignment = find_latest_assignment(lshedding_columns)

        scheme_cols = list([scheme]+latest_assignment)
        group_keys = ["assignment_id", "mnemonic"]
        all_cols = list(group_keys + scheme_cols)

        agg_dict = {col: join_unique_non_empty for col in scheme_cols}

        selected_df = (
            masterlist[all_cols]
            .groupby(group_keys, as_index=False, dropna=False)
            .agg(agg_dict)
        )

        selected_df = selected_df.loc[selected_df[scheme].notna()]

        overlap_ls = selected_df.dropna(
            subset=latest_assignment, how='all').reset_index(drop=True)

        overlap_ls = overlap_ls[all_cols].rename(
            columns={"assignment_id": "Assignment", "mnemonic": "Substation"})

        overlap_ls_table = scheme_col_sorted(overlap_ls, scheme)
        overlap_ls_table = overlap_ls_table.replace({None: ""})

        html_overlap_ls_table = overlap_ls_table.to_html(
            index=False, classes="custom-table", escape=False, na_rep="")

        custom_table(
            table_title=f"{scheme} Overlaps With Other Load Shedding Table:", table_content=html_overlap_ls_table)


def join_unique_non_empty(series):
    unique_vals = [str(v) for v in series.dropna().unique() if str(v).strip() != ""]
    return ", ".join(unique_vals) if unique_vals else None
