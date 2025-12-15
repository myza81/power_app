import pandas as pd 
from applications.load_shedding.load_profile import (
    load_profile_metric,
    df_search_filter,
)

class LoadProfile:
    def __init__(self, load_profile):
        self.loadprofile = load_profile
        self.STATE = {
            "North": ["Kedah", "Perlis", "P Pinang", "Perak"],
            "KlangValley": ["KL", "Selangor"],
            "South": ["NS", "Johor", "Melaka"],
            "East": ["Kelantan", "Terengganu", "Pahang"],
        }
        self.df = self.load_df()

    def load_df(self):
        df = self.loadprofile.copy()
        
        state_name = {"LANGKAWI": "KEDAH", "WPKL": "KL", "TGANU": "TERENGGANU"}
        
        df["Zone Name"] = df["Zone Name"].replace(state_name)
        
        df["Id"] = df["Id"].astype(str)

        zone_state = {}
        for zone, states in self.STATE.items():
            for state in states:
                zone_state[state.upper()] = zone
        df["zone"] = df["Zone Name"].str.upper().map(zone_state)
 
        return df
    
    def totalMW(self):
        load_df = self.load_df()
        total_mw = load_df["Pload (MW)"].sum()

        return int(total_mw)

    
    def regional_loadprofile(self, zone):
        regional_load = load_profile_metric(self.load_df(), zone)
        return int(regional_load)



