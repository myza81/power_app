import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from applications.load_shedding.ufls_setting import UFLS_SETTING
from pages.load_shedding.helper import find_latest_assignment


def loadshedding_subset():

    loadshedding = st.session_state["loadshedding"]
    masterlist_ls = loadshedding.ls_assignment_masterlist()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    lshedding_columns = [
        col
        for col in masterlist_ls.columns
        if any(keyword in col for keyword in LS_SCHEME)
    ]

    lastest_assignment = find_latest_assignment(lshedding_columns)

    col1, col2, col3 = st.columns(3)

    with col1:
        ref_scheme = st.selectbox(
            label="Reference Load Shedding Scheme",
            options=lshedding_columns,
            key="ls_subset",
        )

    scheme = ref_scheme.split("_")[0]

    ref_ls = masterlist_ls[[ref_scheme, "local_trip_id", "assignment_id", "Pload (MW)"]].replace(["nan"], np.nan)
    valid_ref_ls = ref_ls.loc[ref_ls[ref_scheme].notna()]

    # st.dataframe(valid_ref_ls)

    for ls_scheme in lastest_assignment:
        if any(keyword not in ls_scheme for keyword in scheme):
            pd_df = masterlist_ls[
                [ls_scheme, "local_trip_id", "assignment_id", "Pload (MW)"]
            ].replace(["nan", "#na"], np.nan)
            valid_df = pd_df.loc[pd_df[ls_scheme].notna()]
            valid_df = valid_df.rename(
                columns={
                    "Pload (MW)": f"{ls_scheme}_mw",
                    "assignment_id": f"{ls_scheme}_assignment_id",
                }
            )
            valid_ref_ls = pd.merge(valid_ref_ls, valid_df, on="local_trip_id", how="left")

    st.dataframe(valid_ref_ls)

    quantum = valid_ref_ls.groupby(
        [scheme],
        as_index=False,
        dropna=False,
    ).agg(
        {
            "Pload (MW)": "sum",
            "local_trip_id": lambda x: ", ".join(x.astype(str).unique()),
            "assignement_id": lambda x: ", ".join(x.astype(str).unique()),
            
        }
    )

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
