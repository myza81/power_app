import streamlit as st
import pandas as pd
from io import BytesIO


def export_to_excel(df: pd.DataFrame, sheet_name: str = 'Sheet1') -> BytesIO:
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data


