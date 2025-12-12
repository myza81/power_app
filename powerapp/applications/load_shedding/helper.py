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


def column_data_list(
    df: Optional[pd.DataFrame],
    column_name: str,
    unwanted_el: Optional[Sequence[Any]] = None,
    add_el: Optional[Sequence[dict]] = None,
) -> List[Any]:

    if df is None or column_name not in df.columns:
        return []

    values = df[column_name].tolist()
    unique_ordered = list(dict.fromkeys(values))

    if unwanted_el:
        unique_ordered = [v for v in unique_ordered if v not in unwanted_el]

    if add_el:
        for el in add_el:
            idx = el.get("idx", 0)
            data = el.get("data")
            idx = max(0, min(idx, len(unique_ordered)))
            unique_ordered.insert(idx, data)

    return unique_ordered


def scheme_col_sorted(df, ls_column):
    col_scheme = ls_column
    if isinstance(ls_column, set):
        length_scheme = {}
        for col in ls_column:
            length_scheme[col] = len(df[df[col].notna()])
        col_scheme = max(length_scheme, key=lambda k: length_scheme[k])

    df_filtered = df[df[col_scheme].notna()].copy()
    df_filtered["seq_order"] = (
        df_filtered[col_scheme].str.split("_", expand=True).iloc[:, 1].astype(int)
    )

    sorted_overlap = df_filtered.sort_values(by="seq_order")
    sorted_overlap = sorted_overlap.drop(columns=["seq_order"], axis=1)

    return sorted_overlap
