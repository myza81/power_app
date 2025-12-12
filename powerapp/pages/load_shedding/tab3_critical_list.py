import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
from applications.load_shedding.load_profile import df_search_filter
from applications.load_shedding.helper import (column_data_list, scheme_col_sorted)


def critical_list():
    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    zone_mapping = loadshedding.zone_mapping
    subs_metadata = loadshedding.subs_metadata_enrichment()
    dp_flaglist = loadshedding.merged_dp_with_flaglist()

    LOADSHED_SCHEME = ["UFLS", "UVLS", "EMLS"]

    #########################################################
    ##      sub-section 1: List of Critical Load          ##
    #########################################################
    st.subheader("List of Critical Load from GSO & DSO")
    show_all_warning_list = st.checkbox(
        "**Show All Critical Load (Non-overlap & Overlap)**", value=False
    )

    if show_all_warning_list:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # --- Column 1: Review Year ---
        with col1:
            zone = sorted(set(zone_mapping.values()))
            zone_selected = st.multiselect(
                label="Regional Zone",
                options=zone,
                key="flaglist_zone",
            )

        # --- Column 2: Scheme ---
        with col2:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(
                label="GM Subzone",
                options=subzone,
                key="flaglist_subzone",
            )

        # --- Column 3: critical_list ---
        with col3:
            critical_list = list(set(dp_flaglist["critical_list"]))
            selected_critical_list = st.multiselect(
                label="Critical List by",
                options=critical_list,
                key="flaglist_critical_list",
            )

        # --- Column 4: ls_dp ---
        with col4:
            ls_dp = list(set(dp_flaglist["ls_dp"]))
            trip_assignment = st.multiselect(
                label="Tripping Assignment",
                options=ls_dp,
                key="flaglist_ls_dp",
            )

        # --- Column 5: Search Box ---
        with col5:
            search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search keyword here...",
                key="flaglist_search_box",
            )

        filters = {
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
            "critical_list": selected_critical_list,
            "ls_dp": trip_assignment,
        }

        dp = loadshedding.dp_grpId_loadquantum()

        flaglist = dp.loc[
            (dp["critical_list"] == "dn") | (dp["critical_list"] == "gso")
        ]

        if not flaglist.empty:
            remove_duplicate = flaglist.drop_duplicates(
                subset=["local_trip_id", "mnemonic", "feeder_id"], keep="first"
            )

            filtered_data = loadshedding.filtered_data(
                filters=filters, df=remove_duplicate
            )

            if not filtered_data.empty:
                filtered_df = df_search_filter(filtered_data, search_query)
                st.dataframe(
                    filtered_df,
                    column_order=[
                        "mnemonic",
                        "kV",
                        "assignment_id",
                        "short_text",
                        "critical_list",
                    ],
                    width="stretch",
                    hide_index=True,
                )
                st.write(len(remove_duplicate))

            else:
                st.info(
                    "No active load shedding assignment found for the selected filters."
                )

        else:
            st.info(
                "No active load shedding assignment found for the selected filters."
            )

    st.divider()

    #########################################################
    ##      sub-section 2: Overlap Critical Load List       ##
    #########################################################
    st.subheader("Overlap Critical Load List with Existing Load Shedding Scheme")

    show_overlap_list = st.checkbox("**Show Overlap Critical Load List**", value=False)

    if show_overlap_list:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # --- Column 1: Review Year ---
        with col1:
            review_year_list = ufls_assignment.columns.drop(
                "assignment_id", errors="ignore"
            ).tolist()
            review_year_list.sort(reverse=True)
            review_year = st.selectbox(
                label="Review Year",
                options=review_year_list,
                key="overlap_flaglist_review_year",
            )

        # --- Column 2: Scheme ---
        with col2:
            ls_scheme = st.multiselect(
                label="Scheme",
                options=LOADSHED_SCHEME,
                key="overlap_flaglist_scheme",
                default="UFLS",
            )
            selected_ls_scheme = LOADSHED_SCHEME if ls_scheme == [] else ls_scheme

        # --- Column 3: Operating Stage ---
        with col3:
            ls_stage_options = ufls_setting.columns.tolist()
            if len(selected_ls_scheme) == 1 and selected_ls_scheme[0] == "UVLS":
                ls_stage_options = uvls_setting.columns.tolist()

            stage_selected = st.multiselect(
                label="Operating Stage",
                options=ls_stage_options,
                key="overlap_flaglist_stage",
            )

        # --- Column 4: Zone ---
        with col4:
            zone = sorted(set(zone_mapping.values()))
            zone_selected = st.multiselect(
                label="Regional Zone",
                options=zone,
                key="overlap_flaglist_zone",
            )

        # --- Column 5: Search Box ---
        with col5:
            subzone = column_data_list(
                subs_metadata,
                "gm_subzone",
            )
            subzone_selected = st.multiselect(
                label="GM Subzone",
                options=subzone,
                key="overlap_flaglist_subzone",
            )

        with col6:
            search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search keyword here...",
                key="overlap_flaglist_search_box",
            )
        filters = {
            "review_year": review_year,
            "scheme": selected_ls_scheme,
            "op_stage": stage_selected,
            "zone": zone_selected,
            "gm_subzone": subzone_selected,
        }

        masterlist_ls = loadshedding.ls_assignment_masterlist()
        overlap_list = masterlist_ls.loc[
            (masterlist_ls["critical_list"] == "dn")
            | (masterlist_ls["critical_list"] == "gso")
        ]

        filtered_data = loadshedding.filtered_data(filters=filters, df=overlap_list)

        if not filtered_data.empty:
            selected_inp_scheme = [
                f"{scheme}_{review_year}" for scheme in selected_ls_scheme
            ]

            missing_scheme = set(selected_inp_scheme).difference(
                set(filtered_data.columns)
            )
            available_scheme_set = set(selected_inp_scheme).intersection(
                set(filtered_data.columns)
            )

            filtered_df = df_search_filter(filtered_data, search_query)

            ls_cols = [
                col
                for col in filtered_df.columns
                if any(keyword in col for keyword in LOADSHED_SCHEME)
            ]
            other_cols = ["mnemonic", "kV", "assignment_id", "short_text"]
            col_seq = ls_cols + other_cols

            sorted_df = scheme_col_sorted(filtered_df, available_scheme_set)
            st.dataframe(
                sorted_df, column_order=col_seq, width="stretch", hide_index=True
            )

            if missing_scheme:
                for scheme in missing_scheme:
                    st.info(
                        f"No active load shedding {scheme} assignment found for the selected filters."
                    )

        else:
            st.info(
                "No active load shedding assignment found for the selected filters."
            )

        st.divider()

        #########################################################
        ##      sub-section 3: Stacked Bar Chart      ##
        #########################################################
        st.subheader(
            "Distributions of Overlap Critical Load List with Existing Load Shedding Scheme"
        )

        if selected_ls_scheme:
            ls_cols = [
                col
                for col in overlap_list.columns
                if any(keyword in col for keyword in LOADSHED_SCHEME)
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

                tab3_s3_col1, tab3_s3_col2 = st.columns([1,3])

                df_list = masterlist_ls[
                    [ls_review, "critical_list", "assignment_id", "Pload (MW)"]
                ].copy()

                df_list[ls_review] = df_list[ls_review].replace(["nan", "#na"], np.nan)
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

                with tab3_s3_col1:
                    st.dataframe(sorted_df, hide_index=True)

                with tab3_s3_col1:
                    pass

        else:
            st.info("No load shedding assignment found for the selected filters.")
