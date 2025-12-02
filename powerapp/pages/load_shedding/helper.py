import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any
from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric
)


def display_ls_metrics(scheme, df, load_profile):
    
    col3_1, col3_2 = st.columns(2)

    total_mw = load_profile["Pload (MW)"].sum()
    total_scheme_ls = df.loc[df[scheme].notna(), "Pload (MW)"].sum()
    
    if total_mw == 0:
        pct_scheme_ls = 0
    else:
        pct_scheme_ls = int((total_scheme_ls / total_mw) * 100)

    zones = ["North", "KlangValley", "South", "East"]
    zone_data = {
        zone: load_profile_metric(df=df, zone=zone, scheme=scheme)
        for zone in zones
    }
    
    with col3_1:
        st.metric(
            label=f"Total {scheme} Load Quantum",
            value=f"{int(total_scheme_ls):,} MW",
        )
        st.metric(
            label=f"% {scheme} Quantum Over MD",
            value=f"{pct_scheme_ls:.0f}%",
        )
        
    with col3_2:
        col3_2a, col3_2b = st.columns(2)
        
        with col3_2a:
            st.metric(
                label=f"{zones[0]} Load Shedding",
                value=f"{int(zone_data[zones[0]]):,} MW",
            )
            st.metric(
                label=f"{zones[1]} Load Shedding",
                value=f"{int(zone_data[zones[1]]):,} MW",
            )
        with col3_2b:
            st.metric(
                label=f"{zones[2]} Load Shedding",
                value=f"{int(zone_data[zones[2]]):,} MW",
            )
            st.metric(
                label=f"{zones[3]} Load Shedding",
                value=f"{int(zone_data[zones[3]]):,} MW",
            )
    st.divider()
    