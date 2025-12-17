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

def find_latest_assignment(data_list):
    latest_entries = {}
    parts = []
    for item in data_list:
        parts = item.split('_')

        if len(parts) == 2:
            category = parts[0]
            try:
                year = int(parts[1])
            except ValueError:
                return []

            if category not in latest_entries or year > latest_entries[category]['year']:
                latest_entries[category] = {
                    'year': year,
                    'full_name': item
                }

    latest_selection = [entry['full_name'] for entry in latest_entries.values()]
    return latest_selection
