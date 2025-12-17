import pandas as pd
from typing import List, Optional, Sequence, Tuple, Any, Union, Set


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


def scheme_col_sorted(
    df: pd.DataFrame,
    ls_column: Union[str, Set[str]],
    sort_seqcol: Optional[list] = None,
) -> pd.DataFrame:
    col_scheme = ls_column

    # 1. Determine the primary column if a set is provided (original logic kept)
    if isinstance(ls_column, set):
        length_scheme = {col: len(df[df[col].notna()]) for col in ls_column}
        col_scheme = max(length_scheme, key=lambda k: length_scheme[k])

    # 2. Filter and create the sequence column
    df_filtered = df[df[col_scheme].notna()].copy()

    # Assuming the sequence is always the 2nd part after splitting by "_" (e.g., "A_10_X" -> 10)
    try:
        df_filtered["seq_order"] = (
            df_filtered[col_scheme].str.split("_", expand=True).iloc[:, 1].astype(int)
        )
    except Exception as e:
        # Handle cases where the split might not result in 2 parts or conversion fails
        print(f"Error creating seq_order column: {e}")
        return df_filtered.sort_values(by=col_scheme)  # Fallback sort

    # 3. Define the sorting hierarchy

    # Primary sort column is always 'seq_order'
    sorted_cols = ["seq_order"]

    # Primary sort direction is always Ascending (True)
    sorted_bool = [True]

    if sort_seqcol:
        # Add secondary sort columns and their ascending direction (True by default)
        sorted_cols.extend(sort_seqcol)
        sorted_bool.extend(
            [True] * len(sort_seqcol)
        )  # Assumes all secondary sorts are Ascending

    # 4. Perform the single, correct sort operation
    # This ensures seq_order is the highest priority, followed by any secondary columns
    df_sorted = df_filtered.sort_values(by=sorted_cols, ascending=sorted_bool)

    # 5. Clean up and return
    df_sorted = df_sorted.drop(columns=["seq_order"])

    return df_sorted
