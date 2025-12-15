import streamlit as st

# -- css --#
st.markdown(
    """
        <style>
        /* Title text (the label) */
        /* [data-testid="stMarkdownContainer"] > div {
            font-size: 22px; 
            font-weight: 300;
            color: #2E86C1; 
        } */

        [data-testid="stWidgetLabel"] > [data-testid="stMarkdownContainer"] > p {
            font-size: 15px; 
            */font-weight: 300;*/
            */color: #2E86C1; */
        }
    
        /* Title text (the label) */
        [data-testid="stMetricLabel"] > div {
            font-size: 22px;
        }

        /* Value text (the big number) */
        [data-testid="stMetricValue"] > div {
            font-size: 20px;   
            font-weight: 600;
            color: #2E86C1; 
        }

        /* Delta text (the +/- value) */
        [data-testid="stMetricDelta"] > div {
            font-size: 18px; 
        }
        div[data-testid="stDataFrame"] .ag-cell {
            /* Use flexbox to control alignment */
            display: flex !important;
            /* Vertically center the content */
            align-items: center !important; 
            /* Optionally, horizontally center the content */
            justify-content: center !important; 
        }
        /* If you only want to align the header content */
        div[data-testid="stDataFrame"] .ag-header-cell-text {
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)



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
