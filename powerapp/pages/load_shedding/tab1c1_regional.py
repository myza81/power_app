import pandas as pd
import streamlit as st
import plotly.express as px
from css.streamlit_css import vertical_center_css


def regional_lshedding_stacked(df, scheme):

    loadprofile = st.session_state["loadprofile"]
    load_df = loadprofile.df
    load_df_grp = load_df[["zone", "Pload (MW)"]].groupby(
        ["zone"],
        as_index=False,
    ).agg({"Pload (MW)": "sum"})

    ls_operstage = df[[scheme, "zone", "Pload (MW)"]]
    ls_operstage_grp = ls_operstage.groupby(
        [scheme, "zone"],
        as_index=False,
    ).agg({"Pload (MW)": "sum"})
    ls_operstage_grp = ls_operstage_grp.rename(
        columns={"Pload (MW)": "Load Shedding Quantum"})
    ls_operstage_grp_sum = ls_operstage_grp[["zone", "Load Shedding Quantum"]].groupby(
        ["zone"]).agg({"Load Shedding Quantum": "sum"}).reset_index()

    zone_df = pd.merge(
        ls_operstage_grp_sum,
        load_df_grp,
        on='zone',
        how='left'
    )[["zone", "Load Shedding Quantum", "Pload (MW)"]]

    zone_df['Remaining Load Quantum'] = zone_df['Pload (MW)'] - \
        zone_df['Load Shedding Quantum']

    df_melted = zone_df.melt(
        id_vars=['zone'],
        value_vars=['Load Shedding Quantum', 'Remaining Load Quantum'],
        var_name='load_type',
        value_name='mw'
    )

    # st.markdown(vertical_center_css, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 0.1, 2])

    with col1:
        fig_shed = px.bar(
            df_melted,
            x="zone",
            y='mw',
            color='load_type',
            color_discrete_map={
                'Load Shedding Quantum': 'red',
                'Remaining Load Quantum': 'lightgray'
            },
            title="Regional Load Shedding Proportion"
        )

        fig_shed.update_layout(
            title={
                'text': "Regional Load Breakdown: Shedding vs. Balance",
                'font': {
                    'size': 18,
                    'family': 'Arial'
                },
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title=None,
            yaxis_title="Demand (MW)",
            height=400,
            width=600,
            legend_title_text=''
        )

        st.plotly_chart(fig_shed, width='content')

    with col3:
        total_load = loadprofile.totalMW()
        total_ls = zone_df["Load Shedding Quantum"].sum()
        ls_pct = int(total_ls/total_load * 100)
        st.markdown(
            f"<p style='margin-top:30px; font-size:18px; font-weight: 600; font-family: Arial'>Total Load Shedding Quantum for {scheme}:</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='margin-top:-20px; color:#2E86C1; font-size:25px; font-weight: 600'>{total_ls:,.0f} MW ({ls_pct}%)</p>",
            unsafe_allow_html=True,
        )

        zone_list = zone_df["zone"]
        for zone in zone_list:
            zone_load = loadprofile.regional_loadprofile(zone)
            zone_ls = zone_df.loc[zone_df["zone"] ==
                                  zone]["Load Shedding Quantum"].values[0]
            zone_ls_pct = int(zone_ls/zone_load * 100)

            st.markdown(
                f"<p style='margin-top:-10px; font-size:14px;'>Load Shedding Quantum for {zone}:</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='margin-top:-20px; color:#2E86C1; font-size:22px; font-weight: 600'>{zone_ls:,.0f} MW ({zone_ls_pct}%)</p>",
                unsafe_allow_html=True,
            )
