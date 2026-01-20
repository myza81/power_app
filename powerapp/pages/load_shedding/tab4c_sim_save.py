import re
import streamlit as st
import pandas as pd
from datetime import date


def col_sim_validation(ls_colname):
    col_pattern = r'^\d{4}(?:v\d+)?$'
    valid_col_name = re.match(col_pattern, ls_colname)

    if valid_col_name:
        return False
    return True


def save_sim_data(df_sim, ls_colname, review_year, container):

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    try:
        scheme = review_year.split("_")[0]
    except:
        container.error("Invalid review year format.")
        return

    scheme_files = {
        "UFLS": (ls_obj.ufls_assignment, ls_obj.ufls_filepath),
        "UVLS": (ls_obj.uvls_assignment, ls_obj.uvls_filepath),
        "EMLS": (ls_obj.emls_assignment, ls_obj.emls_filepath),
    }

    if scheme not in scheme_files:
        container.error("Invalid scheme.")
        return

    excel_file, file_path = scheme_files[scheme]

    header = [str(col).lower() for col in excel_file.columns]
    column_exists = ls_colname in header
    if not column_exists:
        # New column - save directly
        data_saved(container, excel_file, ls_colname, df_sim, file_path)
        return

    existing_ls = [col for col in header if re.match(r'^\d{4}$', col)]
    current_year = date.today().year

    if ls_colname in existing_ls and int(ls_colname) < current_year:
        container.error("❌ Cannot overwrite existing assignment!")
    else:
        with container:
            warning_container = st.container()
            confirmation_container = st.container()

            with warning_container:
                st.warning(f"'{ls_colname}' already exists. Overwrite?")

            with confirmation_container:
                proceed_btn, cancel_btn, _, _, = st.columns([2, 2, 2, 2])

                with proceed_btn:
                    st.button(
                        label=f"✅ Yes, Overwrite",
                        type="secondary",
                        on_click=data_saved,
                        args=(container, excel_file,
                              ls_colname, df_sim, file_path),
                        key=f"save_btn_{ls_colname}",
                        width="stretch"
                    )

                with cancel_btn:
                    if st.button(
                        label="❌ No, Cancel",
                        key=f"cancle_btn_{ls_colname}",
                        width="stretch"
                    ):
                        st.rerun()


def data_saved(container, df_excel, ls_colname, df_sim, file_path):

    KEY_COL = "assignment_id"

    try:
        if KEY_COL not in df_sim.columns or KEY_COL not in df_excel.columns:
            container.error(f"Missing key column: {KEY_COL}")
            return

        df_sim = df_sim.set_index(KEY_COL)
        df_excel = df_excel.set_index(KEY_COL)

        common_cols = df_excel.columns.intersection(df_sim.columns)
        df_excel.update(df_sim[common_cols])

        new_cols = df_sim.columns.difference(df_excel.columns)
        for col in new_cols:
            df_excel[col] = df_sim[col]

        new_keys = df_sim.index.difference(df_excel.index)
        if not new_keys.empty:
            df_to_append = df_sim.loc[new_keys]

            df_excel = pd.concat([df_excel, df_to_append], sort=False)

        df_excel_final = df_excel.dropna(
            how='all', subset=df_excel.columns).reset_index()

        df_excel_final.to_excel(file_path, index=False, engine='openpyxl')

        container.success(f"✅ Data saved successfully!")

    except Exception as e:
        container.error(f"❌ Error saving data: {str(e)}")
