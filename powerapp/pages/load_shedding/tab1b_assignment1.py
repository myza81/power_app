import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import date
from typing import List, Dict, Any

from applications.load_shedding.helper import (
    columns_list,
    column_data_list,
    scheme_col_sorted,
)
from applications.data_processing.read_data import df_search_filter
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.helper import display_ls_metrics, show_temporary_message
from css.streamlit_css import custom_metric


def create_donut_chart(df: pd.DataFrame, names_col: str, title: str, key: str):
    """Helper to generate standardized donut charts."""
    total_mw = df["Load (MW)"].sum()
    fig = px.pie(df, values="Load (MW)", names=names_col, hole=0.5)

    fig.update_traces(
        hoverinfo="label+percent+value",
        texttemplate="<b>%{label}</b><br>%{value:,.0f} MW<br>(%{percent})",
        textfont_size=10,
        textposition="auto",
    )
    fig.update_layout(
        showlegend=False,
        height=250,
        margin=dict(t=30, b=10, l=10, r=10),
        annotations=[dict(text=f"{total_mw:,.0f} MW",
                          x=0.5, y=0.5, font_size=18, showarrow=False)]
    )
    st.plotly_chart(fig, width='content', key=key)


def process_display_data(searched_df: pd.DataFrame, pocket_relay: pd.DataFrame, scheme_cols: List[str]) -> pd.DataFrame:
    """Handles the merging and grouping logic for the main table."""
    # Use suffixes to avoid collision, then fill missing values
    df_merged = pd.merge(searched_df, pocket_relay,
                         on="assignment_id", how="left", suffixes=('', '_rly'))

    # Clean up columns: Prefer original, fallback to relay data
    mappings = {
        "Regional Zone": "zone",
        "Grid Maint. Subzone": "gm_subzone",
        "Mnemonic": "mnemonic",
        "Substation": "substation_name",
        "Breaker(s)": "breaker_id",
        "Feeder Assignment": "feeder_id"
    }

    for display_col, raw_col in mappings.items():
        # If the display_col doesn't exist yet, it's created from raw_col
        # If it does exist (from relay data), fill nans from raw_col
        if display_col in df_merged.columns:
            df_merged[display_col] = df_merged[display_col].fillna(
                df_merged[raw_col])
        else:
            df_merged[display_col] = df_merged[raw_col]

    df_merged["Voltage Level"] = df_merged["kV"].astype(str)

    group_cols = scheme_cols + \
        ["Substation", "Mnemonic", "Voltage Level", "assignment_id", "dp_type"]
    agg_map = {
        "Regional Zone": lambda x: ", ".join(x.astype(str).unique()),
        "Grid Maint. Subzone": lambda x: ", ".join(x.astype(str).unique()),
        "Breaker(s)": lambda x: ", ".join(x.astype(str).unique()),
        "Feeder Assignment": lambda x: ", ".join(x.astype(str).unique()),
    }

    return df_merged.groupby(group_cols, as_index=False, dropna=False).agg(agg_map)


