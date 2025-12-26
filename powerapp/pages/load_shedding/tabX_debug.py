import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
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


def debug():
    loadprofile = st.session_state["loadprofile"]


    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    uvls_assignmnet = loadshedding.uvls_assignment
    emls_assignment = loadshedding.emls_assignment
    ufls_setting = loadshedding.ufls_setting
    uvls_setting = loadshedding.uvls_setting
    subs_metadata = loadshedding.subs_meta

 
    delivery_point = loadshedding.delivery_point


    load_dp = loadshedding.load_dp()
    load_pocket = loadshedding.load_pocket()
    assign_quantum = loadshedding.assignment_loadquantum()
    ls_masterlist = loadshedding.ls_assignment_masterlist()

    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    st.subheader("Debugging Info")

    # st.dataframe(load_dp)
    st.dataframe(assign_quantum)
    # st.dataframe(ls_masterlist)

    # st.dataframe(LS_SCHEME)
    # 

    # st.write("Debug")
