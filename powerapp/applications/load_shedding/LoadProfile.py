import pandas as pd
from typing import Dict, List
from applications.load_shedding.load_profile import load_profile_metric


class LoadProfile:
    STATE_MAPPING: Dict[str, str] = {
        "LANGKAWI": "KEDAH",
        "WPKL": "KUALA LUMPUR",
        "TGANU": "TERENGGANU",
        "P PINANG": "PULAU PINANG",
        "NS": "NEGERI SEMBILAN"
    }

    ZONE_STRUCTURE: Dict[str, List[str]] = {
        "North": ["Kedah", "Perlis", "Pulau Pinang", "Perak"],
        "KlangValley": ["Kuala Lumpur", "Selangor"],
        "South": ["Negeri Sembilan", "Johor", "Melaka"],
        "East": ["Kelantan", "Terengganu", "Pahang"],
    }

    def __init__(self, load_profile: pd.DataFrame):
        self.raw_load_profile = load_profile
        self.zone_map = {
            state.upper(): zone
            for zone, states in self.ZONE_STRUCTURE.items()
            for state in states
        }
        self.df = self._process_data()

    def _process_data(self) -> pd.DataFrame:
        """Internal helper to clean and structure the load profile data."""
        df = self.raw_load_profile.copy()
        df.columns = df.columns.str.replace(' ', '')

        df = df.drop(columns=["ZoneNum", "OwnerNum",
                     "InService"], errors='ignore')
        df = df.rename(columns={
            "BusNumber": "bus_number",
            "BusName": "bus_name",
            "Mnemonic": "mnemonic",
            "Id": "feeder_id",
            "ZoneName": "state",
            "OwnerName": "owner",
            "Pload(MW)": "Load (MW)"
        })

        df["state"] = df["state"].str.upper().replace(self.STATE_MAPPING)
        df["owner"] = df["owner"].replace({"TNB T": "Grid"})
        df["feeder_id"] = df["feeder_id"].astype(str)
        ## tukar guna substation list - substation.xlsx
        df["zone"] = df["state"].map(self.zone_map)

        return df

    def totalMW(self) -> int:
        """Returns the total system load from the processed dataframe."""
        return int(self.df["Load (MW)"].sum())

    def regional_loadprofile(self, zone: str) -> int:
        """Returns the load for a specific region using the helper utility."""
        regional_load = load_profile_metric(self.df, zone)
        return int(regional_load)

