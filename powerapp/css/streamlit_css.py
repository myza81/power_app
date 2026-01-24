import streamlit as st


def custom_metric(
    label,
    value1,
    value2=None,
    delta_text=None,
    value_color="#2E86C1",
    delta_color="#2ECC71",
    delta_bgcolor="#0E3421"
):
    if value2 is None:
        if delta_text:
            st.markdown(
                f"""
                <div style="font-family: sans-serif; margin-bottom: 10px">
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
                    <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value1}</p>
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
                    <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value1}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        if delta_text:
            st.markdown(
                f"""
                <div style="font-family: sans-serif; margin-bottom: 10px">
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
                    <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value1}</p>
                    <p style="font-size: 14px; font-weight: 700; color: {value_color}; margin: 0px;">{value2}</p>
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
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div style="font-family: sans-serif; margin-bottom: 10px">
                    <p style="font-size: 16px; font-weight: 600; margin-bottom: 0px;">{label}</p>
                    <p style="font-size: 32px; font-weight: 700; color: {value_color}; margin: 0px;">{value1}</p>
                    <p style="font-size: 14px; font-weight: 700; color: {value_color}; margin: 0px;">{value2}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def custom_metric_one_line(
    title,
    values_obj,
    title_size="16px",
    title_color="#6b7280",
    title_weight=600,
    item_size="18px",
    item_color="#6b7280",
    item_weight=600,
    value_size="32px",
    value_weight=600,
    value_color="#2E86C1",
    margin="0"
):

    items_html = "".join([
        f'<div style="display: block; margin: {margin};"> '
        f'<span style="font-size: {item_size}; font-weight: {item_weight}; '
        f'color: {item_color}; margin-right: 5px;">{item}:</span>'
        f'<span style="font-size: {value_size}; font-weight: {value_weight}; '
        f'color: {value_color}; margin-right: 10px;">{value}</span></div>'
        for item, value in values_obj.items()
    ])

    return st.markdown(
        f"""
        <div style="font-family: sans-serif; margin-bottom: 10px;">
            <div style="font-size: {title_size}; font-weight: {title_weight}; color: {title_color}; margin-bottom: 5px;">{title}</div>
            <div style="display: block; margin: {margin};">
                {items_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def custom_metric_two_line(
    title,
    values_obj1,
    values_obj2,
    title_size="16px",
    title_color="#6b7280",
    title_weight=600,
    item_size="18px",
    item_color="#6b7280",
    item_weight=600,
    value1_size="32px",
    value1_weight=600,
    value1_color="#2E86C1",
    value2_size="32px",
    value2_weight=600,
    value2_color="#6b7280",
    margin="0"
):

    line1_html = "".join([
        f'<div style="display: block; margin: {margin};"> '
        f'<span style="font-size: {item_size}; font-weight: {item_weight}; '
        f'color: {item_color}; margin-right: 5px;">{item}:</span>'
        f'<span style="font-size: {value1_size}; font-weight: {value1_weight}; '
        f'color: {value1_color}; margin-right: 10px;">{value}</span></div>'
        for item, value in values_obj1.items()
    ])
    line2_html = "".join([
        f'<div style="display: block; margin: {margin};"> '
        f'<span style="font-size: {item_size}; font-weight: {item_weight}; '
        f'color: {item_color}; margin-right: 5px;">{item}</span>'
        f'<span style="font-size: {value2_size}; font-weight: {value2_weight}; '
        f'color: {value2_color}; margin-right: 10px;">{value}</span></div>'
        for item, value in values_obj2.items()
    ])

    st.markdown(
        f"""
        <div style="font-family: sans-serif; margin-bottom: 10px;">
            <div style="font-size: {title_size}; font-weight: {title_weight}; color: {title_color}; margin-bottom: 5px;">{title}</div>
            <div style="display: block; margin: {margin};">
                <span>{line1_html}</span>
                <span>{line2_html}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def scrollable_text_box(text, height=300, bg_color="#7C8492", text_color="#303339", font_size="13px"):
    st.markdown(f"""
    <div style="
        height: {height}px;
        overflow-y: auto;
        background-color: {bg_color};
        color: {text_color};
        padding: 5px 15px;
        border-radius: 5px;
        border: 1px solid #d3d3d3;
        font-size: {font_size};
        font-family: Consolas', 'Monaco', 'Courier New', monospace;
        white-space: pre-wrap;
    ">{text}</div>
    """, unsafe_allow_html=True)

