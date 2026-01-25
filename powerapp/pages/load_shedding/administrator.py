import streamlit as st
from datetime import date
from applications.data_processing.save_to import export_to_excel
from pages.load_shedding.helper import remove_duplicates_keep_nan


def update_meta():
    st.header("Administrator Panel")

    ls_obj = st.session_state["loadshedding"]
    subsmeta_container = st.container()

    if ls_obj is None:
        st.warning("Please upload a load profile to access administrator features.")
        return

    with subsmeta_container:
        st.write("Download the current substation metadata.")
        subs_meta = ls_obj.profile_metadata()
        subs_meta =  remove_duplicates_keep_nan(subs_meta, ["mnemonic", "substation_name"])

        c10, _ = st.columns([3, 1])

        with c10:
            filename_input, export_btn = st.columns([2, 1])

            with filename_input:
                filename = st.text_input(
                    label="Filename",
                    value=f"subs_metadata_{date.today().strftime('%d%m%Y')}",
                    label_visibility="collapsed",
                    key="subsmeta_filename",
                )
            with export_btn:
                save_btn = st.download_button(
                    label="Export to Excel",
                    data=export_to_excel(subs_meta),
                    file_name=f"{filename}.xlsx",
                    width="stretch",
                    key="subsmeta_export_btn",
                )

            st.dataframe(subs_meta)
            state = subs_meta["state"].unique().tolist()
            st.write("States in the metadata:", state)
            gm_subzone = subs_meta["gm_subzone"].unique().tolist()
            st.write("GM Subzones in the metadata:", gm_subzone)
            st.write()
