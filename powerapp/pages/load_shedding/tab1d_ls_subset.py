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
    ref_ls = clean_masterlist[[ref_scheme, "Pload (MW)"]]
    clean_ref_ls = ref_ls.loc[ref_ls[ref_scheme].notna()]
    clean_ref_ls_mw = clean_ref_ls.groupby(
        [ref_scheme],
        as_index=False,
        dropna=False
    ).agg({"Pload (MW)": "sum"})

    scheme = ref_scheme.split("_")[0]
    lastest_assignment = find_latest_assignment(lshedding_columns)

    loadshedd_df = clean_masterlist[[ref_scheme, "local_trip_id", "assignment_id"]].rename(
        columns={"assignment_id": f"{ref_scheme}_assignment_id"})

    for ls_scheme in lastest_assignment:
        if any(keyword not in ls_scheme for keyword in scheme):

            pd_df = clean_masterlist[
                [ls_scheme, "local_trip_id", "assignment_id", "Pload (MW)"]
            ]
            valid_df = pd_df.loc[pd_df[ls_scheme].notna()]
            merging_df = pd.merge(
                valid_df,
                loadshedd_df,
                on="local_trip_id",
                how="left"
            ).dropna()

            merging_df_grp = merging_df.groupby(
                [ref_scheme]
            ).agg({
                "Pload (MW)": "sum",
                ls_scheme: lambda x: ", ".join(x.astype(str).unique()),
                "assignment_id": lambda x: ", ".join(x.astype(str).unique()),
                "local_trip_id": lambda x: ", ".join(x.astype(str).unique()),
                f"{ref_scheme}_assignment_id": lambda x: ", ".join(x.astype(str).unique()),
            }).reset_index()

            merging_df_grp = (
                merging_df_grp[[
                    ref_scheme, "Pload (MW)", ls_scheme, "local_trip_id", f"{ref_scheme}_assignment_id"]]
                .rename(columns={
                    "Pload (MW)": f"{ls_scheme}_mw",
                    "local_trip_id": f"{ls_scheme}_local_trip_id",
                    f"{ref_scheme}_assignment_id": f"{ls_scheme}_{ref_scheme}_assignment_id"
                })
            )

            clean_ref_ls_mw = pd.merge(
                clean_ref_ls_mw,
                merging_df_grp,
                on=ref_scheme,
                how="left"
            )

    # df_melted = clean_ref_ls_mw.melt(
    #     id_vars=[ref_scheme],
    #     value_vars=["Critical Load", "Non-critical Load", ],
    #     var_name="Type",
    #     value_name="Quantum (MW)"
    # )
    # df_melted = scheme_col_sorted(df_melted, scheme)

    st.dataframe(clean_ref_ls_mw)

    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset Bar</p>",
        unsafe_allow_html=True,
    )

    # st.dataframe(ls_subset)
    col1, col2, col3 = st.columns([2, 0.1, 2])

    with col1:
        bar_subset()
    with col3:
        circle_subset()


def bar_subset():
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset </p>",
        unsafe_allow_html=True,
    )


def circle_subset():
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset </p>",
        unsafe_allow_html=True,
    )
