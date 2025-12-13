import streamlit as st
from applications.load_shedding.load_profile import df_search_filter
from applications.load_shedding.helper import (
    column_data_list)


def critical_list():
    loadshedding = st.session_state["loadshedding"]
    zone_mapping = loadshedding.zone_mapping
    subs_metadata = loadshedding.subs_metadata_enrichment()
    dp_flaglist = loadshedding.merged_dp_with_flaglist()

    st.subheader("List of Critical Load from GSO & DSO")
    show_all_warning_list = st.checkbox(
        "**Show All Critical Load (Non-overlap & Overlap)**", value=False
    )

    if show_all_warning_list:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            zone = sorted(set(zone_mapping.values()))
            zone_selected = st.multiselect(
                label="Regional Zone",
                options=zone,
                key="flaglist_zone",
            )

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

        with col3:
            critical_list = list(set(dp_flaglist["critical_list"]))
            selected_critical_list = st.multiselect(
                label="Critical List by",
                options=critical_list,
                key="flaglist_critical_list",
            )

        with col4:
            ls_dp = list(set(dp_flaglist["ls_dp"]))
            trip_assignment = st.multiselect(
                label="Tripping Assignment",
                options=ls_dp,
                key="flaglist_ls_dp",
            )

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
            filtered_data["critical_list"] = filtered_data["critical_list"].str.upper()

            filtered_data = filtered_data.rename(
                columns={
                    "substation_name": "Substation",
                    "mnemonic": "Mnemonic",
                    "kV": "Voltage Level",
                    "short_text": "Remark",
                    "critical_list": "List by"
                }
            )

            columns_order = [
                "Substation",
                "Mnemonic",
                "Voltage Level",
                "Remark",
                "List by",
                "assignment_id",
            ]

            if not filtered_data.empty:
                filtered_df = df_search_filter(filtered_data, search_query)
                df_final_display = filtered_df.reindex(columns=columns_order)
                st.dataframe(
                    df_final_display,
                    width="stretch",
                    hide_index=True,
                )
                st.markdown(
                    f'Count of Critical Load Delivery Points:<span style="color:#2E86C1; font-size: 16px; font-weight: 600"> {len(remove_duplicate):,} </span>',
                    unsafe_allow_html=True
                )
            else:
                st.info(
                    "No active load shedding assignment found for the selected filters."
                )
        else:
            st.info(
                "No active load shedding assignment found for the selected filters."
            )
