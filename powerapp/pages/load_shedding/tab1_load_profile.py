import streamlit as st
import pandas as pd
import plotly.express as px

from applications.load_shedding.load_profile import (
    load_profile_metric,
    df_search_filter,
)


def display_load_profile():

    load_profile_df = st.session_state["load_profile"] 
    total_mw = int(load_profile_df["Pload (MW)"].sum())
    north_MW = int(load_profile_metric(load_profile_df, "North"))
    kValley_MW = int(load_profile_metric(load_profile_df, "KlangValley"))
    south_MW = int(load_profile_metric(load_profile_df, "South"))
    east_MW = int(load_profile_metric(load_profile_df, "East"))

    tab1_s1_col1, tab1_s1_col2, tab1_s1_col3 = st.columns([2.0,3.5,2.5])
    with tab1_s1_col1:
        st.metric(
            label=f"Maximum Demand (MD)",
            value=f"{total_mw:,} MW",
        )

    with tab1_s1_col2:
        colf2_1, colf2_2 = st.columns(2)
        with colf2_1:
            st.metric(
                label="North Demand",
                value=f"{north_MW:,} MW",
            )
            st.metric(
                label="Klang Valley Demand",
                value=f"{kValley_MW:,} MW",
            )
        with colf2_2:
            st.metric(
                label="South Demand",
                value=f"{south_MW:,} MW",
            )
            st.metric(
                label="East Demand",
                value=f"{east_MW:,} MW",
            )

    with tab1_s1_col3:
        data = {
            'Regional': ["North", "KlangValley", "South", "East"],
            "Load Demand": [north_MW, kValley_MW, south_MW, east_MW]
        }
        df = pd.DataFrame(data)
        fig = px.pie(
            df, 
            values='Load Demand', 
            names='Regional', 
            title='Regional Load Demand Profile'
        )
        fig.update_traces(
            hole=.6, 
            hoverinfo="label+percent+value", 
            textinfo='percent+label',
            
        )
        fig.update_layout(
            title=dict(
                font=dict(size=15, color='White'),
                y=0.015,
                x=0.5,
                xanchor='center',
                xref='paper',
            ),
            showlegend=False, 
            height=230,  
            width=250,
            margin=dict(t=0, b=15, l=3, r=3),
            annotations=[
                dict(
                    text=f"{total_mw:,} MW", 
                    x=0.5,         
                    y=0.5,          
                    font_size=20,  
                    showarrow=False, 
                    align="center" 
                )
            ]
        )
        st.plotly_chart(fig, width="stretch")

    
    #### List of Load Profile Dataframe  ##############################
    
    show_table = st.checkbox("**Show Load Profile Data**", value=False)

    if show_table:
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

        

        