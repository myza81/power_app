import streamlit as st
from applications.load_shedding.load_profile import df_search_filter
from applications.load_shedding.helper import column_data_list


def critical_list():

    st.subheader("List of Critical Load from GSO & DSO")

    ls_obj = st.session_state.get("loadshedding")
    flaglist_subs = ls_obj.flaglist_subs()

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        zones = st.multiselect(
            label="Zone",
            options=flaglist_subs["zone"].dropna().unique(),
            key="flaglist_zones"
        )

    with col2:
        subzone_list = column_data_list(
            ls_obj.subs_meta(),
            "gm_subzone",
        )
        subzones = st.multiselect(
            label="Grid Maintenace Subzone", options=subzone_list, key="flaglist_subzones")

    with col3:
        state = st.multiselect(
            label="State",
            options=flaglist_subs["state"].dropna().unique(),
            key="flaglist_state",
        )

    with col4:
        selected_critical_list = st.multiselect(
            label="Critical List by",
            options=flaglist_subs["critical_list"].dropna().unique(),
            key="flaglist_critical_list",
        )

    with col5:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search keyword here...",
            key="flaglist_search_box",
        )

    filters = {
        "zone": zones,
        "gm_subzone": subzones,
        "critical_list": selected_critical_list,
        "state": state,
    }

    if not flaglist_subs.empty:

        filtered_flaglist = ls_obj.simple_filtered(
            filters=filters, df=flaglist_subs)

        if filtered_flaglist.empty:
            st.info("No active load shedding assignment found.")
            return

        filtered_flaglist = filtered_flaglist.rename(
            columns={
                "substation_name": "Substation",
                "state": "State",
                "mnemonic": "Mnemonic",
                "kV": "Voltage Level",
                "short_text": "Remark",
                "critical_list": "List by"
            }
        )

        columns_order = [
            "State",
            "Substation",
            "Mnemonic",
            "Voltage Level",
            "Remark",
            "List by",
        ]

        filtered_df = df_search_filter(filtered_flaglist, search_query)
        df_final_display = filtered_df.reindex(columns=columns_order)
        st.dataframe(
            df_final_display,
            width="stretch",
            hide_index=True,
        )
        st.markdown(
            f'Displaying <span style="color:#2E86C1; font-size: 16px; font-weight: 600"> {len(df_final_display):,} </span> results out of <span style="color:#2E86C1; font-size: 16px; font-weight: 600"> {len(flaglist_subs):,} </span> total',
            unsafe_allow_html=True
        )

    else:
        st.info(
            "No active load shedding assignment found for the selected filters."
        )
