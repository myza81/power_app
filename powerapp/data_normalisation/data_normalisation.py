import pandas as pd
from ..calculation.mw_mvar import calculate_mw_mvar


def phasor_data(df):
    clean_df = df.copy()
    timestamp = clean_df['Date']+' '+clean_df['Time (Asia/Singapore)']
    clean_df['Timestamp'] = pd.to_datetime(
        timestamp, format="%m/%d/%y %H:%M:%S.%f")
    calc = calculate_mw_mvar(clean_df, source_data='phasor')
    clean_df['MW'] = calc.get('MW')
    clean_df['Mvar'] = calc.get('Mvar')

    return clean_df
