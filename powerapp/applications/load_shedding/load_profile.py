import pandas as pd


# def load_profile_enrichment(df):
#     state_name = {"LANGKAWI": "KEDAH", "WPKL": "KL", "TGANU": "TERENGGANU"}
#     state = {
#         "North": ["Kedah", "Perlis", "P Pinang", "Perak"],
#         "KlangValley": ["KL", "Selangor"],
#         "South": ["NS", "Johor", "Melaka"],
#         "East": ["Kelantan", "Terengganu", "Pahang"],
#     }
#     df["Zone Name"] = df["Zone Name"].replace(state_name)
#     df["Id"] = df["Id"].astype(str)

#     zone_state = {}
#     for zone, states in state.items():
#         for state in states:
#             zone_state[state.upper()] = zone
#     df["zone"] = df["Zone Name"].str.upper().map(zone_state)

#     return df


def load_profile_metric(df, zone, scheme=None):
    df_filtered = df
    if scheme is not None:

        is_scheme_valid = df[scheme].notna() & (df[scheme] != "nan") & (df[scheme] != "#na")
        df_filtered = df[is_scheme_valid]
    zone_MW = df_filtered.groupby(
        ["zone"],
        as_index=False,
    ).agg(
        {
            "Pload (MW)": "sum",
            "Qload (Mvar)": "sum",
        }
    )
    return zone_MW.loc[zone_MW["zone"] == zone]["Pload (MW)"].to_numpy().sum()


def df_search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df

    df_str = df.astype(str)
    mask = df_str.apply(
        lambda row: row.str.contains(query, case=False, na=False).any(), axis=1
    )

    return df[mask]
