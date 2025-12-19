import pandas as pd
from applications.load_shedding.load_profile import (
    load_profile_metric,
    df_search_filter,
)


class LoadProfile:
    def __init__(self, load_profile):
        self.loadprofile = load_profile
        self.ZONE = {
            "North": ["Kedah", "Perlis", "P Pinang", "Perak"],
            "KlangValley": ["KL", "Selangor"],
            "South": ["NS", "Johor", "Melaka"],
            "East": ["Kelantan", "Terengganu", "Pahang"],
        }
        self.df = self.load_df()

    def load_df(self):
        df = self.loadprofile.copy()
        df.columns = df.columns.str.replace(' ', '')
        df = df.drop(columns=["ZoneNum", "OwnerNum", "InService"])
        df = df.rename(columns={
            "BusNumber": "bus_number",
            "BusName": "bus_name",
            "Mnemonic": "mnemonic",
            "Id": "feeder_id",
            "ZoneName": "locality",
            "OwnerName": "owner",
            "Pload(MW)": "Load (MW)"

        })

        state_name = {"LANGKAWI": "KEDAH", "WPKL": "KL", "TGANU": "TERENGGANU"}
        df["locality"] = df["locality"].replace(state_name)
        owner_name = {"TNB T": "Grid"}
        df["owner"] = df["owner"].replace(owner_name)
        df["feeder_id"] = df["feeder_id"].astype(str)

        zone_state = {}
        for zone, states in self.ZONE.items():
            for state in states:
                zone_state[state.upper()] = zone
        df["zone"] = df["locality"].str.upper().map(zone_state)

        return df

    def totalMW(self):
        load_df = self.load_df()
        total_mw = load_df["Load (MW)"].sum()

        return int(total_mw)

    def regional_loadprofile(self, zone):
        regional_load = load_profile_metric(self.load_df(), zone)
        return int(regional_load)
    


