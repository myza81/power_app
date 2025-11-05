import streamlit as st 
from applications.generator_response.data_serialization.read_data import (
    get_key_metric,
)


@st.fragment
def data_preview_fragment(df):
    st.subheader("🧾 Uploaded Raw Data Preview")

    max_rows = len(df)
    rows_to_display = st.slider(
        "Select number of rows to display:",
        min_value=5,
        max_value=max_rows,
        value=min(20, max_rows),
        step=1,
        help="Use this slider to change how many rows of the raw data are visible.",
    )
    st.dataframe(df.head(rows_to_display), width="content")


def data_viewer():
    st.header("⚙️ Key Parameter Metrics")
    metric_display = ["frequency", "mw"]

    (raw_df, correct_df) = st.session_state["current_file_data"]

    for metric in metric_display:
        result = get_key_metric(
            df=correct_df,
            metric=metric,
            time_column="time (asia/singapore)",
        )

        if result:
            col_f1, col_f2 = st.columns(2)
            col_f1.metric(
                f"Lowest {result.get('metric')}",
                f"{result.get('lowest'):.3f} Hz",
                f"{result.get('lowest_at_time')}",
            )
            col_f2.metric(
                f"Highest {result.get('metric')}",
                f"{result.get('highest'):.3f} Hz",
                f"{result.get('highest_at_time')}",
            )

    # --- Data Preview ---
    data_preview_fragment(raw_df)
