import pandas as pd
import numpy as np


class LoadShedding:

    def __init__(
        self,
        load_profile: pd.DataFrame,
        ufls_assignment: pd.DataFrame,
        uvls_assignment: pd.DataFrame,
        ls_load_local: pd.DataFrame,
        ls_load_pocket: pd.DataFrame,
        dn_excluded_list: pd.DataFrame,
        log_defeated: pd.DataFrame,
        relay_location: pd.DataFrame,
        substation_masterlist: pd.DataFrame,
        ufls_setting: pd.DataFrame,
        uvls_setting: pd.DataFrame,
    ):

        self.load_profile = load_profile.copy()
        self.local_load = ls_load_local.copy()
        self.pocket_load = ls_load_pocket.copy()
        self.combined_all_load = pd.concat(
            [self.local_load, self.pocket_load], ignore_index=True
        )

        self.masterlist_load = self.combined_all_load.merge(
            self.load_profile,
            left_on=["mnemonic", "feeder_id"],
            right_on=["Mnemonic", "Id"],
            how="inner",
        )[
            [
                "mnemonic",
                "feeder_id",
                "group_trip_id",
                "Pload (MW)",
                "Qload (Mvar)",
            ]
        ]

        self.load_by_subs = self.masterlist_load.groupby(
            ["mnemonic", "group_trip_id"], as_index=False
        )[["Pload (MW)", "Qload (Mvar)"]].sum()

        self.dn_excluded_list = dn_excluded_list.copy()

        self.ufls_assignment = ufls_assignment.copy()
        self.ufls_assignment.columns = self.ufls_assignment.columns.astype(str)
        self.uvls_assignment = uvls_assignment.copy()
        self.uvls_assignment.columns = self.uvls_assignment.columns.astype(str)

        self.ufls = SchemeReview(
            scheme="UFLS",
            load_by_subs=self.load_by_subs,
            dn_excluded_list=dn_excluded_list.copy(),
            ls_assignment=self.ufls_assignment,
            log_defeated=log_defeated.copy(),
            relay_location=relay_location.copy(),
            substation_masterlist=substation_masterlist.copy(),
            ls_setting=ufls_setting.copy()
        )

        self.uvls = SchemeReview(
            scheme="UFLS",
            load_by_subs=self.load_by_subs,
            dn_excluded_list=dn_excluded_list.copy(),
            ls_assignment=self.uvls_assignment,
            log_defeated=log_defeated.copy(),
            relay_location=relay_location.copy(),
            substation_masterlist=substation_masterlist.copy(),
            ls_setting=uvls_setting.copy(),
        )


class SchemeReview:
    def __init__(
        self,
        scheme: str,
        load_by_subs: pd.DataFrame,
        dn_excluded_list: pd.DataFrame,
        ls_assignment: pd.DataFrame,
        log_defeated: pd.DataFrame,
        relay_location: pd.DataFrame,
        substation_masterlist: pd.DataFrame,
        ls_setting: pd.DataFrame,
    ):
        self.name = scheme  # "UFLS" or "UVLS"
        self.load_by_subs = load_by_subs
        self.ls_assignment = ls_assignment

    def review_by_year(self, review_year: str) -> pd.DataFrame:

        ufls_review_df = self.ls_assignment[self.ls_assignment[review_year].notna()][
            ["group_trip_id", review_year]
        ]

        load_by_grpId = self.load_by_subs.groupby(
            ["group_trip_id"], as_index=False
        )[["Pload (MW)", "Qload (Mvar)"]].sum()

        review_year_list = ufls_review_df.merge(
            load_by_grpId, on="group_trip_id", how="left"
        )
        return review_year_list

    # def assigned_quantum_filter_by_group_id(self, group_id: str):
    #     group_list = self.assigned_ls[self.assigned_ls["group_trip_id"] == group_id]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Group Load for {group_id}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def assigned_quantum_filter_by_GMSubzone(self, subzone: str):
    #     group_list = self.assigned_ls[self.assigned_ls["GM_Subzone"] == subzone]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Group Load for {subzone}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def assigned_quantum_filter_by_geo_loc(self, geo_loc: str):
    #     group_list = self.assigned_ls[self.assigned_ls["Geo_Region"] == geo_loc]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Group Load for {geo_loc}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def assigned_quantum_filter_by_substation(self, substation: str):
    #     group_list = self.assigned_ls[self.assigned_ls["Mnemonic"] == substation]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Group Load for {substation}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def available_quantum(self):
    #     return (
    #         self.masterlist_load.assign(
    #             priority=self.masterlist_load["group_trip_id"].notna()
    #         )
    #         .sort_values(
    #             by=["Mnemonic", "Assigned_Feeders", "priority"],
    #             ascending=[True, True, False],  # keep True (not NaN) first
    #         )
    #         .drop_duplicates(subset=["Mnemonic", "Assigned_Feeders"], keep="first")
    #         .drop(columns="priority")
    #     )

    # def available_quantum_filter_by_GMSubzone(self, subzone: str):
    #     group_list = self.available_quantum_ls[
    #         self.available_quantum_ls["GM_Subzone"] == subzone
    #     ]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Available Load for {subzone}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def available_quantum_filter_by_geo_loc(self, geo_loc: str):
    #     group_list = self.available_quantum_ls[
    #         self.available_quantum_ls["Geo_Region"] == geo_loc
    #     ]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Available Load for {geo_loc}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load

    # def available_quantum_filter_by_substation(self, substation: str):
    #     group_list = self.available_quantum_ls[
    #         self.available_quantum_ls["Mnemonic"] == substation
    #     ]
    #     quantum_grp_load = group_list["Pload (MW)"].sum()
    #     print(f"Total Available Load for {substation}: {quantum_grp_load} MW")
    #     return group_list, quantum_grp_load


