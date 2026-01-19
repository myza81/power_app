import pandas as pd
from typing import List, Optional, Sequence, Tuple, Any, Union, Set
from functools import wraps


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


# def handle_series_input(func):
#     """Decorator to automatically handle Series inputs"""
#     from functools import wraps

#     @wraps(func)
#     def wrapper(df, *args, **kwargs):
#         original_is_series = isinstance(df, pd.Series)
#         original_name = df.name if original_is_series else None

#         if original_is_series:
#             df = df.to_frame(name=original_name or 'value')
#             result = func(df, *args, **kwargs)
#             result = result.iloc[:, 0]
#             result.name = original_name
#             return result
#         return func(df, *args, **kwargs)

#     return wrapper


# # Alternative implementation using decorator
# @handle_series_input
# def scheme_col_sorted(
#     df: pd.DataFrame,
#     ls_column: Union[str, Set[str]],
#     sort_seqcol: Optional[list] = None,
#     keep_nulls: bool = False
# ) -> pd.DataFrame:

#     if df.empty:
#         return df.copy()
    
#     if isinstance(ls_column, str):
#         if ls_column not in df.columns:
#             raise ValueError(f"Column '{ls_column}' not found in DataFrame")
#     elif isinstance(ls_column, set):
#         missing_cols = [col for col in ls_column if col not in df.columns]
#         if missing_cols:
#             raise ValueError(f"Columns {missing_cols} not found in DataFrame")
    
#     col_scheme = ls_column

#     if isinstance(ls_column, set):
#         length_scheme = {col: len(df[df[col].notna()]) for col in ls_column}
#         col_scheme = max(length_scheme, key=lambda k: length_scheme[k])

#     if keep_nulls:
#         df_notna = df[df[col_scheme].notna()].copy()
#         df_isna = df[df[col_scheme].isna()].copy()

#         try:
#             df_notna["seq_order"] = (
#                 df_notna[col_scheme]
#                 .astype(str)
#                 .split("_", expand=True)
#                 .iloc[:, 1]
#                 .astype(int)
#             )
#         except Exception as e:
#             print(f"Error creating seq_order column: {e}")
#             return df_notna.sort_values(by=col_scheme)

#         sorted_cols = ["seq_order"]
#         sorted_bool = [True]

#         if sort_seqcol:
#             sorted_cols.extend(sort_seqcol)
#             sorted_bool.extend([True] * len(sort_seqcol))

#         df_sorted = df_notna.sort_values(by=sorted_cols, ascending=sorted_bool)
#         df_sorted = df_sorted.drop(columns=["seq_order"])

#         result = pd.concat([df_sorted, df_isna], ignore_index=True)
#         return result
    
#     else:
#         df_filtered = df[df[col_scheme].notna()].copy()
#         try:
#             df_filtered["seq_order"] = (
#                 df_filtered[col_scheme].str.split(
#                     "_", expand=True).iloc[:, 1].astype(int)
#             )
#         except Exception as e:
#             print(f"Error creating seq_order column: {e}")
#             return df_filtered.sort_values(by=col_scheme)

#         sorted_cols = ["seq_order"]
#         sorted_bool = [True]

#         if sort_seqcol:
#             sorted_cols.extend(sort_seqcol)
#             sorted_bool.extend(
#                 [True] * len(sort_seqcol)
#             )

#         df_sorted = df_filtered.sort_values(
#             by=sorted_cols, ascending=sorted_bool)

#         df_sorted = df_sorted.drop(columns=["seq_order"])

#         return df_sorted

def handle_series_input(func):
    """Decorator to automatically handle Series inputs"""
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        original_is_series = isinstance(df, pd.Series)
        original_name = df.name if original_is_series else None

        if original_is_series:
            df = df.to_frame(name=original_name or 'value')
            result = func(df, *args, **kwargs)
            
            # Ensure result is not empty before trying to get iloc
            if not result.empty and result.shape[1] > 0:
                result = result.iloc[:, 0]
                result.name = original_name
                return result
            else:
                # Return empty Series if result is empty
                return pd.Series([], name=original_name)
        
        return func(df, *args, **kwargs)

    return wrapper


