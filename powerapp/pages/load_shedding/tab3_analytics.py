import streamlit as st
from applications.load_shedding.helper import columns_list
from pages.load_shedding.tab3a_ls_barStacked import lshedding_barStacked
from pages.load_shedding.tab3b_ls_table import ls_table
from pages.load_shedding.tab3c_flag_assignment import ls_assignment_flag
from pages.load_shedding.helper import find_latest_assignment


def ls_analytics_main():
    ls_analytics()
    ls_assignment_flag()


def ls_analytics():
    st.subheader("Load Sheddding Assignment Analytics")

    chart_container = st.container()
    table_container = st.container()
 

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    masterlist = ls_obj.ls_assignment_masterlist()

    with chart_container:
        schemes, input2, _ = st.columns(3)

        with schemes:
            ls_scheme_cols = [
                c for c in masterlist.columns if any(k in c for k in ls_obj.LOADSHED_SCHEME)
            ]
            latest_assignment = find_latest_assignment(ls_scheme_cols)
            ufls_latest = [
                ls for ls in latest_assignment if 'ufls' in str(ls).lower()]

            schemes = st.multiselect(
                "Scheme", options=ls_scheme_cols, default=ufls_latest[0], key="ls_analytics_scheme"
            )

        filters = {
            "scheme": schemes,
        }

        filtered_data = ls_obj.filtered_data(filters=filters, df=masterlist)

        if filtered_data.empty:
            st.info("No active load shedding assignment found.")
            return

    with table_container:
        for target_col in schemes:
            clean_scheme_df = filtered_data.dropna(subset=[target_col])
            if not clean_scheme_df.empty:
                lshedding_barStacked(clean_scheme_df, target_col)
                ls_table(clean_scheme_df, target_col)
                st.divider()
            else:
                st.warning(f"Data for {target_col} is empty after filtering.")

