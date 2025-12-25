import streamlit as st
import plotly.express as px

from applications.load_shedding.helper import scheme_col_sorted
from pages.load_shedding.helper import create_donut_chart, create_stackedBar_chart, get_dynamic_colors, stage_sort


def operating_stages_bar(df, scheme):

    ls_oper_zone = df[[scheme, "zone", "Load (MW)"]].groupby(
        [scheme, "zone"],
        as_index=False,
    ).agg({"Load (MW)": "sum"})

    ls_sorted = scheme_col_sorted(ls_oper_zone, scheme)

    c1, _, c2, _, c3 = st.columns([2, 0.1, 2, 0.1, 2])

    with c1:
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
