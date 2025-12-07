import streamlit as st

# -- page setup --#
home = st.Page(
    page="pages/home/homepage.py",
    title="Main Page",
    icon=":material/home:",
    default=True,
)
page_1 = st.Page(
    page="pages/generator_response/home_gen_response.py",
    title="Generator Response",
    icon=":material/solar_power:",
)
page_2 = st.Page(
    page="pages/load_shedding/home_main.py",
    title="Load Shedding",
    icon=":material/lightning_stand:",
)


pg = st.navigation(pages=[home, page_1, page_2])
pg.run()
