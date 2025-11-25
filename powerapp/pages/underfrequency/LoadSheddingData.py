import pandas as pd

class LoadSheddingData:
    def __init__(
        self, 
        load_profile: pd.DataFrame, 
        masterlist_relay: pd.DataFrame
    ):
        self.load_profile = load_profile
        self.masterlist_relay = masterlist_relay

        self.masterlist_load = self.masterlist_relay.merge(
            self.load_profile,
            left_on=["Mnemonic", "Assigned_Feeders"],
            right_on=["Mnemonic", "Id"],
            how="inner",
        )[
            [
                "GM_Subzone",
                "Geo_Region",
                "Substation",
                "Mnemonic",
                "Assigned_Feeders",
                "Pload (MW)",
                "TripGroup_id",
            ]
        ]
        self.assigned_ls = self.masterlist_load.loc[self.masterlist_load["TripGroup_id"].notna()]
        self.quantum_assigned_ls = self.assigned_ls["Pload (MW)"].sum()
        self.available_quantum_ls = self.available_quantum()

    def assigned_quantum_filter_by_group_id(self, group_id: str):
        group_list = self.assigned_ls[self.assigned_ls["TripGroup_id"] == group_id]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Group Load for {group_id}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def assigned_quantum_filter_by_GMSubzone(self, subzone: str):
        group_list = self.assigned_ls[self.assigned_ls["GM_Subzone"] == subzone]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Group Load for {subzone}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def assigned_quantum_filter_by_geo_loc(self, geo_loc: str):
        group_list = self.assigned_ls[self.assigned_ls["Geo_Region"] == geo_loc]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Group Load for {geo_loc}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def assigned_quantum_filter_by_substation(self, substation: str):
        group_list = self.assigned_ls[self.assigned_ls["Mnemonic"] == substation]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Group Load for {substation}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def available_quantum(self):
        return (
            self.masterlist_load.assign(
                priority=self.masterlist_load["TripGroup_id"].notna()
            )
            .sort_values(
                by=["Mnemonic", "Assigned_Feeders", "priority"],
                ascending=[True, True, False],  # keep True (not NaN) first
            )
            .drop_duplicates(subset=["Mnemonic", "Assigned_Feeders"], keep="first")
            .drop(columns="priority")
        )

    def available_quantum_filter_by_GMSubzone(self, subzone: str):
        group_list = self.available_quantum_ls[
            self.available_quantum_ls["GM_Subzone"] == subzone
        ]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Available Load for {subzone}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def available_quantum_filter_by_geo_loc(self, geo_loc: str):
        group_list = self.available_quantum_ls[
            self.available_quantum_ls["Geo_Region"] == geo_loc
        ]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Available Load for {geo_loc}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load

    def available_quantum_filter_by_substation(self, substation: str):
        group_list = self.available_quantum_ls[
            self.available_quantum_ls["Mnemonic"] == substation
        ]
        quantum_grp_load = group_list["Pload (MW)"].sum()
        print(f"Total Available Load for {substation}: {quantum_grp_load} MW")
        return group_list, quantum_grp_load


if __name__ == "__main__":

    load_profile_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/2025_psse_load_profile.xlsx"
    masterlist_relay_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/db_masterlist_ls_relay.xlsx"
    group_tripId = "nlai_proi_kjng_nuni"
    subzone = "KL"
    geo_loc = "KlangValley"
    substation = 'TJID'

    pd.set_option("display.max_rows", None)

    load_profile = pd.read_excel(load_profile_path)
    masterlist_relay = pd.read_excel(masterlist_relay_path)
    ufls = LoadSheddingData(
        load_profile=load_profile, masterlist_relay=masterlist_relay
    )

    # all_load
    all_load = ufls.masterlist_load
    all_load.to_excel(r"C:/Users/fairizat/Desktop/masterlist.xlsx", index=False)

    # existing assigned
    grp_trip_list, quantum = ufls.assigned_quantum_filter_by_group_id(
        group_id=group_tripId
    )
    gmsubzone_list, subzone_quantum = ufls.assigned_quantum_filter_by_GMSubzone(
        subzone=subzone
    )
    geoloc_list, geoloc_quantum = ufls.assigned_quantum_filter_by_geo_loc(
        geo_loc=geo_loc
    )
    subs_list, subs_quantum = ufls.assigned_quantum_filter_by_substation(
        substation=substation
    )

    # available ls - assigned + non-assigned
    avail_geoloc, geoloc_availquantum = ufls.available_quantum_filter_by_geo_loc(
        geo_loc=geo_loc
    )
    avail_subzone, subzone_availquantum = ufls.available_quantum_filter_by_GMSubzone(
        subzone=subzone
    )
    avail_subs, subs_availquantum = ufls.available_quantum_filter_by_substation(
        substation=substation
    )
    # print(grp_trip_list)
    # print(gmsubzone_list)
    # print(geoloc_list)
    # print(subs_list)
    # print(ufls.quantum_assigned_ls)
    print(all_load)
    # print("Available load by subzone", avail_subzone)
    # print('Available load by Substation', avail_subs)
    # print('Available ls', ufls.available_quantum_ls)
