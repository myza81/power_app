import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import time
from datetime import date
from typing import List, Optional, Sequence, Any

from applications.load_shedding.helper import (
    columns_list,
    column_data_list,
    scheme_col_sorted,
)
from applications.data_processing.read_data import df_search_filter
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.helper import display_ls_metrics, show_temporary_message


def loadshedding_assignment() -> None:
    # loadprofile = st.session_state["loadprofile"]
    # load_df = loadprofile.df

    loadshedding = st.session_state["loadshedding"]

    ufls_assignment = loadshedding.ufls_assignment
    uvls_assignment = loadshedding.uvls_assignment
    emls_assignment = loadshedding.emls_assignment

    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    subs_metadata = loadshedding.subs_meta
    # zone_mapping = loadshedding.zone_mapping
    # loadshedding_dp = loadshedding.merged_dp()
    hvcb_rly = loadshedding.rly_hvcb
    masterlist_ls = loadshedding.ls_assignment_masterlist()
    # assignment = loadshedding.assignment_loadquantum()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    st.subheader("Load Sheddding Assignment")

    show_table = st.checkbox(
        "**Show Load Shedding Assignment List**", value=True)

    if show_table:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col7, col8, col9 = st.columns(3)

        with col1:
            assignments = [ufls_assignment, uvls_assignment, emls_assignment]
            all_years = []
            for a in assignments:
                all_years.extend(columns_list(
                    a, unwanted_el=["assignment_id"]))

            year = sorted(set(all_years), reverse=True)
            review_year = st.selectbox(label="Review Year", options=year)

        with col2:
            ls_scheme = st.multiselect(
                label="Scheme", options=LS_SCHEME, default="UFLS"
            )
            # selected_ls_scheme = LS_SCHEME if ls_scheme == [] else ls_scheme
            scheme = ls_scheme

        with col3:

            zone = masterlist_ls["zone"].dropna().unique().tolist()
            zone_selected = st.multiselect(label="Regional Zone", options=zone)

        with col4:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(
                label="Grid Maintenace Subzone", options=subzone
            )

        with col5:
            ls_stage_options = ufls_setting.columns.tolist()
            if len(scheme) == 1:
                if scheme[0] == "UVLS":
                    ls_stage_options = uvls_setting.columns.tolist()
                elif scheme[0] == "EMLS":
                    ls_stage_options = None

            stage_selected = st.multiselect(
                label="Operating Stage", options=ls_stage_options
            )

        with col6:
            dp_type = masterlist_ls["dp_type"].replace(
                [""], np.nan).dropna().unique().tolist()
            trip_assignment = st.multiselect(
                label="Tripping Assignment",
                options=dp_type,
            )

        filters = {
            "review_year": review_year,
            "scheme": scheme,
            "op_stage": stage_selected,
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
            "dp_type": trip_assignment,
        }

        filtered_data = loadshedding.filtered_data(
            filters=filters, df=masterlist_ls)
        
        st.dataframe(filtered_data)

        if not filtered_data.empty:

            selected_inp_scheme = [
                f"{ls}_{review_year}" for ls in scheme
            ]

            missing_scheme = set(selected_inp_scheme).difference(
                set(filtered_data.columns)
            )
            available_scheme_set = set(selected_inp_scheme).intersection(
                set(filtered_data.columns)
            )

            with col7:
                search_query = st.text_input(
                    label="Search for a Keyword:",
                    placeholder="Enter your search keyword here...",
                    key="active_ls_search_box",
                )
                filtered_df = df_search_filter(filtered_data, search_query)
            
            

            ls_cols = [
                col
                for col in filtered_df.columns
                if any(keyword in col for keyword in LS_SCHEME)
            ]

            # add with hv relay loc
            hvcb_rly["kV"] = hvcb_rly["kV"].astype(str)
            hvcb_rly = hvcb_rly.rename(
                columns={
                    "breaker_id": "Breaker(s)",
                    "feeder_id": "Feeder Assignment",
                    "mnemonic": "Mnemonic",
                    "kV": "Voltage Level",
                }
            )

            merge_rly_loc = pd.merge(
                filtered_df,
                hvcb_rly,
                on="assignment_id",
                how="left",
            )

            

            merge_rly_loc["Mnemonic"] = merge_rly_loc["Mnemonic"].fillna(
                merge_rly_loc["mnemonic"]
            )

            merge_rly_loc["Voltage Level"] = merge_rly_loc["Voltage Level"].fillna(
                merge_rly_loc["kV"]
            )

            merge_rly_loc["Breaker(s)"] = merge_rly_loc["Breaker(s)"].fillna(
                merge_rly_loc["breaker_id"]
            )

            merge_rly_loc["Feeder Assignment"] = merge_rly_loc[
                "Feeder Assignment"
            ].fillna(merge_rly_loc["feeder_id"])

            column_order = ls_cols + [
                "Mnemonic",
                "Voltage Level",
                "Breaker(s)",
                "Feeder Assignment",
                "assignment_id",
                "dp_type",
            ]

            merge_rly_loc = merge_rly_loc[column_order]

            st.dataframe(merge_rly_loc)
            
            # merge_rly_meta = pd.merge(
            #     merge_rly_loc,
            #     subs_metadata,
            #     left_on="Mnemonic",
            #     right_on="mnemonic",
            #     how="left",
            # )[
            #     merge_rly_loc.columns.tolist()
            #     + ["zone", "gm_subzone", "substation_name"]
            # ]

        #     grp_df = merge_rly_meta.groupby(
        #         ls_cols
        #         + [
        #             "substation_name",
        #             "Mnemonic",
        #             "Voltage Level",
        #             "assignment_id",
        #             "ls_dp",
        #         ],
        #         as_index=False,
        #         dropna=False,
        #     ).agg(
        #         {
        #             "zone": lambda x: ", ".join(x.astype(str).unique()),
        #             "gm_subzone": lambda x: ", ".join(x.astype(str).unique()),
        #             "Breaker(s)": lambda x: ", ".join(x.astype(str).unique()),
        #             "Feeder Assignment": lambda x: ", ".join(x.astype(str).unique()),
        #         }
        #     )

        #     grp_df = grp_df.rename(
        #         columns={
        #             "zone": "Regional Zone",
        #             "gm_subzone": "Grid Maint. Subzone",
        #             "substation_name": "Substation",
        #             "ls_dp": "Type",
        #         }
        #     )

        #     sorted_df = scheme_col_sorted(
        #         grp_df,
        #         available_scheme_set,
        #         ["assignment_id", "Regional Zone", "Grid Maint. Subzone"],
        #     )

        #     columns_order = ls_cols + [
        #         "Regional Zone",
        #         "Grid Maint. Subzone",
        #         "Substation",
        #         "Mnemonic",
        #         "Voltage Level",
        #         "Breaker(s)",
        #         "Feeder Assignment",
        #         "Type",
        #         "assignment_id",
        #     ]

        #     df_final_display = sorted_df.reindex(columns=columns_order)

        #     st.dataframe(df_final_display, width="stretch", hide_index=True)

        #     col10, col11, col12, col13, col14 = st.columns([1.8, 1.5, 0.1, 2, 2])

        #     with col10:
        #         ls_name = [ls for ls in available_scheme_set]
        #         combine_ls_name = "_".join(ls_name)
        #         today = date.today()
        #         default_filename = (
        #             f"{combine_ls_name}_downloadOn_{today.strftime("%d%m%Y")}"
        #         )

        #         filename = st.text_input(
        #             label="Enter filename: ",
        #             value=default_filename,
        #             key="export_filename",
        #         )

        #     with col11:
        #         st.markdown("<br>", unsafe_allow_html=True)
        #         excel_data = export_to_excel(df_final_display)
        #         export_btn = st.download_button(
        #             label="Export to Excel File",
        #             data=excel_data,
        #             file_name=f"{filename}.xlsx",
        #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #             key="export_button",
        #         )

        #     if export_btn:
        #         show_temporary_message(
        #             message_type="info",
        #             message=f"File will be saved as **{filename}** to your browser's downloads folder.",
        #             duration=3,
        #         )

        #     for ls_sch in available_scheme_set:
        #         col15, col16, col17, col18, col19 = st.columns([2, 0.1, 2, 0.1, 2])

        #         filtered_data[ls_sch] = filtered_data[ls_sch].replace("nan", np.nan)

        #         zone_ls = (
        #             filtered_data[[ls_sch, "zone", "Pload (MW)"]]
        #             .groupby(["zone", ls_sch], as_index=False)
        #             .agg({"Pload (MW)": "sum"})
        #         )

        #         load_df_grp = (
        #             load_df[["zone", "Pload (MW)"]]
        #             .groupby(
        #                 ["zone"],
        #                 as_index=False,
        #             )
        #             .agg({"Pload (MW)": "sum"})
        #         )

        #         with col15:

        #             st.markdown(
        #                 f"<p style='margin-top:30px; font-size:16px; font-weight: 600; font-family: Arial'>{ls_sch} Assignment - Filtered by Regional Zone</p>",
        #                 unsafe_allow_html=True,
        #             )
        #             fig = px.pie(
        #                 zone_ls,
        #                 values="Pload (MW)",
        #                 names="zone",
        #                 title=" ",
        #             )
        #             fig.update_traces(
        #                 hole=0.5,
        #                 hoverinfo="label+percent+value",
        #                 # textinfo='value+percent+label',
        #                 texttemplate="<b>%{label}</b><br>"
        #                 + "%{value:,.0f} MW"
        #                 + " (%{percent})",
        #                 textfont_size=12,
        #                 textposition="auto",
        #             )
        #             fig.update_layout(
        #                 title=dict(
        #                     font=dict(size=15),
        #                     y=0.5,
        #                     x=0.5,
        #                     xanchor="center",
        #                     xref="paper",
        #                 ),
        #                 showlegend=False,
        #                 height=230,
        #                 width=250,
        #                 margin=dict(t=20, b=40, l=3, r=3),
        #                 annotations=[
        #                     dict(
        #                         text=f"{zone_ls["Pload (MW)"].sum():,.0f} MW",
        #                         x=0.5,
        #                         y=0.5,
        #                         font_size=20,
        #                         showarrow=False,
        #                         align="center",
        #                     )
        #                 ],
        #             )

        #             st.plotly_chart(
        #                 fig, width="stretch", key=f"{ls_sch}_filtered_region"
        #             )

        #         with col17:
        #             total_quantum = load_df_grp["Pload (MW)"].sum()
        #             total_quantum_zone = zone_ls["Pload (MW)"].sum()
        #             ls_pct = (total_quantum_zone / total_quantum) * 100

        #             st.markdown(
        #                 f"<p style='margin-top:28px; display: flex, align-item: center, justify-content: center'><span style='color:inherit; font-size:20px; font-weight: 600'>Total Load Shed Quantum:</span><br> <span style='font-size:22px; font-weight: 600'>{total_quantum_zone:,.0f} MW ({ls_pct:,.1f}%)</span></p>",
        #                 unsafe_allow_html=True,
        #             )

        #             zone_grp = zone_ls.groupby("zone", as_index=False).agg(
        #                 {
        #                     "Pload (MW)": "sum",
        #                     ls_sch: lambda x: ", ".join(x.astype(str).unique()),
        #                 }
        #             )
        #             zone_list = zone_grp["zone"]

        #             for zone in zone_list:
        #                 zone_load = loadprofile.regional_loadprofile(zone)

        #                 zone_ls_quantum = zone_grp.loc[zone_grp["zone"] == zone][
        #                     "Pload (MW)"
        #                 ].values[0]

        #                 zone_ls_pct = zone_ls_quantum / zone_load * 100

        #                 st.markdown(
        #                     f"<p style='margin-top:-10px; font-size:14px;'>Quantum Contribution from {zone}:</p>",
        #                     unsafe_allow_html=True,
        #                 )
        #                 st.markdown(
        #                     f"<p style='margin-top:-20px; color:#2E86C1; font-size:22px; font-weight: 600'>{zone_ls_quantum:,.0f} MW ({zone_ls_pct:,.1f}%)</p>",
        #                     unsafe_allow_html=True,
        #                 )

        #         with col19:
        #             filtered_data[ls_sch] = filtered_data[ls_sch].replace("nan", np.nan)
        #             ls_dp = (
        #                 filtered_data[[ls_sch, "ls_dp", "Pload (MW)"]]
        #                 .groupby(["ls_dp", ls_sch], as_index=False)
        #                 .agg({"Pload (MW)": "sum"})
        #             )

        #             st.markdown(
        #                 f"<p style='margin-top:30px; font-size:16px; font-weight: 600; font-family: Arial'>{ls_sch} Assignment - Filtered by Load Type</p>",
        #                 unsafe_allow_html=True,
        #             )
        #             fig = px.pie(
        #                 ls_dp,
        #                 values="Pload (MW)",
        #                 names="ls_dp",
        #                 title=" ",
        #             )
        #             fig.update_traces(
        #                 hole=0.5,
        #                 hoverinfo="label+percent+value",
        #                 texttemplate="<b>%{label}</b><br>"
        #                 + "%{value:,.0f} MW"
        #                 + " (%{percent})",
        #                 textfont_size=12,
        #                 textposition="auto",
        #             )
        #             fig.update_layout(
        #                 title=dict(
        #                     font=dict(size=15),
        #                     y=0.5,
        #                     x=0.5,
        #                     xanchor="center",
        #                     xref="paper",
        #                 ),
        #                 showlegend=False,
        #                 height=230,
        #                 width=250,
        #                 margin=dict(t=20, b=40, l=3, r=3),
        #                 annotations=[
        #                     dict(
        #                         text=f"{ls_dp["Pload (MW)"].sum():,.0f} MW",
        #                         x=0.5,
        #                         y=0.5,
        #                         font_size=20,
        #                         showarrow=False,
        #                         align="center",
        #                     )
        #                 ],
        #             )

        #             st.plotly_chart(fig, width="stretch", key=f"{ls_sch}_filtered_dp")

            if missing_scheme:
                for scheme in missing_scheme:
                    st.info(
                        f"No active load shedding {scheme} assignment found for the selected filters."
                    )
        else:
            st.info(
                "No active load shedding assignment found for the selected filters."
            )
