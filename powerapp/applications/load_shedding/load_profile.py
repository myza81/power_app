import streamlit as st
import pandas as pd


def load_profile_metric(df, zone, scheme=None):
    df_filtered = df

    if scheme is not None:
        is_scheme_valid = (
            df[scheme].notna() & (df[scheme] != "nan") & (df[scheme] != "#na")
        )
        df_filtered = df[is_scheme_valid]

    zone_MW = df_filtered.groupby(
        ["zone"],
        as_index=False,
    ).agg({"Load (MW)": "sum"}
          )
    return zone_MW.loc[zone_MW["zone"] == zone]["Load (MW)"].to_numpy().sum()


def df_search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df

    df_str = df.astype(str)
    mask = df_str.apply(
        lambda row: row.str.contains(query, case=False, na=False).any(), axis=1
    )

    return df[mask]
