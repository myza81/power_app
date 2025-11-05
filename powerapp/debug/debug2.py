import pandas as pd
import streamlit as st 

file_name = "UFLS_UVLS_2024_raw_data.xlsx"
file_path = f"D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2024_Review/{file_name}"

df = {}
if file_name.lower().endswith(".csv"):
    df = pd.read_csv(file_path, skiprows=None)
elif file_name.lower().endswith((".xlsx", ".xls")):
    df = pd.read_excel(file_path, skiprows=None)
else:
    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")

print(df)
