import streamlit as st 



def data_plotting():
    st.write("Data Plotting")

    if "uploaded_file" in st.session_state:
        for subs in st.session_state["uploaded_file"]:
            print(subs)