def loadshedding_assignment() -> None:
    # 1. State Initialization
    ls_obj = st.session_state["loadshedding"]
    load_profile_obj = st.session_state["loadprofile"]

    st.subheader("Load Shedding Assignment")
    if not st.checkbox("**Show Load Shedding Assignment List**", value=True):
        return

    # 2. Filters UI
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    with c1:
        # Simplified year extraction
        all_dfs = [ls_obj.ufls_assignment,
                   ls_obj.uvls_assignment, ls_obj.emls_assignment]
        years = sorted({col for df in all_dfs for col in columns_list(
            df, ["assignment_id"])}, reverse=True)
        review_year = st.selectbox("Review Year", options=years)

    with c2:
        schemes = st.multiselect(
            "Scheme", options=ls_obj.LOADSHED_SCHEME, default="UFLS")

    with c3:
        zones = st.multiselect("Regional Zone", options=ls_obj.ls_assignment_masterlist()[
                               "zone"].dropna().unique())

    with c5:
        # Simplified Stage Logic
        stage_opts = ls_obj.ufls_setting.columns.tolist()
        if len(schemes) == 1:
            if schemes[0] == "UVLS":
                stage_opts = ls_obj.uvls_setting.columns.tolist()
            elif schemes[0] == "EMLS":
                stage_opts = []
        stages = st.multiselect("Operating Stage", options=stage_opts)

    # 3. Data Filtering
    filters = {
        "review_year": review_year, "scheme": schemes, "op_stage": stages,
        "zone": zones, "gm_subzone": [], "dp_type": []  # Add others as needed
    }

    masterlist = ls_obj.ls_assignment_masterlist()
    filtered_data = ls_obj.filtered_data(filters=filters, df=masterlist)

    if filtered_data.empty:
        st.info("No active load shedding assignment found.")
        return

    # 4. Search and Table Processing
    search_query = st.text_input(
        "Search:", placeholder="Enter keyword...", key="ls_search")
    searched_df = df_search_filter(filtered_data, search_query)

    available_schemes = [
        f"{ls}_{review_year}" for ls in schemes if f"{ls}_{review_year}" in filtered_data.columns]

    if not searched_df.empty:
        df_display = process_display_data(
            searched_df, ls_obj.pocket_relay(), available_schemes)

        # Sort and Reorder
        df_display = scheme_col_sorted(df_display, set(
            available_schemes), ["assignment_id"])
        cols_order = available_schemes + ["Regional Zone", "Grid Maint. Subzone", "Mnemonic",
                                          "Substation", "Voltage Level", "Breaker(s)", "Feeder Assignment", "assignment_id", "dp_type"]
        st.dataframe(df_display.reindex(columns=cols_order),
                     width='content', hide_index=True)

        # 5. Export Section
        export_col, btn_col = st.columns([3, 1])
        filename = export_col.text_input(
            "Filename", value=f"{'_'.join(available_schemes)}_DL_{date.today().strftime('%d%m%Y')}")
        if btn_col.download_button("Export to Excel", data=export_to_excel(df_display), file_name=f"{filename}.xlsx"):
            show_temporary_message("info", f"Saved as {filename}.xlsx")

    # 6. Metrics and Charts
    st.divider()
    for ls_sch in available_schemes:
        st.write(f"### Analysis: {ls_sch}")
        col_pie1, col_metrics, col_pie2 = st.columns([2, 2, 2])

        # Data Prep for charts
        plot_df = filtered_data.copy()
        plot_df[ls_sch] = plot_df[ls_sch].replace("nan", np.nan)

        with col_pie1:
            zone_ls = plot_df.groupby(["zone", ls_sch], as_index=False)[
                "Load (MW)"].sum()
            create_donut_chart(zone_ls, "zone", "By Zone",
                               f"pie_zone_{ls_sch}")

        with col_metrics:
            total_ls_mw = zone_ls["Load (MW)"].sum()
            total_system_mw = ls_obj.load_profile["Load (MW)"].sum()

            custom_metric("Total Load Shed", f"{total_ls_mw:,.0f} MW",
                          f"{(total_ls_mw/total_system_mw)*100:.1f}% of System")

            # Regional breakdown
            for z in zone_ls["zone"].unique():
                z_total = load_profile_obj.regional_loadprofile(z)
                z_shed = zone_ls[zone_ls["zone"] == z]["Load (MW)"].sum()
                st.caption(
                    f"**{z}**: {z_shed:,.0f} MW ({(z_shed/z_total)*100:.1f}%)")

        with col_pie2:
            dp_ls = plot_df.groupby(["dp_type", ls_sch], as_index=False)[
                "Load (MW)"].sum()
            create_donut_chart(
                dp_ls, "dp_type", "By Load Type", f"pie_dp_{ls_sch}")
