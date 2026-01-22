import pandas as pd
import streamlit as st
from applications.load_shedding.helper import scheme_col_sorted
from pages.load_shedding.helper import create_stackedBar_chart, get_dynamic_colors, stage_sort


def lshedding_barStacked(df, scheme):
    # 1. Data Preparation & Aggregation
    load_profile_obj = st.session_state["loadprofile"]
    load_df_grp = load_profile_obj.df.groupby(
        "zone").agg({"Load (MW)": "sum"}).reset_index()

    ls_operstage = df[[scheme, "zone", "Load (MW)"]]
    ls_operstage_grp = ls_operstage.groupby(
        [scheme, "zone"],
        as_index=False,
    ).agg({"Load (MW)": "sum"})
    ls_operstage_grp = ls_operstage_grp.rename(
        columns={"Load (MW)": "Shedding"})

    regional_df = ls_operstage_grp.groupby("zone")["Shedding"].sum()
    zone_df = pd.merge(regional_df, load_df_grp, on='zone', how='left')

    zone_df[["Shedding", "Load (MW)"]] = zone_df[[
        "Shedding", "Load (MW)"]].fillna(0)
    zone_df["Un-shed"] = zone_df["Load (MW)"] - \
        zone_df["Shedding"]

    cols = ["Load (MW)", "Shedding", "Un-shed"]
    zone_df[cols] = zone_df[cols].fillna(0).astype(int)

    staging_ls = ls_operstage_grp.groupby(["zone", scheme]).agg(
        {"Shedding": "sum"}).reset_index()

    # 3. Layout: Visualization
    c1, _, c2 = st.columns([1, 0.1, 1])
    c3, _ = st.columns([1, 0.1])

    # Regional Zone Shedding Quantum Vs Un-Shed Quantum
    with c1:
        df_melted_regional = zone_df.melt(
            id_vars=['zone'],
            value_vars=['Shedding', 'Un-shed'],
            var_name='load_type',
            value_name='mw'
        )

        create_stackedBar_chart(
            df=df_melted_regional,
            x_col="zone",
            y_col="mw",
            color_col="load_type",
            color_discrete_map={
                "Shedding": "#E74C3C",
                "Un-shed": "#D5D8DC",
            },
            title=f"{scheme} Quantum Vs Un-Shed Quantum - by Zone",
            title_width=30,
            category_order={"load_type": ["Un-shed", "Shedding"]},
            key=f"regional_load_shedding_stackedBar{scheme}",
            showlegend=True,
            legend_x=0,
            legend_y=-0.15,
            legend_orient="h",
        )

    # Regional Operating Stage
    with c2:
        df_melted_staging = staging_ls.melt(
            id_vars=['zone', scheme],
            value_vars=['Shedding'],
            var_name='load_type',
            value_name='mw'
        )

        scheme_list = staging_ls[scheme].unique().tolist()

        if not scheme_list:
            sorted_stages = []
        else:
            sorted_stages = sorted(scheme_list, key=stage_sort)

        dynamic_color_map = get_dynamic_colors(categories=sorted_stages)

        create_stackedBar_chart(
            df=df_melted_staging,
            x_col="zone",
            y_col="mw",
            y_label="Load Shedd Quantum (MW)",
            color_col=scheme,
            color_discrete_map=dynamic_color_map,
            title=f"{scheme} Operational Staging - by Zone",
            title_width=30,
            category_order={scheme: sorted_stages},
            key=f"regional_load_shedding_staging_stackedBar{scheme}",
            showlegend=True,
            legend_x=0,
            legend_y=-0.15,
            legend_orient="h",
        )

    # Regional Distribution
    with c3:
        ls_oper_zone = df[[scheme, "zone", "Load (MW)"]].groupby(
            [scheme, "zone"],
            as_index=False,
        ).agg({"Load (MW)": "sum"})

        ls_sorted = scheme_col_sorted(ls_oper_zone, scheme)

        scheme_list = ls_oper_zone[scheme].unique().tolist()
        sorted_stages = sorted(scheme_list, key=stage_sort)

        create_stackedBar_chart(
            ls_sorted,
            x_col=scheme,
            y_col="Load (MW)",
            color_col="zone",
            title=f"{scheme} Regional Zone Distributions",
            title_width=30,
            y_label="Load Shedd Quantum (MW)",
            color_discrete_map={},
            category_order={
                "zone": ["KlangValley", "South", "North", "East"],
                scheme: sorted_stages,
            },
            height=450,
            key=f"{scheme}_regional_zone_distribution",
            showlegend=True,
            legend_x=0,
            legend_y=-0.15,
            legend_orient="h",
        )