@handle_series_input
def scheme_col_sorted(
    df: pd.DataFrame,
    ls_column: Union[str, Set[str]],
    sort_seqcol: Optional[list] = None,
    keep_nulls: bool = False
) -> pd.DataFrame:
    """
    Sort DataFrame based on scheme column with format 'prefix_number_suffix'.
    
    Parameters:
    -----------
    df : DataFrame or Series
        Input data
    ls_column : str or set
        Column name or set of column names containing scheme strings
    sort_seqcol : list, optional
        Additional columns to sort by after sequence number
    keep_nulls : bool, default=False
        If True, keep rows with null values in the sorted result (at the end)
        
    Returns:
    --------
    DataFrame or Series sorted by sequence number
    """
    # Handle empty DataFrame
    if df.empty:
        return df.copy()
    
    # Validate ls_column
    if isinstance(ls_column, str):
        if ls_column not in df.columns:
            raise ValueError(f"Column '{ls_column}' not found in DataFrame")
        col_scheme = ls_column
    elif isinstance(ls_column, set):
        # Validate all columns in set exist
        missing_cols = [col for col in ls_column if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns {missing_cols} not found in DataFrame")
        
        # Find column with most non-null values
        length_scheme = {col: len(df[df[col].notna()]) for col in ls_column}
        if not length_scheme:  # All columns are empty
            return df.copy()
        col_scheme = max(length_scheme, key=lambda k: length_scheme[k])
    else:
        raise TypeError(f"ls_column must be str or set, got {type(ls_column)}")
    
    # Validate sort_seqcol columns if provided
    if sort_seqcol:
        missing_sort_cols = [col for col in sort_seqcol if col not in df.columns]
        if missing_sort_cols:
            raise ValueError(f"Sort columns {missing_sort_cols} not found in DataFrame")
    
    if keep_nulls:
        # Separate null and non-null rows
        df_notna = df[df[col_scheme].notna()].copy()
        df_isna = df[df[col_scheme].isna()].copy()
        
        if not df_notna.empty:
            try:
                # Extract sequence number
                split_result = df_notna[col_scheme].astype(str).str.split("_", expand=True)
                if split_result.shape[1] < 2:
                    raise ValueError(f"Column '{col_scheme}' doesn't have expected '_' separator")
                
                df_notna["seq_order"] = split_result.iloc[:, 1].astype(int)
            except Exception as e:
                print(f"Error creating seq_order column: {e}")
                # Return unsorted non-nulls + nulls
                return pd.concat([df_notna, df_isna], ignore_index=True)
            
            # Sort non-null rows
            sorted_cols = ["seq_order"]
            sorted_bool = [True]
            
            if sort_seqcol:
                sorted_cols.extend(sort_seqcol)
                sorted_bool.extend([True] * len(sort_seqcol))
            
            df_sorted = df_notna.sort_values(by=sorted_cols, ascending=sorted_bool)
            df_sorted = df_sorted.drop(columns=["seq_order"])
            
            # Combine sorted non-null rows with null rows at the end
            result = pd.concat([df_sorted, df_isna], ignore_index=True)
            return result
        else:
            # All rows are null, return as-is
            return df.copy()
    
    else:
        # Filter out null rows
        df_filtered = df[df[col_scheme].notna()].copy()
        
        if df_filtered.empty:
            return df_filtered
        
        try:
            split_result = df_filtered[col_scheme].astype(str).str.split("_", expand=True)
            if split_result.shape[1] < 2:
                raise ValueError(f"Column '{col_scheme}' doesn't have expected '_' separator")
            
            df_filtered["seq_order"] = split_result.iloc[:, 1].astype(int)
        except Exception as e:
            print(f"Error creating seq_order column: {e}")
            # Return unsorted (but filtered) DataFrame
            return df_filtered.sort_values(by=col_scheme)
        
        # Sort
        sorted_cols = ["seq_order"]
        sorted_bool = [True]
        
        if sort_seqcol:
            sorted_cols.extend(sort_seqcol)
            sorted_bool.extend([True] * len(sort_seqcol))
        
        df_sorted = df_filtered.sort_values(by=sorted_cols, ascending=sorted_bool)
        df_sorted = df_sorted.drop(columns=["seq_order"])
        
        return df_sorted
    
def scheme_col_sorted1(
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
            df_filtered[col_scheme].str.split(
                "_", expand=True).iloc[:, 1].astype(int)
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
