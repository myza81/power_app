import pandas as pd
from io import BytesIO

def find_correct_header(uploaded_file, keywords):
    """Try to detect the correct header row by checking for given keywords."""
    # Read file once into memory for repeated reads
    file_bytes = uploaded_file.read()

    # Read first attempt (no skiprows)
    raw_df = read_raw_data(file_bytes, uploaded_file.name)

    keywords_lower = set(k.lower() for k in keywords)

    def has_keywords(df):
        """Check if any keyword appears in column names."""
        return any(
            any(k in str(col).lower() for k in keywords_lower) for col in df.columns
        )

    # 1️⃣ Check if the first read already has correct headers
    if has_keywords(raw_df):
        return raw_df, raw_df

    # 2️⃣ Try different possible header rows
    for tested_index in range(10):
        correct_df = read_raw_data(file_bytes, uploaded_file.name, tested_index)
        if has_keywords(correct_df):
            # print(f"Detected header row at line {tested_index + 1}")
            return raw_df, correct_df

    # 3️⃣ If no keyword found in first 10 lines, raise error
    raise ValueError("No header containing specified keywords found in first 10 rows.")


def read_raw_data(file_bytes, file_name, skiprow_index=-1):
    """Read CSV or Excel data from in-memory bytes."""
    # Always wrap bytes in a fresh BytesIO to avoid pointer issues
    file_buffer = BytesIO(file_bytes)

    # Define skiprows properly
    skip_row = list(range(skiprow_index + 1)) if skiprow_index >= 0 else None

    if file_name.lower().endswith(".csv"):
        return pd.read_csv(file_buffer, skiprows=skip_row)
    elif file_name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_buffer, skiprows=skip_row)
    else:
        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


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
