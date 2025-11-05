import pandas as pd
import re
from io import BytesIO


def find_correct_header(uploaded_file, required_keywords, optional_groups=None):
    """
    Detect correct header row by checking for given keywords (case-insensitive).

    Parameters
    ----------
    uploaded_file : UploadedFile
        File object from Streamlit uploader.
    required_keywords : list[str]
        List of keywords that must exist in the header.
    optional_groups : list[list[str]], optional
        List of keyword groups where at least one keyword from each group must appear.
        Example: [["voltage", "current", "mw"]]

    Returns
    -------
    tuple:
        (raw_df, correct_df)
        or
        (raw_df, ValueError, missing_keywords)
    """
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
            """Check if keyword partially matches column using substring or simple pattern."""
            # Allow small variations like underscores, spaces, or parentheses
            pattern = re.sub(r"[^a-z0-9]", ".*", keyword.lower())
            return re.search(pattern, col) is not None

        # --- Check required keywords ---
        missing_required = []
        for k in required_lower:
            # print('required_lower', k)
            if not any(is_partial_match(k, col) for col in columns):
                missing_required.append(k)

        # --- Check optional keyword groups ---
        missing_groups = []
        for group in optional_groups:
            group_lower = [g.lower() for g in group]
            # print('group_lower', group_lower)
            if not any(
                any(is_partial_match(g, col) for col in columns)
                for g in group_lower
            ):
                missing_groups.append(group_lower)

        has_all_required = len(missing_required) == 0
        has_valid_groups = len(missing_groups) == 0

        # print('missing_groups', missing_groups)

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
    """Read CSV or Excel data from in-memory bytes."""
    file_buffer = BytesIO(file_bytes)
    skip_row = list(range(skiprow_index + 1)) if skiprow_index >= 0 else None

    if file_name.lower().endswith(".csv"):
        return pd.read_csv(file_buffer, skiprows=skip_row)
    elif file_name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_buffer, skiprows=skip_row)
    else:
        raise ValueError(
            "Unsupported file type. Please upload a CSV or Excel file.")


# import pandas as pd
# from io import BytesIO

# def find_correct_header(uploaded_file, keywords):
#     # --- Step 1: Load file ---
#     file_bytes = uploaded_file.read()
#     raw_df = read_raw_data(file_bytes, uploaded_file.name)

#     keywords_lower = set(k.lower() for k in keywords)

#     def has_keywords(df):
#         """Check if any keyword appears in column names."""
#         return any(
#             any(k in str(col).lower() for k in keywords_lower) for col in df.columns
#         )

#     # 1️⃣ Check if the first read already has correct headers
#     if has_keywords(raw_df):
#         return raw_df, raw_df

#     # 2️⃣ Try different possible header rows
#     for tested_index in range(10):
#         correct_df = read_raw_data(file_bytes, uploaded_file.name, tested_index)
#         if has_keywords(correct_df):
#             # print(f"Detected header row at line {tested_index + 1}")
#             return raw_df, correct_df

#     # 3️⃣ If no keyword found in first 10 lines, raise error
#     return (raw_df, ValueError("No header containing specified keywords found in first 10 rows."))


# def read_raw_data(file_bytes, file_name, skiprow_index=-1):
#     """Read CSV or Excel data from in-memory bytes."""
#     # Always wrap bytes in a fresh BytesIO to avoid pointer issues
#     file_buffer = BytesIO(file_bytes)

#     # Define skiprows properly
#     skip_row = list(range(skiprow_index + 1)) if skiprow_index >= 0 else None

#     if file_name.lower().endswith(".csv"):
#         return pd.read_csv(file_buffer, skiprows=skip_row)
#     elif file_name.lower().endswith((".xlsx", ".xls")):
#         return pd.read_excel(file_buffer, skiprows=skip_row)
#     else:
#         raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


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
