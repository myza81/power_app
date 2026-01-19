import pandas as pd
import numpy as np
import streamlit as st
from datetime import date
# from typing import List, Dict, Any

from applications.load_shedding.helper import (
    columns_list,
    column_data_list,
    scheme_col_sorted,
)
from applications.data_processing.read_data import df_search_filter
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.tab2a_assign_compare import ls_assignment_comparison
from pages.load_shedding.helper import show_temporary_message, create_donut_chart, process_display_data
from css.streamlit_css import custom_metric


def loadshedding_assignment() -> None:
    st.subheader("Load Shedding Assignment")

    # Layout
    assignment_container = st.container()
    st.divider()
    metrics_container = st.container()
    st.divider()
    assignment_comparison_container = st.container()

    # State Initialization
    lprofile_obj = st.session_state["loadprofile"]

    ls_obj = st.session_state["loadshedding"]
    subs_metadata = ls_obj.subs_meta()
    masterlist = ls_obj.ls_assignment_masterlist()

    # Filter Logic
    with assignment_container:
        input_container = st.container()
        table_container = st.container()
        export_btn_container = st.container()

        with input_container:
            c1, c2, c3 = st.columns(3)
            c4, c5, c6 = st.columns(3)
            c7, c8, _ = st.columns(3)

            with c1:
                all_dfs = [
                    ls_obj.ufls_assignment,
                    ls_obj.uvls_assignment,
                    ls_obj.emls_assignment,
                ]
                years = sorted(
                    {col for df in all_dfs for col in columns_list(
                        df, ["assignment_id"])},
                    reverse=True,
                )
                review_year = st.selectbox("Review Year", options=years)

            with c2:
                schemes = st.multiselect(
                    "Scheme", options=ls_obj.LOADSHED_SCHEME, default="UFLS"
                )

            with c3:
                zones = st.multiselect(
                    "Zone",
                    options=ls_obj.ls_assignment_masterlist()[
                        "zone"].dropna().unique(),
                )

            with c4:
                subzone_list = column_data_list(
                    subs_metadata,
                    "gm_subzone",
                )
                subzone = st.multiselect(
                    label="Grid Maintenace Subzone", options=subzone_list
                )

            with c5:
                state_list = [
                    str(s)
                    for s in subs_metadata["state"].dropna().unique()
                    if str(s).strip().lower() not in ["nan", ""]
                ]
                state = st.multiselect(
                    label="State",
                    options=state_list,
                )

            with c6:
                stage_opts = ls_obj.ufls_setting.columns.tolist()
                if len(schemes) == 1:
                    if schemes[0] == "UVLS":
                        stage_opts = ls_obj.uvls_setting.columns.tolist()
                    elif schemes[0] == "EMLS":
                        stage_opts = []
                stages = st.multiselect("Operating Stage", options=stage_opts)

            with c7:
                dp_type_list = (
                    masterlist["dp_type"].replace(
                        [""], np.nan).dropna().unique().tolist()
                )
                dp_type = st.multiselect(
                    label="Tripping Assignment",
                    options=dp_type_list,
                )

            filters = {
                "review_year": review_year,
                "scheme": schemes,
                "op_stage": stages,
                "zone": zones,
                "state": state,
                "gm_subzone": subzone,
                "dp_type": dp_type,
            }

            filtered_data = ls_obj.filtered_data(
                filters=filters, df=masterlist)

            if filtered_data.empty:
                st.info("No active load shedding assignment found.")
                return

            searched_df = pd.DataFrame()
            with c8:
                search_query = st.text_input(
                    "Search", placeholder="Enter keyword...", key="ls_search"
                )
                searched_df = df_search_filter(filtered_data, search_query)

            available_schemes = [
                f"{ls}_{review_year}"
                for ls in schemes
                if f"{ls}_{review_year}" in filtered_data.columns
            ]

            missing_scheme = set([f"{ls}_{review_year}" for ls in schemes]).difference(
                set(filtered_data.columns)
            )

        # Data Display
        with table_container:
            if not searched_df.empty:

                df_display = process_display_data(
                    searched_df, ls_obj.pocket_relay(), available_schemes
                )

                df_display = scheme_col_sorted(
                    df_display, set(available_schemes), ["dp_type", "assignment_id"], keep_nulls=True
                )
                cols_order = available_schemes + [
                    "Zone",
                    "Subzone",
                    "State",
                    "Mnemonic",
                    "Substation",
                    "Voltage Level",
                    "Breaker(s)",
                    "Feeder Assignment",
                    "assignment_id",
                    "dp_type",
                ]
                st.dataframe(
                    df_display.reindex(columns=cols_order), width="stretch", hide_index=True
                )

        # Export Section
        with export_btn_container:
            c10, _, _ = st.columns([3, 1, 2])

            with c10:
                filename_input, export_btn = st.columns([6, 3])

                with filename_input:
                    filename = st.text_input(
                        label="Filename",
                        value=f"{'_'.join(available_schemes)}_LS_Assignment_{date.today().strftime('%d%m%Y')}",
                        label_visibility="collapsed",
                    )
                with export_btn:
                    save_btn = st.download_button(
                        label="Export to Excel",
                        data=export_to_excel(df_display),
                        file_name=f"{filename}.xlsx",
                        width="stretch",
                    )
                    if save_btn:
                        show_temporary_message(
                            "info", f"Saved as {filename}.xlsx")

            if missing_scheme:
                for scheme in missing_scheme:
                    st.info(
                        f"No active load shedding {scheme} assignment found for the selected filters."
                    )

    # Metrics and Charts
    with metrics_container:
        for ls_sch in available_schemes:

            col_pie1, col_pie2, col_metrics = st.columns([2, 2, 2])

            # Data Prep for charts
            plot_df = filtered_data.copy()
            plot_df[ls_sch] = plot_df[ls_sch].replace("nan", np.nan)

            zone_ls = plot_df.groupby(["zone", ls_sch], as_index=False)[
                "Load (MW)"
            ].sum()
            total_ls_mw = zone_ls["Load (MW)"].sum()
            total_system_mw = ls_obj.load_profile["Load (MW)"].sum()

            with col_pie1:
                create_donut_chart(
                    df=zone_ls,
                    values_col="Load (MW)",
                    names_col="zone",
                    title=f"{ls_sch} Assignment - by Regional Zone",
                    key=f"pie_zone_{ls_sch}",
                    annotations=f"{total_ls_mw:,.0f} MW",
                )

            with col_metrics:
                custom_metric(
                    "Total Load Shed",
                    f"{total_ls_mw:,.0f} MW",
                    f"{(total_ls_mw/total_system_mw)*100:.1f}% of MD",
                )

                for z in zone_ls["zone"].unique():
                    z_total = lprofile_obj.regional_loadprofile(z)
                    z_shed = zone_ls[zone_ls["zone"] == z]["Load (MW)"].sum()
                    st.caption(
                        f"**{z}**: {z_shed:,.0f} MW ({(z_shed/z_total)*100:.1f}%)"
                    )

            with col_pie2:
                dp_ls = plot_df.groupby(["dp_type", ls_sch], as_index=False)[
                    "Load (MW)"
                ].sum()

                create_donut_chart(
                    df=dp_ls,
                    values_col="Load (MW)",
                    names_col="dp_type",
                    title=f"{ls_sch} Assignment - by Load Type",
                    key=f"pie_dp_{ls_sch}",
                    annotations=f"{total_ls_mw:,.0f} MW",
                )

    # Assignment Comparison
    with assignment_comparison_container:
        ls_assignment_comparison()
