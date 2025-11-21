import streamlit as st

st.title("Under-frequency Load Shedding Scheme (UFLS)")

st.set_page_config(layout="wide", page_title="UFLS")

# --- Main UI --- #
st.title("Generator Response")
st.markdown("Use the tabs below to navigate between different views.")
tab1, tab2 = st.tabs(["Data Viewer", "Data Plotting"])

# with tab1:
#     st.write("Upload a CSV or Excel file to view its contents.")
#     uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

#     file_bytes = uploaded_file.read()
#     raw_df = read_raw_data(file_bytes, uploaded_file.name)

#     if raw_df is not None:
#         max_rows = len(raw_df)
#         rows_to_display = st.slider(
#             "Select number of rows to display:",
#             min_value=5,
#             max_value=max_rows,
#             value=min(20, max_rows),
#             step=1,
#             help="Use this slider to change how many rows of the raw data are visible.",
#         )
#         st.dataframe(raw_df.head(rows_to_display), width="content")
