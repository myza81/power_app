import pandas as pd
import re
from io import BytesIO


def find_correct_header(uploaded_file, required_keywords, optional_groups=None):
    # --- Step 1: Load file ---
    file_bytes = uploaded_file.read()
    raw_df = read_raw_data(file_bytes, uploaded_file.name)

    required_lower = [k.lower() for k in required_keywords]
    optional_groups = optional_groups or []

    # --- Helper to check keyword presence ---
    def check_keywords(df):
        columns = [str(c).lower().strip() for c in df.columns]
        # print("columns", columns)

        def is_partial_match(keyword, col):
            pattern = re.sub(r"[^a-z0-9]", ".*", keyword.lower())
            return re.search(pattern, col) is not None

        # --- Check required keywords ---
        missing_required = []
        for k in required_lower:
            if not any(is_partial_match(k, col) for col in columns):
                missing_required.append(k)

        # --- Check optional keyword groups ---
        missing_groups = []
        for group in optional_groups:
            group_lower = [g.lower() for g in group]
            if not any(
                any(is_partial_match(g, col) for col in columns)
                for g in group_lower
            ):
                missing_groups.append(group_lower)

        has_all_required = len(missing_required) == 0
        has_valid_groups = len(missing_groups) == 0

        return has_all_required and has_valid_groups, missing_required, missing_groups

    # --- Step 2: Try initial read ---
    ok, miss_req, miss_groups = check_keywords(raw_df)
    if ok:
        return raw_df, raw_df, None

    # --- Step 3: Try skipping first few rows ---
    for skip_i in range(10):
        df = read_raw_data(file_bytes, uploaded_file.name, skip_i)
        ok, miss_req, miss_groups = check_keywords(df)
        if ok:
            return raw_df, df, None

    # --- Step 4: Return with error and missing info ---
    missing_keywords = miss_req.copy()
    # flatten optional missing groups
    for grp in miss_groups:
        missing_keywords.extend(grp)

    return raw_df, ValueError("Missing required or equivalent keywords."), missing_keywords


def read_raw_data(file_bytes, file_name, skiprow_index=-1):
    file_buffer = BytesIO(file_bytes)
    skip_row = list(range(skiprow_index + 1)) if skiprow_index >= 0 else None

    if file_name.lower().endswith(".csv"):
        return pd.read_csv(file_buffer, skiprows=skip_row)
    elif file_name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_buffer, skiprows=skip_row)
    else:
        raise ValueError(
            "Unsupported file type. Please upload a CSV or Excel file.")


def get_key_metric(df, metric, time_column):
    metric_cols = [c for c in df.columns if metric in c.lower()]
    time_cols = [c for c in df.columns if time_column in c.lower()]
    time_col = time_cols[0] if time_cols else None

    if len(metric_cols) > 0:
        metric_col = metric_cols[0]
        min_idx = df[metric_col].idxmin()
        max_idx = df[metric_col].idxmax()
        min_time = df.loc[min_idx, time_col] if time_col else "N/A"
        max_time = df.loc[max_idx, time_col] if time_col else "N/A"

        lowest_metric_value = df[metric_col].min()
        highest_metric_value = df[metric_col].max()

        return {
            "metric": metric_col,
            "lowest": lowest_metric_value,
            "lowest_at_time": min_time,
            "highest": highest_metric_value,
            "highest_at_time": max_time,
        }

    return {}


def find_project_root(start_path, folder_name):
    for parent in start_path.parents:
        if parent.name == folder_name:
            return parent
    raise FileNotFoundError(
        f"Could not find a parent directory named '{folder_name}' from {start_path}"
    )


def df_search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df

    df_str = df.astype(str)
    mask = df_str.apply(
        lambda row: row.str.contains(query, case=False, na=False).any(), axis=1
    )

    return df[mask]
