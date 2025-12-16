import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from applications.load_shedding.ufls_setting import UFLS_SETTING

def loadshedding_subset():

    loadshedding = st.session_state["loadshedding"]
    ufls_setting = pd.DataFrame(UFLS_SETTING)
    masterlist_ls = loadshedding.ls_assignment_masterlist()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset Bar</p>",
        unsafe_allow_html=True,
    )

    # selected_inp_scheme = [
    #         f"{scheme}_{review_year}" for scheme in selected_scheme
    #     ]
    
    # oper_stage = df[[scheme, "Pload (MW)"]].groupby(
    #     [scheme],
    #     as_index=False
    # ).agg({"Pload (MW)": "sum"})
    print(isinstance(ufls_setting, pd.DataFrame))

    st.dataframe(ufls_setting)
    col1, col2, col3 = st.columns([2,0.1,2])

    with col1:
        bar_subset()
    with col3:
        circle_subset()

def bar_subset():
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset </p>",
        unsafe_allow_html=True,
    )

def circle_subset():
    st.markdown(
        f"<p style='margin-top:30px; font-size:14px; font-weight: 700; font-family: Arial'>Load Shedding Subset </p>",
        unsafe_allow_html=True,
    )