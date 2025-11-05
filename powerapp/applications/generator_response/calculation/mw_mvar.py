import numpy as np
import pandas as pd

def calculate_mw_mvar(df: pd.DataFrame, source_data: str = 'phasor'):
  
    required_cols = ["V1 Magnitude", "V1 Angle", "I1 Magnitude", "I1 Angle"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if 'phasor' in source_data:
        V_mag = df["V1 Magnitude"]
        V_ang = np.deg2rad(df["V1 Angle"])
        I_mag = df["I1 Magnitude"]
        I_ang = np.deg2rad(df["I1 Angle"])
    else:
        raise ValueError(f"Unsupported source_data type: {source_data}")

    # Compute apparent power
    S = 3 * V_mag * I_mag * np.exp(1j * (V_ang - I_ang)) / 1e6  # MVA

    # Debug info
    # print("S (first 5):", S[:5])

    # Return as dictionary or DataFrame
    return pd.DataFrame({
        "MW": np.real(S),
        "Mvar": np.imag(S)
    })
