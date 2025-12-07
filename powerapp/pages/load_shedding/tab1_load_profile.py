import streamlit as st

from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric,
    df_search_filter,
)


def display_load_profile():
    
    show_table = st.checkbox("**Show Load Profile Data**", value=False)

    if show_table:
        load_profile_df = st.session_state["load_profile"] 
        total_mw = load_profile_df["Pload (MW)"].sum()

        north_MW = load_profile_metric(load_profile_df, "North")
        kValley_MW = load_profile_metric(load_profile_df, "KlangValley")
        south_MW = load_profile_metric(load_profile_df, "South")
        east_MW = load_profile_metric(load_profile_df, "East")

        st.subheader("Load Profile Data")

        col_lp1, col_lp2 = st.columns(2)

        with col_lp1:
            search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search term here...",  
                key="search_box", 
            )

        with col_lp2:   
            filtered_df = df_search_filter(load_profile_df, search_query)
            if filtered_df.empty and search_query:
                st.warning(f"No results found for the query: **'{search_query}'**")
                max_rows = 0
                rows_to_display = 0
            else:
                max_rows = len(filtered_df)
                rows_to_display = st.slider(
                    "Select number of rows to display:",
                    min_value=1,
                    max_value=max_rows,
                    value=min(5, max_rows) if max_rows > 1 else 1,
                    step=1,
                    help=f"Currently filtering from {len(load_profile_df)} total rows. {max_rows} rows match the search query.",
                )
        
        st.dataframe(filtered_df.head(rows_to_display), width="stretch")

        col_f1, col_f2 = st.columns(2)
        col_f1.metric(
            f"Active Power MD",
            f"{int(total_mw):,} MW",
        )

        with col_f2:
            colf2_1, colf2_2 = st.columns(2)
            with colf2_1:
                st.metric(
                    label="North",
                    value=f"{int(north_MW):,} MW",
                )
                st.metric(
                    label="Klang Valley",
                    value=f"{int(kValley_MW):,} MW",
                )
            with colf2_2:
                st.metric(
                    label="South",
                    value=f"{int(south_MW):,} MW",
                )
                st.metric(
                    label="East",
                    value=f"{int(east_MW):,} MW",
                )

        