import streamlit as st
from applications.load_shedding.helper import columns_list
from pages.load_shedding.tab1c1_regional import regional_lshedding_stacked
from pages.load_shedding.tab1c2_operating_stages import operating_stages_bar
from pages.load_shedding.tab1c3_ls_analytics import lshedding_analytics


def ls_dashboard():
    loadshedding = st.session_state["loadshedding"]
    ufls_assignment = loadshedding.ufls_assignment
    masterlist_ls = loadshedding.ls_assignment_masterlist()
    LS_SCHEME = loadshedding.LOADSHED_SCHEME

    st.subheader("Load Sheddding Assignment Analytics")

    tab1_s2_col1, tab1_s2_col2, tab1_s2_col3 = st.columns(3)

    with tab1_s2_col1:
        review_year_list = columns_list(
            ufls_assignment, unwanted_el=["assignment_id"])
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

    available_scheme_set = []
    missing_scheme = []
    if not filtered_data.empty:
        selected_inp_scheme = [
            f"{scheme}_{review_year}" for scheme in selected_scheme
        ]
        missing_scheme = set(selected_inp_scheme).difference(
            set(filtered_data.columns)
        )
        available_scheme_set = set(selected_inp_scheme).intersection(
            set(filtered_data.columns)
        )

    for scheme in available_scheme_set:
        drop_scheme = [ls for ls in available_scheme_set if ls != scheme]
        scheme_df = filtered_data

        if drop_scheme:
            scheme_df = filtered_data.drop(columns=drop_scheme)

        clean_scheme_df = scheme_df.dropna(subset=[scheme])

        regional_lshedding_stacked(clean_scheme_df, scheme)
        operating_stages_bar(clean_scheme_df, scheme)
        lshedding_analytics(clean_scheme_df, scheme)

    if missing_scheme:
        for scheme in missing_scheme:
            st.info(
                f"No active load shedding {scheme} assignment found for the selected filters."
            )
