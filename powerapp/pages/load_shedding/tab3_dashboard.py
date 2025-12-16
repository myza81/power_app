import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
from applications.load_shedding.helper import (
    column_data_list, scheme_col_sorted)


def critical_list_dashboard(data):
    loadshedding = st.session_state["loadshedding"]
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    review_year = data.get("review_year")
    selected_ls_scheme = data.get("selected_ls_scheme")
    overlap_list = data.get("overlap_list")
    masterlist_ls = data.get("masterlist_ls")

    st.markdown(
        f'<span style="color: inherit; font-size: 20px; font-weight: 600"> Distributions of Overlap Critical Load List with Existing Load Shedding Scheme:</span>',
        unsafe_allow_html=True
    )

    if selected_ls_scheme:
        ls_cols = [
            col
            for col in overlap_list.columns
            if any(keyword in col for keyword in LS_SCHEME)
        ]
        
        selected_scheme = [
            f"{scheme}_{review_year}" for scheme in selected_ls_scheme
        ]

        valid_ls_cols = [
            ls_review
            for ls_review in selected_scheme
            if ls_review in overlap_list.columns
        ]
       
        for ls_review in valid_ls_cols:
            col1, col2 = st.columns([2, 3])

            df_list = masterlist_ls[
                [ls_review, "critical_list", "assignment_id", "Pload (MW)"]
            ].copy()

            df_list[ls_review] = df_list[ls_review].replace(
                ["nan", "#na"], np.nan)
            filtered_df = df_list.dropna()

            quantum_ls_stg = (
                filtered_df[[ls_review, "Pload (MW)"]]
                .groupby([ls_review])
                .agg({"Pload (MW)": "sum"})
            )

            quantum_ls_stg.rename(
                columns={"Pload (MW)": "Load Shed Quantum MW"}, inplace=True
            )

            quantum_critical_list = filtered_df.groupby(["assignment_id"]).agg(
                {
                    "Pload (MW)": "sum",
                    "critical_list": lambda x: ", ".join(x.astype(str).unique()),
                    ls_review: lambda x: ", ".join(x.astype(str).unique()),
                }
            )
            quantum_critical_list["critical_list"] = quantum_critical_list[
                "critical_list"
            ].replace(["nan", "#na"], np.nan)
            filtered_critical_stg = quantum_critical_list.dropna()
            quantum_critical_stg = (
                filtered_critical_stg[[ls_review, "Pload (MW)"]]
                .groupby([ls_review])
                .agg({"Pload (MW)": "sum"})
            )

            quantum_critical_stg.rename(
                columns={"Pload (MW)": "Critical List MW"}, inplace=True
            )

            summary_overlap = pd.merge(
                quantum_ls_stg, quantum_critical_stg, on=ls_review, how="left"
            ).reset_index()

            sorted_df = scheme_col_sorted(summary_overlap, ls_review)

            with col1:
                st.dataframe(sorted_df, hide_index=True)

            with col2:
                pass

            st.divider()

def overlap_critical_list():
