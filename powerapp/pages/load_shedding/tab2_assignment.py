import pandas as pd
import numpy as np
import streamlit as st
from datetime import date
from applications.load_shedding.helper import (
    columns_list,
    column_data_list,
    scheme_col_sorted,
)
from applications.data_processing.read_data import df_search_filter
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.tab2a_assign_compare import ls_assignment_comparison
from pages.load_shedding.helper import show_temporary_message, create_donut_chart, process_display_data, find_latest_assignment
from css.streamlit_css import custom_metric


def ls_assignment_main():
    loadshedding_assignment()
    ls_assignment_comparison()


def loadshedding_assignment() -> None:
    st.subheader("Load Shedding Assignment")

    # Layout
    assignment_container = st.container()
    st.divider()
    metrics_container = st.container()
    st.divider()

    # State Initialization
    ls_obj = st.session_state["loadshedding"]
    profile_metadata = ls_obj.profile_metadata()

    masterlist = ls_obj.ls_assignment_masterlist()

    # Filter Logic
    with assignment_container:
        input_container = st.container()
        table_container = st.container()
        export_btn_container = st.container()

        with input_container:
            schemes_input, zones_input, subzone_input = st.columns(3)
            state_input, oper_stg_input, dp_input = st.columns(3)
            search_input, _, _ = st.columns(3)

            with schemes_input:
                ls_scheme_cols = [
                    c for c in masterlist.columns if any(k in c for k in ls_obj.LOADSHED_SCHEME)
                ]

                latest_assignment = find_latest_assignment(ls_scheme_cols)

                ufls_latest = [
                    ls for ls in latest_assignment if 'ufls' in str(ls).lower()]

                schemes = st.multiselect(
                    "Scheme", options=ls_scheme_cols, default=ufls_latest[0]
                )

            with zones_input:
                zones = st.multiselect(
                    "Zone",
                    options=ls_obj.ls_assignment_masterlist()[
                        "zone"].dropna().unique(),
                )

            with subzone_input:
                subzone_list = column_data_list(
                    profile_metadata,
                    "gm_subzone",
                )
                subzone = st.multiselect(
                    label="Grid Maintenace Subzone", options=subzone_list
                )

            with state_input:
                state_list = [
                    str(s)
                    for s in profile_metadata["state"].dropna().unique()
                    if str(s).strip().lower() not in ["nan", ""]
                ]
                state = st.multiselect(
                    label="State",
                    options=state_list,
                )

            with oper_stg_input:
                stage_opts = ls_obj.ufls_setting.columns.tolist()
                if len(schemes) == 1:
                    if schemes[0] == "UVLS":
                        stage_opts = ls_obj.uvls_setting.columns.tolist()
                    elif schemes[0] == "EMLS":
                        stage_opts = []
                stages = st.multiselect("Operating Stage", options=stage_opts)

            with dp_input:
                dp_type_list = (
                    masterlist["dp_type"].replace(
                        [""], np.nan).dropna().unique().tolist()
                )
                dp_type = st.multiselect(
                    label="Tripping Assignment",
                    options=dp_type_list,
                )

            filters = {
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
            with search_input:
                search_query = st.text_input(
                    "Search", placeholder="Enter keyword...", key="ls_search"
                )
                searched_df = df_search_filter(filtered_data, search_query)

        # Data Display
        with table_container:
            if not searched_df.empty:
                df_display = process_display_data(
                    searched_df, ls_obj.pocket_relay(), schemes
                )

                df_display = scheme_col_sorted(
                    df_display, set(schemes), ["dp_type", "assignment_id"], keep_nulls=True
                )
                cols_order = schemes + [
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
            else:
                st.info("No active load shedding assignment found.")
                return

        # Export Section
        with export_btn_container:
            if not searched_df.empty:
                c10, _ = st.columns([3, 1])

                with c10:
                    filename_input, export_btn = st.columns([2, 1])

                    with filename_input:
                        filename = st.text_input(
                            label="Filename",
                            value=f"{'_'.join(schemes)}_LS_Assignment_{date.today().strftime('%d%m%Y')}",
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

    # Metrics and Charts
    with metrics_container:
        for ls_sch in schemes:
            col_pie1, col_pie2, col_metrics = st.columns([2, 2, 2])

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
                    title=f"{ls_sch} - by Regional Zone",
                    title_width=30,
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
                    zoneMW = ls_obj.zone_load_profile(z)
                    z_shed = zone_ls[zone_ls["zone"] == z]["Load (MW)"].sum()
                    st.caption(
                        f"**{z}**: {z_shed:,.0f} MW ({(z_shed/zoneMW)*100:.1f}%)"
                    )

            with col_pie2:
                dp_ls = plot_df.groupby(["dp_type", ls_sch], as_index=False)[
                    "Load (MW)"
                ].sum()

                create_donut_chart(
                    df=dp_ls,
                    values_col="Load (MW)",
                    names_col="dp_type",
                    title=f"{ls_sch} - by Load Type",
                    title_width=30,
                    key=f"pie_dp_{ls_sch}",
                    annotations=f"{total_ls_mw:,.0f} MW",
                )

