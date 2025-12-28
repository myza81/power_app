import streamlit as st

def custom_metric(label, value, delta_text=None, value_color="#2E86C1", delta_color="#2ECC71", delta_bgcolor="#0E3421"):
    if delta_text:
        st.markdown(
            f"""
            <div style="font-family: sans-serif; margin-bottom: 10px">
                <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
                <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value}</p>
                <div style="
                    background-color: {delta_bgcolor}; 
                    color: {delta_color}; 
                    padding: 2px 12px; 
                    border-radius: 20px; 
                    display: inline-block; 
                    font-size: 14px; 
                    font-weight: 600; 
                    margin-top: 0px;">
                    {delta_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="font-family: sans-serif; margin-bottom: 10px">
                <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
                <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
