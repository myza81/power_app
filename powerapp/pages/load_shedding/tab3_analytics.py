import streamlit as st
from applications.load_shedding.helper import columns_list
from pages.load_shedding.tab3a_ls_barStacked import lshedding_barStacked
from pages.load_shedding.tab3b_ls_table import ls_table
from pages.load_shedding.tab3c_flag_assignment import ls_assignment_flag


def ls_analytics():
    st.subheader("Load Sheddding Assignment Analytics")

    chart_container = st.container()
    table_container = st.container()
    st.divider()
    flag_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    masterlist = ls_obj.ls_assignment_masterlist()

    with chart_container:
        input1, input2, _ = st.columns(3)

        with input1:
            all_dfs = [
                ls_obj.ufls_assignment,
                ls_obj.uvls_assignment,
                ls_obj.emls_assignment,
            ]
            years = sorted(
                {col for df in all_dfs for col in columns_list(df, ["assignment_id"])},
                reverse=True,
            )
            review_year = st.selectbox(
                "Review Year", options=years, key="ls_dashboard_review_year"
            )

        with input2:
            active_schemes = st.multiselect(
                "Scheme",
                options=ls_obj.LOADSHED_SCHEME,
                default="UFLS",
                key="ls_dashboard_scheme",
            )

        filters = {
            "review_year": review_year,
            "scheme": active_schemes,
        }

        filtered_data = ls_obj.filtered_data(filters=filters, df=masterlist)

        if filtered_data.empty:
            st.info("No active load shedding assignment found.")
            return

        # 4. Processing Schemes
        expected_cols = [f"{s}_{review_year}" for s in active_schemes]
        available_cols = [col for col in expected_cols if col in filtered_data.columns]
        missing_cols = set(expected_cols) - set(available_cols)

    with table_container:
        for target_col in available_cols:
            clean_scheme_df = filtered_data.dropna(subset=[target_col])
            if not clean_scheme_df.empty:
                lshedding_barStacked(clean_scheme_df, target_col)
                ls_table(clean_scheme_df, target_col)
            else:
                st.warning(f"Data for {target_col} is empty after filtering.")

        # 5. Handle Missing Data
        if missing_cols:
            for col in sorted(missing_cols):
                st.info(f"No active assignment found for {col.replace('_', ' ')}.")

    with flag_container:
        ls_assignment_flag()