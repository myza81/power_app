import streamlit as st
import pandas as pd

from pages.load_shedding.tab4_simulator import potential_ls_candidate
from pages.load_shedding.tab5b_critList_dashboard import critical_list_metric
from pages.load_shedding.helper_chart import create_groupBar_chart
from pages.load_shedding.helper import remove_duplicates_keep_nan


def critical_list_analytic_main():
    critical_list_analytic()
    critical_list_metric()


def critical_list_analytic():
    st.subheader("Critical List Distribution Analysis")

    barchart_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    df_raw_cand, cand_with_crit, cand_without_crit = potential_ls_candidate(
        ls_obj)

    cand_with_crit_uniq = remove_duplicates_keep_nan(
        cand_with_crit, ["local_trip_id", "feeder_id"])

    cand_without_crit_uniq = remove_duplicates_keep_nan(
        cand_without_crit, ["local_trip_id", "feeder_id"])

    cand_with_crit_zone = cand_with_crit_uniq.groupby(
        ["zone"], as_index=False, dropna=False
    ).agg({"Load (MW)": "sum"})

    cand_without_crit_zone = cand_without_crit_uniq.groupby(
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

            category = ["Total Potential (MW)",
                        "Non-Critical Load", "Critical Load"]

            zone_list_df = zone_list.rename(
                columns={
                    "Load (MW)_critical": "Critical Load",
                    "Load (MW)_non_critical": "Non-Critical Load",
                }
            ).melt(
                id_vars=["zone"],
                value_vars=category,
                var_name="load_type",
                value_name="MW",
            )

            color_map = {
                "Critical Load": "#F54927",
                "Non-Critical Load": "#27C8F5",
                "Total Potential (MW)": "#2749F5"
            }

            category_order = {"load_type": category}

            create_groupBar_chart(
                df=zone_list_df,
                x_col="zone",
                y_col="MW",
                color_col="load_type",
                title="Automatic Load Shedding: Critical vs Non-Critical by Load Zone",
                title_fsize=18,
                title_width=50,
                title_x=0,
                legend_x=0.1,
                legend_y=-0.15,
                lagend_xanchor="left",
                legend_orient="h",
                margin=dict(t=80, b=50, l=40, r=20),
                color_discrete_map=color_map,
                category_order=category_order,
                height=450,
                key=None,
                showlegend=True,
                xaxis_label=None,
                yaxis_label="Load (MW)",
            )

        with barchart2:
            assign_non_list = (
                cand_without_crit.groupby(
                    ["zone"], as_index=False, dropna=False)
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

            category = ["Total Assignment",
                        "Non-Critical Load", "Critical Load"]

            assign_list_df = assign_list.rename(
                columns={
                    "assignment_id_critical": "Critical Load",
                    "assignment_id_non_critical": "Non-Critical Load",
                }
            ).melt(
                id_vars=["zone"],
                value_vars=category,
                var_name="load_type",
                value_name="MW",
            )

            color_map = {
                "Critical Load": "#F54927",
                "Non-Critical Load": "#27C8F5",
                "Total Assignment": "#2749F5"
            }
            category_order = {"load_type": category}

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
                color_discrete_map=color_map,
                category_order=category_order,
                height=450,
                key=None,
                showlegend=True,
                xaxis_label=None,
                yaxis_label="Number of Assignment",
            )
