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


def save_sim_data(sim_df, ls_colname, review_year, container):

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
        data_saved(container, excel_file, ls_colname, sim_df, file_path)
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
                              ls_colname, sim_df, file_path),
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


def data_saved(container, excel_file, ls_colname, sim_df, file_path):
    try:

        excel_id_map = {}
        for idx, value in enumerate(excel_file.iloc[:, 0], start=1):
            if pd.notna(value):
                excel_id_map[str(value).strip()] = idx + 1

        # save_sim_container.write(excel_id_map)
        cols_to_update = [ls_colname]

        container.success(f"✅ Data saved successfully!")

    except Exception as e:
        container.error(f"❌ Error saving data: {str(e)}")
