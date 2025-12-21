import streamlit as st

def custom_metric(label, value, delta_text):
    st.markdown(
        f"""
        <div style="font-family: sans-serif;">
            <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
            <p style="font-size: 32px; font-weight: 700; color: #2E86C1; margin: 0px;">{value}</p>
            <div style="
                background-color: #0E3421; 
                color: #2ECC71; 
                padding: 2px 12px; 
                border-radius: 20px; 
                display: inline-block; 
                font-size: 18px; 
                font-weight: 600; 
                margin-top: 8px;">
                {delta_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )