import time
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Optional, Sequence, Any
from applications.load_shedding.load_profile import (
    load_profile_metric,
)


def display_ls_metrics(scheme, df, load_profile):

    st.dataframe(df)

    col1, col2, col3 = st.columns([2.0, 3.5, 2.5])

    total_MD = load_profile["Pload (MW)"].sum()
    is_scheme_valid = df[scheme].notna() & (df[scheme] != "nan") & (df[scheme] != "#na")
    
    total_scheme_ls = df.loc[is_scheme_valid, "Pload (MW)"].sum()

    if total_MD == 0:
        pct_scheme_ls = 0
    else:
        pct_scheme_ls = (total_scheme_ls / total_MD) * 100

    zones = ["North", "KlangValley", "South", "East"]
    zone_data = {
        zone: load_profile_metric(df=df, zone=zone, scheme=scheme)
        for zone in zones
    }
    zone_MD = {
        zone: load_profile_metric(df=load_profile, zone=zone)
        for zone in zones
    }

    with col1:
        st.metric(
            label=f"Total {scheme} Load Quantum",
            value=f"{int(total_scheme_ls):,} MW",
        )
        st.metric(
            label=f"% {scheme} Quantum Over MD",
            value=f"{pct_scheme_ls:.1f}%",
        )

    with col2:
        col2a, col2b = st.columns(2)

        with col2a:
            zone_metric(col2a, "North", zone_data, zone_MD)
            zone_metric(col2a, "KlangValley", zone_data, zone_MD)

        with col2b:
            zone_metric(col2b, "South", zone_data, zone_MD)
            zone_metric(col2b, "East", zone_data, zone_MD)
    
    with col3:
        pass





        # ls_data = {
        #     'Region': ["North", "KlangValley", "South", "East"],
        #     'Type': ['ls', 'ls', 'ls', 'ls'],
        #     "MW": [int(zone_data.get("North")), int(zone_data.get("KlangValley")), int(zone_data.get("South")), int(zone_data.get("East"))]
        # }
        # df_ls = pd.DataFrame(ls_data)

        # ls_data = {
        #     'Region': ["North", "KlangValley", "South", "East"],
        #     'Type': ['balance_load', 'balance_load', 'balance_load', 'balance_load'],
        #     "MW": [int(zone_data.get("North")), int(zone_data.get("KlangValley")), int(zone_data.get("South")), int(zone_data.get("East"))]
        # }

        # fig = px.pie(
        #     df,
        #     values='Load Shed',
        #     names='Regional',
        #     title='Regional Load Shedding Quantum Distribution'
        # )
        # fig.update_traces(
        #     hole=.6,
        #     hoverinfo="label+percent+value",
        #     textinfo='value+label',
        # )
        # fig.update_layout(
        #     title=dict(
        #         font=dict(size=15, color="#2E86C1"),
        #         y=0.015,
        #         x=0.5,
        #         xanchor="center",
        #         xref="paper",
        #     ),
        #     showlegend=False,
        #     height=230,
        #     width=250,
        #     margin=dict(t=0, b=25, l=3, r=3),
        #     annotations=[
        #         dict(
        #             text=f"{int(total_scheme_ls):,} MW",
        #             x=0.5,
        #             y=0.5,
        #             font_size=20,
        #             showarrow=False,
        #             align="center",
        #         )
        #     ],
        # )
        # st.plotly_chart(fig, width="stretch")


def zone_metric(col, zone_name, zone_data, zone_MD):
    ls = int(zone_data[zone_name])
    md = int(zone_MD[zone_name])
    pct = (ls / md) * 100

    with col:
        st.metric(
            label=f"{zone_name} Load Shedding",
            value=f"{ls:,} MW",
        )
        st.markdown(
            f"<p style='margin-top:-25px; color:gray; font-size:13px;'>{pct:.1f}% of total {zone_name} MD</p>",
            unsafe_allow_html=True,
        )


def show_temporary_message(message_type, message, duration=3):
    placeholder = st.empty()

    if message_type == 'info':
        placeholder.info(message)
    elif message_type == 'success':
        placeholder.success(message)
    elif message_type == 'warning':
        placeholder.warning(message)

    time.sleep(duration)

    placeholder.empty()