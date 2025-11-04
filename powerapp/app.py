import streamlit as st

#-- page setup --#
main = st.Page(
    page="pages/main.py",
    title="Main Page",
    icon=":material/home:",
    default=True

)
project_1_page = st.Page(
    page="pages/generator_response.py",
    title="Generator Response",
    icon=":material/solar_power:"

)

pg = st.navigation(pages=[main, project_1_page])

pg.run()