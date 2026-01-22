import streamlit as st
import pandas as pd
from datetime import date
from pages.load_shedding.helper import process_display_data, show_temporary_message
from applications.data_processing.save_to import export_to_excel
from applications.load_shedding.helper import scheme_col_sorted


def ls_assignment_comparison():
    st.subheader("Load Shedding Scheme: Historical Bay Assignment Changes")

    input_container = st.container()
    dataframe_container = st.container()
    export_btn_container = st.container()

    with input_container:
        input1, input2, _ = st.columns(3)

        ls_obj = st.session_state.get("loadshedding")

        if not ls_obj:
            st.error("Load shedding data not found in session state.")
            return

        master_df = ls_obj.ls_assignment_masterlist().copy()

        base_scheme_cols = [
            c for c in master_df.columns if any(k in c for k in ls_obj.LOADSHED_SCHEME)
        ]

        with input1:
            review_year_ref = st.selectbox(
                "Reference LS Scheme [Newest]", options=base_scheme_cols, key="assign_comparison_ref"
            )

        ref_scheme_cols = [
            c for c in base_scheme_cols
            if c.startswith(review_year_ref[:4]) and c != review_year_ref
        ]

        with input2:
            review_year_prev = st.selectbox(
                "Comparison LS Scheme [Previous]", options=ref_scheme_cols, key="assign_comparison_base"
            )
    
    with dataframe_container:
        if review_year_prev and review_year_ref:
            df = process_display_data(
                master_df, ls_obj.pocket_relay(
                ), [review_year_prev, review_year_ref]
            )

            df = df.dropna(
                subset=[review_year_prev, review_year_ref], how='all')
            df['Changes'] = df.apply(comparison_logic, axis=1, args=(
                review_year_prev, review_year_ref))

            df = scheme_col_sorted(
                df, set([review_year_ref]), ["dp_type", "assignment_id"], keep_nulls=True
            )

            cols_order = [review_year_ref] + [
                "Zone",
                "Subzone",
                "State",
                "Mnemonic",
                "Substation",
                "Voltage Level",
                "Breaker(s)",
                "Feeder Assignment",
                "assignment_id",
                "dp_type",
                "Changes",
            ]
            st.dataframe(
                df.reindex(columns=cols_order), width="content", hide_index=True
            )
    
    with export_btn_container:
        btn, _ = st.columns([3, 1])

        with btn:
            filename_input, export_btn = st.columns([2, 1])

            with filename_input:
                filename = st.text_input(
                    label="Filename",
                    value=f"{'_'.join([review_year_prev, review_year_ref])}_LS_Assignment_{date.today().strftime('%d%m%Y')}",
                    label_visibility="collapsed",
                    key="ls_assignment_comparison_filename",
                )
            with export_btn:
                save_btn = st.download_button(
                    label="Export to Excel",
                    data=export_to_excel(df),
                    file_name=f"{filename}.xlsx",
                    width="stretch",
                    key="ls_assignment_comparison_export_btn",
                )
                if save_btn:
                    show_temporary_message(
                        "info", f"Saved as {filename}.xlsx")
                    

def comparison_logic(row, from_col, to_col):
    from_col = row[from_col]
    to_col = row[to_col]

    # Both values are NaN
    if pd.isna(from_col) and pd.isna(to_col):
        return

    elif pd.notna(from_col) and pd.isna(to_col):
        return 'Defeated/Removed'

    elif pd.isna(from_col) and pd.notna(to_col):
        return 'New Assignment'

    # Both have values and they're similar
    elif pd.notna(from_col) and pd.notna(to_col) and from_col == to_col:
        return 'No Change'

    # Both have values but they're different
    elif pd.notna(from_col) and pd.notna(to_col) and from_col != to_col:
        return f'{from_col} --> {to_col}'
