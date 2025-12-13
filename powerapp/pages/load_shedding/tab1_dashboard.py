import pandas as pd
import streamlit as st
import time
from datetime import date
from typing import List, Optional, Sequence, Any

from applications.load_shedding.helper import (
    columns_list,
    column_data_list,
    scheme_col_sorted,
)
from applications.data_processing.read_data import df_search_filter
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.helper import display_ls_metrics, show_temporary_message

def ls_assignment_dashboard():
        loadshedding = st.session_state["loadshedding"]
        ufls_assignment = loadshedding.ufls_assignment
        masterlist_ls = loadshedding.ls_assignment_masterlist()
        LS_SCHEME = loadshedding.LOADSHED_SCHEME

        st.subheader("Load Sheddding Assignment Dashboard")

        tab1_s2_col1, tab1_s2_col2, tab1_s2_col3 = st.columns(3)

        with tab1_s2_col1:
            review_year_list = columns_list(ufls_assignment, unwanted_el=["assignment_id"])
            review_year_list.sort(reverse=True)
            review_year = st.selectbox(
                label="Review Year", options=review_year_list, key="dashboard_review_year")

        with tab1_s2_col2:
            ls_scheme = st.multiselect(
                label="Scheme", options=LS_SCHEME, default="UFLS", key="dashboard_ls_scheme")
            selected_scheme = LS_SCHEME if ls_scheme == [] else ls_scheme

        filters = {
                "review_year": review_year,
                "scheme": selected_scheme,
                # "op_stage": stage_selected,
                # "zone": zone_selected,
                # "gm_subzone": subzone_selected,
                # "ls_dp": trip_assignment,
            }
        
        filtered_data = loadshedding.filtered_data(
                filters=filters, df=masterlist_ls)
        
        if not filtered_data.empty:

            selected_inp_scheme = [
                f"{scheme}_{review_year}" for scheme in selected_scheme
            ]
        for item in selected_scheme:
            pass
            
            #donut pie for reginal MW 
            #bar chart for MW each stage
            #bar chart for regional MW each stage
            #total local load 
            #total pocket load
            #selection local load by zone
            #selection each pocket