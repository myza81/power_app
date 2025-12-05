import streamlit as st
from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric,
)


def display_ls_metrics(scheme, df, load_profile):
    
    col3_1, col3_2 = st.columns(2)

    total_MD = load_profile["Pload (MW)"].sum()
    total_scheme_ls = df.loc[df[scheme].notna(), "Pload (MW)"].sum()
    
    if total_MD == 0:
        pct_scheme_ls = 0
    else:
        pct_scheme_ls = int((total_scheme_ls / total_MD) * 100)

    zones = ["North", "KlangValley", "South", "East"]
    zone_data = {
        zone: load_profile_metric(df=df, zone=zone, scheme=scheme)
        for zone in zones
    }
    zone_MD = {
        zone: load_profile_metric(df=load_profile, zone=zone)
        for zone in zones
    }
    
    with col3_1:
        st.metric(
            label=f"Total {scheme} Load Quantum",
            value=f"{int(total_scheme_ls):,} MW",
        )
        st.metric(
            label=f"% {scheme} Quantum Over MD",
            value=f"{pct_scheme_ls:.1f}%",
        )
        
    with col3_2:
        col3_2a, col3_2b = st.columns(2)
        
        with col3_2a:
                zone_metric(col3_2a, "North", zone_data, zone_MD)
                zone_metric(col3_2a, "KlangValley", zone_data, zone_MD)
        
        with col3_2b:
            zone_metric(col3_2b, "South", zone_data, zone_MD)
            zone_metric(col3_2b, "East", zone_data, zone_MD)
        
    st.divider()
    
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