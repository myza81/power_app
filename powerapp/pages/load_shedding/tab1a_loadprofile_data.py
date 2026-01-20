import streamlit as st
import numpy as np
from applications.load_shedding.load_profile import df_search_filter


def loadprofile_data():
    col1, _, col2 = st.columns([2, 0.1, 1])
    with col1:
        loadprofile_table()
    with col2:
        loadprofile_finder()


def loadprofile_table():
    loadprofile = st.session_state["loadprofile"]
    load_df = loadprofile.df

    st.markdown(
        f'<span style="color: inherit; font-size: 20px; font-weight: 600">1. Load Profile Data Table</span>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    error_container = st.container()
    dataframe_container = st.container()

    with col1:
        search_query = st.text_input(
            label="Search for a Keyword",
            placeholder="Enter your search term here...",
            key="search_box",
        )

    with col2:
        filtered_df = df_search_filter(load_df, search_query)
        if filtered_df.empty and search_query:
            error_container.warning(
                f"No results found for the query: **'{search_query}'**")
            max_rows = 0
            rows_to_display = 0
        else:
            max_rows = len(filtered_df)

            if max_rows <= 1:
                rows_to_display = max_rows
                if max_rows == 0:
                    st.info("No data found matching your filters.")
            else:
                rows_to_display = st.slider(
                    "Select number of rows to display",
                    min_value=1,
                    max_value=max_rows,
                    value=min(10, max_rows),
                    step=1,
                    help=f"Currently filtering from {len(load_df)} total rows. {max_rows} rows match the search query.",
                    key="substation_load_slider",
                )

            with dataframe_container:
                st.dataframe(filtered_df.head(rows_to_display),
                             width="stretch", hide_index=True)


def loadprofile_finder():
    ls_obj = st.session_state["loadshedding"]
    load_df = ls_obj.loadprofile_df()

    st.markdown(
        f'<span style="color: inherit; font-size: 20px; font-weight: 600">2. Find Substation Load Profile</span>',
        unsafe_allow_html=True,
    )

    substation_list = load_df["subs_fullname"].unique().tolist()
    subs_input = st.selectbox(label="Substation Name",
                              options=substation_list, key="subs_finder")
    selected_subs = load_df.loc[load_df["subs_fullname"] == subs_input]

    totalMW = selected_subs["Load (MW)"].sum()
    zone = ", ".join(selected_subs["zone"].astype(str).unique())
    state = ", ".join(selected_subs["state"].astype(str).unique())
    gmzone = ", ".join(selected_subs["gm_subzone"].astype(str).unique())

    st.metric(
        label=f"Total Demand for {subs_input}:", value=f"{totalMW:.2f} MW")
    st.write(f"Zone: {zone} | Subzone: {gmzone} | State: {state}")
    for index, row in selected_subs.iterrows():
        st.write(f"**{row["feeder_id"]}:** {row["Load (MW)"]} MW")


def load_verifyer():
    ls_obj = st.session_state["loadshedding"]
    load_dp = ls_obj.load_dp()

    substations = load_dp["mnemonic"].unique()

    subs = {
        "Substation": [],
        "MW": []
    }
    for sub in substations:
        subs_loadMW = load_dp.loc[load_dp["mnemonic"]
                                  == sub]["Load (MW)"].sum()
        if subs_loadMW <= 0:
            subs["Substation"].append(sub)
            subs["MW"].append(subs_loadMW)

    st.write(subs["Substation"])
