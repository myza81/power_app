import streamlit as st
import plotly.express as px
from css.streamlit_css import vertical_center_css
from applications.load_shedding.helper import scheme_col_sorted


def operating_stages_bar(df, scheme):

    ls_oper_zone = df[[scheme, "zone", "Pload (MW)"]].groupby(
        [scheme, "zone"],
        as_index=False,
    ).agg({"Pload (MW)": "sum"})

    ls_operstage_grp = ls_oper_zone.rename(
        columns={"Pload (MW)": "Load (MW)"})
    ls_sorted = scheme_col_sorted(ls_operstage_grp, scheme)

    col1, col2, col3 = st.columns([2, 0.1, 2])
    with col1:
        fig_shed = px.bar(
            ls_sorted,
            x=scheme,
            y="Load (MW)",
            color="zone",
            title=f"{scheme} Operating Staging and Load Quantum (MW)"
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
            legend_title_text=''
        )

        st.plotly_chart(fig_shed, width='content')

    with col3:
        ls_table = ls_sorted[[scheme, "Load (MW)"]].groupby(
            [scheme],
            as_index=False
        ).agg({"Load (MW)": "sum"})

        ls_table = scheme_col_sorted(ls_table, scheme)
        st.markdown(
            f"<p style='margin-top:30px; font-size:16px; font-weight: 600; font-family: Arial'>{scheme} Operating Staging and Load Quantum Table:</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(ls_table, hide_index=True)
