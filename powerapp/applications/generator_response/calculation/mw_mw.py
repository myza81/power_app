import numpy as np

def calculate_mw_mvar(self):
        V_mag = self.df["V1 Magnitude"]
        V_ang = np.deg2rad(self.df["V1 Angle"])
        I_mag = self.df["I1 Magnitude"]
        I_ang = np.deg2rad(self.df["I1 Angle"])

        # Complex power calculation
        S = 3 * V_mag * I_mag * np.exp(1j * (V_ang - I_ang)) / 1e6  # MVA
        self.df["MW"] = S.real
        self.df["Mvar"] = S.imag