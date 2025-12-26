import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from applications.load_shedding.ufls_setting import UFLS_SETTING
from pages.load_shedding.helper import find_latest_assignment
from applications.load_shedding.helper import scheme_col_sorted


def loadshedding_subset():

    loadshedding = st.session_state["loadshedding"]
    masterlist_ls = loadshedding.ls_assignment_masterlist()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    lshedding_columns = [
        col
        for col in masterlist_ls.columns
        if any(keyword in col for keyword in LS_SCHEME)
    ]

    col1, col2, col3 = st.columns(3)

    with col1:
        ref_scheme = st.selectbox(
            label="Reference Load Shedding Scheme",
            options=lshedding_columns,
            key="ls_subset",
        )

    clean_masterlist = masterlist_ls.replace(["nan", "#na"], np.nan)
    # ref_scheme_rename = f"{ref_scheme} (MW)"
    ref_ls = clean_masterlist[[ref_scheme, "Pload (MW)"]]
    clean_ref_ls = ref_ls.loc[ref_ls[ref_scheme].notna()]
    # .rename(
    #     columns={"Pload (MW)": ref_scheme_rename}
    # )
    # clean_ref_ls = ref_ls.loc[ref_ls[ref_scheme].notna()]
    clean_ref_ls_mw = clean_ref_ls.groupby(
        [ref_scheme], as_index=False, dropna=False
    ).agg({"Pload (MW)": "sum"})

    balanced_col_name = f"Balanced {ref_scheme} (MW)"
    clean_ref_ls_mw[balanced_col_name] = clean_ref_ls_mw["Pload (MW)"]

    scheme_prefix = str(ref_scheme).split("_")[0]
    lastest_assignment = find_latest_assignment(lshedding_columns)

    loadshedd_df = clean_masterlist[
        [ref_scheme, "local_trip_id", "assignment_id"]
    ].copy()
    loadshedd_df.rename(
        columns={"assignment_id": f"{ref_scheme}_assignment_id"}, inplace=True
    )

    scheme_mw_col = [f"Balanced {ref_scheme} (MW)"]
    for ls_scheme in lastest_assignment:
        if scheme_prefix in ls_scheme:
            continue

        pd_df = clean_masterlist[
            [ls_scheme, "local_trip_id", "assignment_id", "Pload (MW)"]
        ]
        valid_df = pd_df.loc[pd_df[ls_scheme].notna()]
        merging_df = pd.merge(valid_df, loadshedd_df, on="local_trip_id", how="left")

        merging_df_grp = (
            merging_df.groupby([ref_scheme])
            .agg(
                {
                    "Pload (MW)": "sum",
                    ls_scheme: lambda x: ", ".join(x.astype(str).unique()),
                    "assignment_id": lambda x: ", ".join(x.astype(str).unique()),
                    "local_trip_id": lambda x: ", ".join(x.astype(str).unique()),
                    f"{ref_scheme}_assignment_id": lambda x: ", ".join(
                        x.astype(str).unique()
                    ),
                }
            )
            .reset_index()
        )
        ls_scheme_col_rename = f"{ls_scheme} (MW)"
        merging_df_grp.rename(
            columns={
                "Pload (MW)": ls_scheme_col_rename,
                "local_trip_id": f"{ls_scheme}_local_trip_id",
                f"{ref_scheme}_assignment_id": f"{ls_scheme}_{ref_scheme}_assignment_id",
            },
            inplace=True,
        )

        clean_ref_ls_mw = pd.merge(
            clean_ref_ls_mw, merging_df_grp, on=ref_scheme, how="left"
        )

        clean_ref_ls_mw[balanced_col_name] = np.maximum(
            0,
            clean_ref_ls_mw[balanced_col_name]
            - clean_ref_ls_mw[ls_scheme_col_rename].fillna(0),
        )

        scheme_mw_col.append(ls_scheme_col_rename)

    # st.dataframe(clean_ref_ls_mw)

    df_melted = clean_ref_ls_mw[
        [ref_scheme] + scheme_mw_col
    ].melt(
        id_vars=[ref_scheme],
        value_vars=scheme_mw_col,
        var_name="scheme",
        value_name="Quantum (MW)",
    )

    df_melted = scheme_col_sorted(df_melted, str(ref_scheme))
    # st.dataframe(df_melted)

    color = ["#DFE6E3", "#F06B33", "#E359A0"]
    result = dict(zip(scheme_mw_col, color))

    fig_shed = px.bar(
        df_melted,
        x=ref_scheme,
        y="Quantum (MW)",
        color="scheme",
        color_discrete_map=result,
        title=f"{ref_scheme}",
    )

    fig_shed.update_layout(
        title={"font": {"size": 18, "family": "Arial"}, "x": 0.5, "xanchor": "center"},
        height=450,
        width=600,
        legend_title_text="",
        xaxis_title=None,
        yaxis_title="Load Shedding Quantum (MW)",
    )

    st.plotly_chart(fig_shed, width="content")
