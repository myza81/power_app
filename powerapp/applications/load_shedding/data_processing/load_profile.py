import pandas as pd
from typing import List, Optional, Sequence, Tuple, Any


def load_profile_enrichment(df):
    state_name = {"LANGKAWI": "KEDAH", "WPKL": "KL", "TGANU": "TERENGGANU"}
    state = {
        "North": ["Kedah", "Perlis", "P Pinang", "Perak"],
        "KlangValley": ["KL", "Selangor"],
        "South": ["NS", "Johor", "Melaka"],
        "East": ["Kelantan", "Terengganu", "Pahang"],
    }
    df["Zone Name"] = df["Zone Name"].replace(state_name)
    df["Id"] = df["Id"].astype(str)

    zone_state = {}
    for zone, states in state.items():
        for state in states:
            zone_state[state.upper()] = zone
    df["zone"] = df["Zone Name"].str.upper().map(zone_state)

    return df


def load_profile_metric(df, zone, scheme=None):
    df_filtered = df
    if scheme is not None:
        df_filtered = df[df[scheme].notna()]
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


# def df_stage_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
#     print(query)
#     if not query:
#         return df

#     # 1. Identify Target Columns
#     target_stage_names = ["UFLS", "UVLS", "EMLS"]
#     stage_cols = [col for col in df.columns if col in target_stage_names]

#     # Check if any stage columns were found
#     if not stage_cols:
#         print("Warning: No columns starting with 'stage_' found in DataFrame.")
#         return df

#     # 2. Prepare Search Terms
#     # Split the query by commas, strip whitespace, and handle case
#     search_terms = [term.strip().lower() for term in query.split(",") if term.strip()]
#     print("search_terms", search_terms)

#     if not search_terms:
#         return df  # Return original df if query was just commas/spaces

#     # 3. Create a Combined Mask
#     # Initialize a mask of all False values
#     combined_mask = pd.Series([False] * len(df))

#     # Iterate through each search term
#     for term in search_terms:
#         # Create a mask for the current term:
#         # a. Select only the stage columns
#         # b. Convert them to string and lowercase for case-insensitive search
#         # c. Check if the term is contained in ANY of the selected stage columns (axis=1)
#         term_mask = (
#             df[stage_cols]
#             .astype(str)
#             .apply(lambda col: col.str.lower().str.contains(term, na=False))
#             .any(axis=1)
#         )

#         # Combine the new term mask with the existing mask using OR (|)
#         # A row is True if it matches the current term OR any previous terms
#         combined_mask = combined_mask | term_mask

#     # Return the DataFrame filtered by the combined mask
#     return df[combined_mask]
