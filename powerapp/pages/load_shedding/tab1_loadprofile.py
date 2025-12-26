import streamlit as st
from pages.load_shedding.helper import create_donut_chart, create_bar_chart
from pages.load_shedding.tab1a_loadprofile_data import loadprofile_data
from css.streamlit_css import custom_metric


def loadprofile_main():
    loadprofile_dashboard()
    st.divider()
    loadprofile_data()


def loadprofile_dashboard():
    loadprofile = st.session_state["loadprofile"]
    load_df = loadprofile.df
    total_mw = loadprofile.totalMW()

    col_stateBar, col_pie1, col_metrics = st.columns([2, 2, 2])

    with col_pie1:
        zone_ls = load_df.groupby(["zone"], as_index=False)["Load (MW)"].sum()
        create_donut_chart(
            df=zone_ls,
            values_col="Load (MW)",
            names_col="zone",
            title="Regional Zone Load Demand",
            key=f"pie_zone_grid_load_profile",
            annotations=f"{total_mw:,.0f} MW",
            height=300,
            margin=dict(t=80, b=20, l=10, r=10)
        )
    
    with col_stateBar:
        states = load_df[["state", "Load (MW)"]].groupby("state").agg({"Load (MW)": "sum"}).reset_index()
        create_bar_chart(
            df=states,
            x_col="state",
            y_col="Load (MW)",
            title="State Load Demand",
            y_label="Demand (MW)",
            height=400,
            color_discrete_sequence=["#26b41f"],
            key=f"state_load_demand"
        )

    with col_metrics:
        st.markdown("")
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