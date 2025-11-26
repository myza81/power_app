import pandas as pd
import numpy as np


class SchemeReview:

    def __init__(
        self,
        review_year: str,
        local_load: pd.DataFrame,
        ls_load_pocket: pd.DataFrame,
        load_by_subs: pd.DataFrame,
        dn_excluded_list: pd.DataFrame,
        ls_assignment: pd.DataFrame,
        log_defeated: pd.DataFrame,
        relay_location: pd.DataFrame,
        substation_masterlist: pd.DataFrame,
        ls_setting: pd.DataFrame,
    ):

        self.review_year = review_year
        self.local_load = local_load
        self.load_by_subs = load_by_subs
        self.ls_assignment = ls_assignment
        self.substation_masterlist = substation_masterlist
        self.dn_excluded_list = dn_excluded_list

        self.ls_active = self.ls_active_list()
        self.ls_active_by_dp = self.ls_active_by_dp_list()
        self.ls_active_by_grpId = self.ls_active_by_grpId_list()
        self.dn_excluded_list = self.dn_list()

    def ls_active_list(self) -> pd.DataFrame:
        return self.ls_assignment[
            self.ls_assignment[self.review_year].notna()
        ][["group_trip_id", self.review_year]]

    def ls_active_by_dp_list(self) -> pd.DataFrame:
        review_year_list = pd.merge(
            self.ls_active,
            self.load_by_subs, 
            on="group_trip_id", how="left"
        )
        # print('LS REVIEW LIST', review_year_list)

        with_metadata = pd.merge(
            review_year_list,
            self.substation_masterlist, 
            on="mnemonic", how="left"
        )
        return with_metadata

    def ls_active_by_grpId_list(self) -> pd.DataFrame:
        load_by_grpId = self.load_by_subs.groupby(["group_trip_id"], as_index=False)[
            ["Pload (MW)", "Qload (Mvar)"]
        ].sum()

        review_year_list = pd.merge(
            self.ls_active, load_by_grpId, on="group_trip_id", how="left"
        )
        return review_year_list

    def ls_active_by_stage(self, stage: str) -> pd.DataFrame:
        return self.ls_active_by_dp[
            self.ls_active_by_dp[self.review_year] == stage
        ]

    def ls_active_by_geoLoc(self, geo_loc: str) -> pd.DataFrame:
        return self.ls_active_by_dp[self.ls_active_by_dp["geo_region"] == geo_loc]

    def ls_active_by_geoLoc_stage(self, stage: str, geo_loc: str) -> pd.DataFrame:
        stage_grp = self.ls_active_by_dp[
            self.ls_active_by_dp[self.review_year] == stage
        ]
        stage_loc = stage_grp[stage_grp["geo_region"] == geo_loc]
        return stage_loc

    def ls_active_by_subs(self, subs_name: str) -> pd.DataFrame:
        return self.ls_active_by_dp[self.ls_active_by_dp["mnemonic"] == subs_name]

    def dn_list(self):
        dn_list_df = pd.merge(
            self.dn_excluded_list, self.ls_active_by_dp, on="local_trip_id", how="left"
        )[["local_trip_id", "group_trip_id", self.review_year, "mnemonic", "remark"]]

        dn_quantum = pd.merge(
            dn_list_df,
            self.ls_active_by_grpId,
            on=["group_trip_id", self.review_year],
            how="left",
        )
        # print(dn_quantum)

        df_merged = dn_quantum.groupby(
            ["group_trip_id", "mnemonic"], as_index=False
        ).agg(lambda x: ", ".join(x.astype(str).unique()))

        return df_merged

    # def quantum_stage_by_grpId(self) -> pd.DataFrame:
    #     """ Provide a list of quantum ls for each operating stage. """
    #     stage_grp = self.grpId_list.groupby([self.review_year], as_index=False)[
    #         ["Pload (MW)", "Qload (Mvar)"]
    #     ].sum()
    #     return stage_grp

    # def review_by_stage_grpId(self, stage: str) -> pd.DataFrame:
    #     stage_grp = self.grpId_list[self.grpId_list[self.review_year] == stage]
    #     return stage_grp

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
