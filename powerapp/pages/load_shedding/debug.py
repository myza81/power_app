import streamlit as st
from applications.data_processing.read_data import read_raw_data
from applications.load_shedding.LoadShedding import LoadShedding
from applications.load_shedding.LoadProfile import LoadProfile


def debug():
    load_profile_uploader = st.sidebar.file_uploader(
        "Choose file", type=["csv", "xlsx", "xls"], key="file_uploader_debug")

    file_bytes = load_profile_uploader.read()
    load_file = read_raw_data(file_bytes, load_profile_uploader.name)
    loadprofile = LoadProfile(load_profile=load_file)
    ls_obj = LoadShedding(load_df=loadprofile.df)

    ufls = ls_obj.ufls_assignment
    dp = ls_obj.delivery_point

    st.write(dp["local_trip_id"])


def trace_cols(df, label):
    st.write(f"🔍 {label}")
    st.write("df id:", id(df))
    st.write("columns:", df.columns.tolist())