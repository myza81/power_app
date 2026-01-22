import streamlit as st
import pandas as pd
import numpy as np
from pages.load_shedding.tab4_simulator import potential_ls_candidate
from pages.load_shedding.helper import stage_sort
from pages.load_shedding.helper_chart import (
    create_stackedBar_chart,
    create_groupBar_chart,
    get_dynamic_colors,
)



def critical_list_analytic():
    st.subheader("Critical List Distribution Analysis")

    barchart_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    raw_cand = potential_ls_candidate(ls_obj)

    critical_list = raw_cand.loc[raw_cand["critical_list"].notna()]
    critical_assign_ids = critical_list["assignment_id"].unique().tolist()

    cand_with_crit = raw_cand.loc[raw_cand["assignment_id"].isin(critical_assign_ids)]
    cand_with_crit_zone = cand_with_crit.groupby(
        ["zone"], as_index=False, dropna=False
    ).agg({"Load (MW)": "sum"})

    cand_without_crit = raw_cand.loc[
        ~raw_cand["assignment_id"].isin(critical_assign_ids)
    ]
    cand_without_crit_zone = cand_without_crit.groupby(
        ["zone"], as_index=False, dropna=False
    ).agg({"Load (MW)": "sum"})

    with barchart_container:
        barchart1, barchart2 = st.columns(2)

        with barchart1:
            zone_list = pd.merge(
                cand_with_crit_zone,
                cand_without_crit_zone,
                on="zone",
                how="outer",
                suffixes=("_critical", "_non_critical"),
            ).dropna(subset=["zone"])

            zone_list["Total Potential (MW)"] = zone_list["Load (MW)_critical"].fillna(
                0
            ) + zone_list["Load (MW)_non_critical"].fillna(0)

            zone_list_df = zone_list.rename(
                columns={
                    "Load (MW)_critical": "Critical Load",
                    "Load (MW)_non_critical": "Non_critical Load",
                }
            ).melt(
                id_vars=["zone"],
                value_vars=[
                    "Critical Load",
                    "Non_critical Load",
                    "Total Potential (MW)",
                ],
                var_name="load_type",
                value_name="MW",
            )

            dynamic_color_map = get_dynamic_colors(
                categories=[
                    "Critical Load",
                    "Non_critical Load",
                    "Total Potential (MW)",
                ]
            )
            create_groupBar_chart(
                df=zone_list_df,
                x_col="zone",
                y_col="MW",
                color_col="load_type",
                title="Automatic Load Shedding: Critical vs Non-Critical Load by Zone",
                title_fsize=18,
                title_width=50,
                title_x=0,
                legend_x=0.1,
                legend_y=-0.15,
                lagend_xanchor="left",
                legend_orient="h",
                margin=dict(t=80, b=50, l=40, r=20),
                color_discrete_map={},
                category_order={},
                height=450,
                key=None,
                showlegend=True,
                xaxis_label=None,
                yaxis_label="Load (MW)",
            )

        with barchart2:
            assign_non_list = (
                cand_without_crit.groupby(["zone"], as_index=False, dropna=False)
                .agg({"assignment_id": lambda x: x.nunique()})
                .dropna(subset=["zone"])
            )
            assign_crit_list = (
                cand_with_crit.groupby(["zone"], as_index=False, dropna=False)
                .agg({"assignment_id": lambda x: x.nunique()})
                .dropna(subset=["zone"])
            )

            assign_list = pd.merge(
                assign_non_list,
                assign_crit_list,
                on="zone",
                how="outer",
                suffixes=("_non_critical", "_critical"),
            ).dropna(subset=["zone"])

            assign_list["Total Assignment"] = assign_list[
                "assignment_id_critical"
            ].fillna(0) + assign_list["assignment_id_non_critical"].fillna(0)

            assign_list_df = assign_list.rename(
                columns={
                    "assignment_id_critical": "Critical Load",
                    "assignment_id_non_critical": "Non-Critical Load",
                }
            ).melt(
                id_vars=["zone"],
                value_vars=[
                    "Critical Load",
                    "Non-Critical Load",
                    "Total Assignment",
                ],
                var_name="load_type",
                value_name="MW",
            )

            create_groupBar_chart(
                df=assign_list_df,
                x_col="zone",
                y_col="MW",
                color_col="load_type",
                title="Automatic Load Shedding: Critical vs Non-Critical by Assignment",
                title_fsize=18,
                title_width=50,
                title_x=0,
                legend_x=0,
                legend_y=-0.15,
                legend_orient="h",
                margin=dict(t=80, b=40, l=40, r=20),
                color_discrete_map={},
                category_order={},
                height=450,
                key=None,
                showlegend=True,
                xaxis_label=None,
                yaxis_label="Number of Assignment",
            )
