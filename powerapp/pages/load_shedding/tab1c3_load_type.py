import streamlit as st
import plotly.express as px
from css.streamlit_css import vertical_center_css


def lshedding_pie_chart(df, scheme):
    col1, col2, col3 = st.columns([2, 0.1, 2])

    with col1:
        load_type_pie(df, scheme)
    with col3:
        find_spesific_load(df, scheme)
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

    fig = px.pie(
        ls_operstage_grp,
        values='Load Shed Quantum (MW)',
        names='ls_dp',
        title='Load Type'
    )
    fig.update_traces(
        hole=.5,
        hoverinfo="label+percent+value",
        # textinfo='value+percent+label',
        texttemplate="<b>%{label}</b><br>" +
        "%{value:,.0f} MW<br>" +
        "(%{percent})",
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
    st.metric(
        label="Total Load Quantum:",
        value=f"{quantum:,.1f} MW",

    )
