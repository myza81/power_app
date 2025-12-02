import pandas as pd
from typing import List, Optional, Sequence, Tuple, Any


def columns_list(
    df: Optional[pd.DataFrame],
    unwanted_el: Optional[Sequence[str]] = None,
    add_el: Optional[Sequence[Tuple[int, str]]] = None,
) -> List[str]:

    if df is None:
        return []

    cols = df.columns.tolist()

    if unwanted_el:
        cols = [c for c in cols if c not in unwanted_el]

    if add_el:
        for idx, name in add_el:
            idx = max(0, min(idx, len(cols)))
            cols.insert(idx, name)

    return cols


# def load_profile_enrichment(df):
#     state = {
#         "North": ["Kedah", "Langkawi", "Perlis", "P Pinang", "Perak"],
#         "KlangValley": ["WPKL", "Selangor"],
#         "South": ["NS", "Johor", "Melaka"],
#         "East": ["Kelantan", "TGanu", "Pahang"]
#     }
#     zone_state = {}
#     for zone, states in state.items():
#         for state in states:
#             zone_state[state.upper()] = zone
#     df["Zone"] = df["Zone Name"].str.upper().map(zone_state)
#     return df

