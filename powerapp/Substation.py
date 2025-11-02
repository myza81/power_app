import pandas as pd
from pathlib import Path
from .data_normalisation.data_normalisation import phasor_data


class Substation:
    def __init__(self, name: str, filepath: str, source_data: str):
        self.name = name
        self.filepath = Path(filepath)
        self.source_data = source_data
        self.raw_data: pd.DataFrame | None = None
        self.cleaned_data: pd.DataFrame | None = None

        self.load_data()

    def load_data(self):
        try:
            if (self.source_data == 'phasor'):
                self.raw_data = pd.read_csv(
                    self.filepath, skiprows=[0], header=0)
                self.cleaned_data = phasor_data(self.raw_data)

            elif (self.source_data == 'ben'):
                self.raw_data = pd.read_csv(self.filepath)

            print(f"[INFO] Loaded {self.name}: {self.raw_data.shape[0]} rows")
            print(self.cleaned_data)

        except Exception as e:
            raise RuntimeError(f"Failed to load CSV for {self.name}: {e}")
