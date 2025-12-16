import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from css.streamlit_css import vertical_center_css
from applications.load_shedding.helper import scheme_col_sorted


def lshedding_analytics(df, scheme):
    col1, col2, col3 = st.columns([2, 0.1, 2])
    col4, col5, col6 = st.columns([2, 0.1, 2])

    with col1:
        load_type_pie(df, scheme)
    with col3:
        find_spesific_load(df, scheme)
    with col4:
        overlap_operating_critical_list(df, scheme)

    st.divider()


def load_type_pie(df, scheme):
    ls_operstage = df[["ls_dp", "Pload (MW)"]]
    ls_operstage_grp = ls_operstage.groupby(
        ["ls_dp"],
        as_index=False,
    ).agg({"Pload (MW)": "sum"})

    ls_operstage_grp = ls_operstage_grp.rename(
        columns={"Pload (MW)": "Load Shed Quantum (MW)"})
    
    total_ls_quantum = ls_operstage_grp["Load Shed Quantum (MW)"].sum()

    st.markdown(
        f"<p style='margin-top:30px; font-size:18px; font-weight: 750; font-family: Arial'>{scheme} Assignment by Load Type</p>",
        unsafe_allow_html=True,
    )

    fig = px.pie(
        ls_operstage_grp,
        values='Load Shed Quantum (MW)',
        names='ls_dp',
        title=' '
    )
    fig.update_traces(
        hole=.5,
        hoverinfo="label+percent+value",
        # textinfo='value+percent+label',
        texttemplate="<b>%{label}</b><br>" +
        "%{value:,.0f} MW"+ "(%{percent})",
        textfont_size=12,
        textposition='auto',
    )
    fig.update_layout(
        title=dict(
            font=dict(size=15),
            y=0.015,
            x=0.5,
            xanchor="center",
            xref="paper",
        ),
        showlegend=False,
        height=230,
        width=250,
        margin=dict(t=0, b=30, l=3, r=3),
        annotations=[
            dict(
                text=f"{total_ls_quantum:,.0f} MW",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
                align="center",
            )
        ],
    )

    st.plotly_chart(fig, width="stretch")


def find_spesific_load(df, scheme):
    assignment_id_list = df["assignment_id"].unique()
    assignment_id = st.multiselect(label="Find Assignment Load Quantum",
                                   options=assignment_id_list, key=f"{scheme}_assignment_quantum")
    total_load = []

    for id in assignment_id:
        mw = df.loc[df["assignment_id"] == id]["Pload (MW)"].sum()
        total_load.append(mw)

    quantum = sum(total_load)
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Total Load Quantum :</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='margin-top:-20px; color:#2E86C1; font-size:30px; font-weight: 700'>{quantum:,.1f} MW</p>",
        unsafe_allow_html=True,
    )


def overlap_operating_critical_list(df, scheme):
    
    oper_stage = df[[scheme, "Pload (MW)"]].groupby(
        [scheme],
        as_index=False
    ).agg({"Pload (MW)": "sum"})

    df["critical_list"] = df["critical_list"].replace('nan', np.nan)
    critical_list = df.loc[df["critical_list"].notna()]
    critical_list_clean = critical_list[[scheme, "Pload (MW)"]].groupby(
        [scheme],
        as_index=False
    ).agg({"Pload (MW)": "sum"})
    critical_list_clean = critical_list_clean.rename(columns={"Pload (MW)": "Critical Load"})

    merged_critical = pd.merge(
        oper_stage,
        critical_list_clean,
        on=scheme,
        how="left"
    )
    merged_critical["Non-critical Load"] =  merged_critical["Pload (MW)"] -  merged_critical["Critical Load"].fillna(0)
    merged_critical = merged_critical.drop(columns=["Pload (MW)"], axis=1)

    df_melted = merged_critical.melt(
        id_vars=[scheme],
        value_vars=["Critical Load", "Non-critical Load"],
        var_name="Type",
        value_name="Quantum (MW)"
    )
    df_melted = scheme_col_sorted(df_melted, scheme)

    fig_shed = px.bar(
            df_melted,
            x=scheme,
            y="Quantum (MW)",
            color='Type',
            color_discrete_map={
                'Critical Load': 'red',
                'Non-critical Load': "#DFE6E3"
            },
            title=f"{scheme} Assignment Vs Critical Load"
        )

    fig_shed.update_layout(
        title={
            'font': {
                'size': 18,
                'family': 'Arial'
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        height=450,
        width=600,
        legend_title_text='',
        xaxis_title=None,
        yaxis_title="Demand (MW)",
    )

    st.plotly_chart(fig_shed, width='content')
    
def overlap_within_ls(df, scheme):
    pass

