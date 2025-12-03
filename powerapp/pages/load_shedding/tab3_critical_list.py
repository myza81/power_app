import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any

# from applications.load_shedding.data_processing.LoadShedding import (
#     LoadShedding,
#     LS_Data,
# )
from applications.load_shedding.data_processing.helper import columns_list
from applications.load_shedding.data_processing.load_profile import (
    load_profile_metric,
    df_search_filter,
)
from pages.load_shedding.helper import display_ls_metrics

def critical_list():
    load_profile_df = st.session_state["load_profile"] 
    loadshedding = st.session_state["loadshedding"]
    defeated_list = loadshedding.warning_list()

    if isinstance(defeated_list, pd.DataFrame):
        search_query = st.text_input(
                label="Search for a Keyword:",
                placeholder="Enter your search keyword here...", 
                key="warning_list_search_box",
            )
        filtered_df = df_search_filter(defeated_list, search_query)
        st.dataframe(
            filtered_df, 
            column_order=["group_trip_id", "date", "remark", "category"],
            width="stretch"
        )        
        
    else:
        st.write(defeated_list)
    





