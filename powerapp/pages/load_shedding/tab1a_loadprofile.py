import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from applications.load_shedding.load_profile import df_search_filter
from pages.load_shedding.helper import create_donut_chart
from css.streamlit_css import custom_metric


def loadprofile_main():
    loadprofile_dashboard()
    st.divider()
    loadprofile_data()


def loadprofile_dashboard():
    loadprofile = st.session_state["loadprofile"]
    load_df = loadprofile.df

    col_pie1, col_metrics = st.columns([2, 2])

    with col_pie1:
        zone_ls = load_df.groupby(["zone"], as_index=False)["Load (MW)"].sum()
        create_donut_chart(zone_ls, "zone", "By Zone", f"pie_zone_grid_load_profile")

    with col_metrics:
        total_mw = loadprofile.totalMW()
        custom_metric(
            label="Maximum Demand (MD)",
            value=f"{total_mw:,.0f} MW",
        )
        st.markdown("")
        for z in load_df["zone"].unique():
            z_total = loadprofile.regional_loadprofile(z)
            st.markdown(
                f'<span style="color: inherit; font-size: 14px; font-weight: 400">{z} Demand: </span><span style="color: inherit; font-size: 18px; font-weight: 600">{z_total:,.0f} MW</span>',
                unsafe_allow_html=True,
            )


def loadprofile_data():
    show_table = st.checkbox("**Show Load Profile Data**", value=False)
    if show_table:
        col1, _, col3 = st.columns([2, 0.1, 1])
        with col1:
            loadprofile_table()
        with col3:
            loadprofile_finder()
            load_verifyer()


def loadprofile_table():
    loadprofile = st.session_state["loadprofile"]
    load_df = loadprofile.df

    st.markdown(
        f'<span style="color: inherit; font-size: 20px; font-weight: 600">1. Load Profile Data Table</span>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)

    with col1:
        search_query = st.text_input(
            label="Search for a Keyword:",
            placeholder="Enter your search term here...",
            key="search_box",
        )

    with col2:
        filtered_df = df_search_filter(load_df, search_query)
        if filtered_df.empty and search_query:
            st.warning(f"No results found for the query: **'{search_query}'**")
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
                    "Select number of rows to display:",
                    min_value=1,
                    max_value=max_rows,
                    value=min(5, max_rows),
                    step=1,
                    help=f"Currently filtering from {len(load_df)} total rows. {max_rows} rows match the search query.",
                    key="substation_load_slider",
                )

    st.dataframe(filtered_df.head(rows_to_display), width="stretch", hide_index=True)


def loadprofile_finder():

    loadshedding = st.session_state["loadshedding"]
    load_dp = loadshedding.load_dp()

    cols = [
        "mnemonic",
        "substation_name",
        "feeder_id",
        "Load (MW)",
        "zone",
        "gm_subzone",
    ]

    subs_load = load_dp[cols]

    load_profile_subs = subs_load.groupby(
        [
            "mnemonic",
            "substation_name",
        ],
        as_index=False,
        dropna=False,
    ).agg(
        {
            "Load (MW)": "sum",
            "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
        }
    )

    combined_name = (
        load_profile_subs["mnemonic"].str.cat(
            load_profile_subs["substation_name"], sep=" (", na_rep=""
        )
        + ")"
    )

    load_profile_subs["substation_fullname"] = np.where(
        load_profile_subs["substation_name"].notna(),
        combined_name,
        load_profile_subs["mnemonic"],
    )

    st.markdown(
        f'<span style="color: inherit; font-size: 20px; font-weight: 600">2. Find Substation Load Profile</span>',
        unsafe_allow_html=True,
    )

    substation_list = load_profile_subs["substation_fullname"].tolist()
    substation = st.selectbox(label="Substation Name", options=substation_list)

    subs_loadMW = load_profile_subs.loc[
        load_profile_subs["substation_fullname"] == substation
    ]["Load (MW)"].values[0]
    st.metric(label=f"Total Demand for {substation}:", value=f"{subs_loadMW:.2f} MW")


def load_verifyer():
    loadshedding = st.session_state["loadshedding"]
    load_dp = loadshedding.load_dp()

    substations = load_dp["mnemonic"].unique()

    subs = {
        "Substation": [],
        "MW":[]
    }
    for sub in substations:
        subs_loadMW = load_dp.loc[load_dp["mnemonic"] == sub]["Load (MW)"].sum()
        if subs_loadMW <= 0:
            subs["Substation"].append(sub)
            subs["MW"].append(subs_loadMW)

    st.write(subs["Substation"])
