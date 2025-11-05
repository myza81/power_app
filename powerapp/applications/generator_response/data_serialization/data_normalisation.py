import pandas as pd

from powerapp.applications.generator_response.calculation.mw_mvar import calculate_mw_mvar


def get_riched_df(df, source_data):
    if source_data == "phasor":
        return phasor_data(df, source_data)
    elif source_data == "ben":
        return


def phasor_data(df, source_data):
    clean_df = df.copy()
    timestamp = clean_df['Date']+' '+clean_df['Time (Asia/Singapore)']
    clean_df['Timestamp'] = pd.to_datetime(
        timestamp, format="%m/%d/%y %H:%M:%S.%f")
    calc = calculate_mw_mvar(clean_df, source_data)
    clean_df['MW'] = calc.get('MW')
    clean_df['Mvar'] = calc.get('Mvar')

    return clean_df