#####################################################################################
if __name__ == "__main__":

    load_profile_2025 = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/2025_load_profile.xlsx"
    dn_excluded_list = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/dn_exluded_list.xlsx"
    ls_load_local = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ls_load_local.xlsx"
    ls_load_pocket = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ls_load_pocket.xlsx"
    relay_location = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/relay_location.xlsx"
    substation_masterlist = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/substation_masterlist.xlsx"
    ufls_assignment = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ufls_assignment.xlsx"
    uvls_assignment = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/uvls_assignment.xlsx"
    ufls_setting = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ufls_setting.xlsx"
    log_defeated_relay = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/log_defeated_relay.xlsx"

    # masterlist_relay_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/db_masterlist_ls_relay.xlsx"

    # input
    group_tripId = "nlai_proi_kjng_nuni"
    subzone = "KL"
    geo_loc = "KlangValley"
    substation = "TJID"

    pd.set_option("display.max_rows", None)

    # read file
    load_profile = pd.read_excel(load_profile_2025)
    ufls_assignment = pd.read_excel(ufls_assignment)
    uvls_assignment = pd.read_excel(uvls_assignment)
    ls_load_local = pd.read_excel(ls_load_local)
    ls_load_pocket = pd.read_excel(ls_load_pocket)
    dn_excluded_list = pd.read_excel(dn_excluded_list)
    log_defeated = pd.read_excel(log_defeated_relay)
    relay_location = pd.read_excel(relay_location)
    substation_masterlist = pd.read_excel(substation_masterlist)
    ufls_setting = pd.read_excel(ufls_setting)

    ls = LoadShedding(
        load_profile=load_profile,
        ufls_assignment=ufls_assignment,
        uvls_assignment=uvls_assignment,
        ls_load_local=ls_load_local,
        ls_load_pocket=ls_load_pocket,
        dn_excluded_list=dn_excluded_list,
        log_defeated=log_defeated,
        relay_location=relay_location,
        substation_masterlist=substation_masterlist,
        ufls_setting=ufls_setting,
        uvls_setting=ufls_setting,
    )

    # all_load
    all_load = ls.masterlist_load
    ufls_review = ls.ufls.review_by_year("2024")
    print(ufls_review)
    # all_load.to_excel(r"C:/Users/fairizat/Desktop/masterlist_25Nov.xlsx", index=False)

    # existing assigned
    # grp_trip_list, quantum = ufls.assigned_quantum_filter_by_group_id(
    #     group_id=group_tripId
    # )
    # gmsubzone_list, subzone_quantum = ufls.assigned_quantum_filter_by_GMSubzone(
    #     subzone=subzone
    # )
    # geoloc_list, geoloc_quantum = ufls.assigned_quantum_filter_by_geo_loc(
    #     geo_loc=geo_loc
    # )
    # subs_list, subs_quantum = ufls.assigned_quantum_filter_by_substation(
    #     substation=substation
    # )

    # # available ls - assigned + non-assigned
    # avail_geoloc, geoloc_availquantum = ufls.available_quantum_filter_by_geo_loc(
    #     geo_loc=geo_loc
    # )
    # avail_subzone, subzone_availquantum = ufls.available_quantum_filter_by_GMSubzone(
    #     subzone=subzone
    # )
    # avail_subs, subs_availquantum = ufls.available_quantum_filter_by_substation(
    #     substation=substation
    # )
    # # print(grp_trip_list)
    # # print(gmsubzone_list)
    # # print(geoloc_list)
    # # print(subs_list)
    # # print(ufls.quantum_assigned_ls)
    # print(all_load)
    # print("Available load by subzone", avail_subzone)
    # print('Available load by Substation', avail_subs)
    # print('Available ls', ufls.available_quantum_ls)
