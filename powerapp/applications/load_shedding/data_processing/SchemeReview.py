import pandas as pd
from typing import Optional


class SchemeReview:
    """
    Encapsulates review logic for LS schemes (UFLS/UVLS/EMLS).
    All internal DataFrames are normalised to non-None (empty DataFrames if missing)
    so that public methods always return pd.DataFrame.
    """

    def __init__(
        self,
        review_year: str,
        local_load: Optional[pd.DataFrame],
        ls_load_pocket: Optional[pd.DataFrame],
        load_by_subs: pd.DataFrame,
        dn_excluded_list: Optional[pd.DataFrame],
        ls_assignment: Optional[pd.DataFrame],
        log_defeated: Optional[pd.DataFrame],
        relay_location: Optional[pd.DataFrame],
        substation_masterlist: Optional[pd.DataFrame],
        ls_setting: Optional[pd.DataFrame] = None,
    ) -> None:

        self.review_year = review_year

        # Normalise inputs: always store DataFrames (empty if None)
        self.local_load = (
            local_load.copy() if local_load is not None else pd.DataFrame()
        )
        self.ls_load_pocket = (
            ls_load_pocket.copy() if ls_load_pocket is not None else pd.DataFrame()
        )
        self.load_by_subs = load_by_subs.copy()

        self.ls_assignment = (
            ls_assignment.copy() if ls_assignment is not None else pd.DataFrame()
        )
        self.dn_excluded_list = (
            dn_excluded_list.copy() if dn_excluded_list is not None else pd.DataFrame()
        )
        self.log_defeated = (
            log_defeated.copy() if log_defeated is not None else pd.DataFrame()
        )
        self.relay_location = (
            relay_location.copy() if relay_location is not None else pd.DataFrame()
        )
        self.substation_masterlist = (
            substation_masterlist.copy()
            if substation_masterlist is not None
            else pd.DataFrame()
        )
        self.ls_setting = ls_setting.copy() if ls_setting is not None else None

        # Ensure the review_year column exists in ls_assignment to avoid KeyError
        if (
            not self.ls_assignment.empty
            and self.review_year not in self.ls_assignment.columns
        ):
            # create the column filled with NA if missing
            self.ls_assignment[self.review_year] = pd.NA

        # Pre-compute key views (they will be empty if inputs are insufficient)
        self.ls_active = self.ls_active_list()
        self.ls_active_by_dp = self.ls_active_by_dp_list()
        self.ls_active_by_grpId = self.ls_active_by_grpId_list()
        self.dn_summary = self.dn_list()

    # --------------------------
    # Core list builders
    # --------------------------

    def ls_active_list(self) -> pd.DataFrame:
        """
        Active LS groups for the review year: [group_trip_id, review_year].
        Returns empty DataFrame if ls_assignment is empty.
        """
        if self.ls_assignment.empty:
            return pd.DataFrame(columns=["group_trip_id", self.review_year])

        mask = self.ls_assignment[self.review_year].notna()
        active = self.ls_assignment.loc[
            mask, ["group_trip_id", self.review_year]
        ].copy()
        return active

    def ls_active_by_dp_list(self) -> pd.DataFrame:
        """
        Active LS by demand point (substation/feeder level) with metadata.
        Merge: ls_active + load_by_subs + substation_masterlist.
        """
        if (
            self.ls_active.empty
            or self.load_by_subs.empty
            or self.substation_masterlist.empty
        ):
            return pd.DataFrame()

        review_year_list = pd.merge(
            self.ls_active,
            self.load_by_subs,
            on="group_trip_id",
            how="left",
        )

        with_metadata = pd.merge(
            review_year_list,
            self.substation_masterlist,
            on="mnemonic",
            how="left",
        )

        return with_metadata

    def ls_active_by_grpId_list(self) -> pd.DataFrame:
        """
        Active LS aggregated by group_trip_id (sum of P and Q).
        """
        if self.load_by_subs.empty or self.ls_active.empty:
            return pd.DataFrame()

        load_by_grpId = self.load_by_subs.groupby(["group_trip_id"], as_index=False)[
            ["Pload (MW)", "Qload (Mvar)"]
        ].sum()

        review_year_list = pd.merge(
            self.ls_active, load_by_grpId, on="group_trip_id", how="left"
        )

        return review_year_list

    # --------------------------
    # Query helpers
    # --------------------------

    def ls_active_by_stage(self, stage: str) -> pd.DataFrame:
        """
        Filter active LS by operating stage (e.g. 'stage_1', 'stage_2').
        """
        if self.ls_active_by_dp.empty:
            return pd.DataFrame()

        return self.ls_active_by_dp[
            self.ls_active_by_dp[self.review_year] == stage
        ].copy()

    def ls_active_by_geoLoc(self, geo_loc: str) -> pd.DataFrame:
        """
        Filter active LS by geo_region.
        """
        if (
            self.ls_active_by_dp.empty
            or "geo_region" not in self.ls_active_by_dp.columns
        ):
            return pd.DataFrame()

        return self.ls_active_by_dp[
            self.ls_active_by_dp["geo_region"] == geo_loc
        ].copy()

    def ls_active_by_geoLoc_stage(self, stage: str, geo_loc: str) -> pd.DataFrame:
        """
        Filter active LS by both stage and geo_region.
        """
        if (
            self.ls_active_by_dp.empty
            or "geo_region" not in self.ls_active_by_dp.columns
        ):
            return pd.DataFrame()

        stage_grp = self.ls_active_by_dp[
            self.ls_active_by_dp[self.review_year] == stage
        ]
        stage_loc = stage_grp[stage_grp["geo_region"] == geo_loc]

        return stage_loc.copy()

    def ls_active_by_subs(self, subs_name: str) -> pd.DataFrame:
        """
        Filter active LS by substation mnemonic.
        """
        if self.ls_active_by_dp.empty or "mnemonic" not in self.ls_active_by_dp.columns:
            return pd.DataFrame()

        return self.ls_active_by_dp[
            self.ls_active_by_dp["mnemonic"] == subs_name
        ].copy()

    # --------------------------
    # DN list processing
    # --------------------------

    def dn_list(self) -> pd.DataFrame:
        """
        Build DN summary list by merging dn_excluded_list with active LS by DP
        and active LS by group, then grouping.
        Returns empty DataFrame if required inputs are missing/empty.
        """
        required_cols_dn = {"local_trip_id"}
        required_cols_active_dp = {"local_trip_id", "group_trip_id", "mnemonic"}
        required_cols_active_grp = {"group_trip_id", self.review_year}

        if (
            self.dn_excluded_list.empty
            or self.ls_active_by_dp.empty
            or self.ls_active_by_grpId.empty
            or not required_cols_dn.issubset(self.dn_excluded_list.columns)
            or not required_cols_active_dp.issubset(self.ls_active_by_dp.columns)
            or not required_cols_active_grp.issubset(self.ls_active_by_grpId.columns)
        ):
            return pd.DataFrame()

        # 1) Attach active LS info (stage, mnemonic, etc.) to DN list
        dn_list_df = pd.merge(
            self.dn_excluded_list,
            self.ls_active_by_dp,
            on="local_trip_id",
            how="left",
        )[
            ["local_trip_id", "group_trip_id", self.review_year, "mnemonic", "remark"]
        ].copy()

        # 2) Attach group quantum (P/Q) to DN list
        dn_quantum = pd.merge(
            dn_list_df,
            self.ls_active_by_grpId,
            on=["group_trip_id", self.review_year],
            how="left",
        )

        # 3) Group & aggregate:
        #    - for IDs/remarks: join unique values
        #    - for P/Q: keep the numeric aggregation logic flexible (you can change to sum if needed)
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
