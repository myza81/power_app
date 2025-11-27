import pandas as pd
import numpy as np

from .SchemeReview import SchemeReview

class LoadShedding:

    def __init__(
        self,
        review_year: str,
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
        self.review_year = review_year
        self.load_profile = load_profile.copy()

        self.local_load = ls_load_local.apply(
            lambda x: (
                x.str.strip().where(~x.str.strip().isna(), x)
                if x.dtype == "object"
                else x
            )
        )

        self.pocket_load = ls_load_pocket.apply(
            lambda x: (
                x.str.strip().where(~x.str.strip().isna(), x)
                if x.dtype == "object"
                else x
            )
        )

        self.combined_all_load = pd.concat(
            [self.local_load, self.pocket_load], ignore_index=True
        )
        # print(self.combined_all_load)

        self.masterlist_load = pd.merge(
            self.combined_all_load,
            self.load_profile,
            left_on=["mnemonic", "feeder_id"],
            right_on=["Mnemonic", "Id"],
            how="inner",
        ) [
            [
                "mnemonic",
                "local_trip_id",
                "feeder_id",
                "group_trip_id",
                "Pload (MW)",
                "Qload (Mvar)",
            ]
        ]
        self.masterlist_load["local_trip_id"] = self.masterlist_load[
            "local_trip_id"
        ].fillna(self.masterlist_load["group_trip_id"])

        self.load_by_subs = self.masterlist_load.groupby(
            ["mnemonic", "local_trip_id", "group_trip_id"], as_index=False
        )[["Pload (MW)", "Qload (Mvar)"]].sum()

        # self.load_by_subsB = self.masterlist_load.groupby(
        #     ["mnemonic", "group_trip_id"], as_index=False
        # )[["Pload (MW)", "Qload (Mvar)"]].sum()

        self.dn_excluded_list = dn_excluded_list.copy()

        self.ufls_assignment = ufls_assignment.copy()
        self.ufls_assignment.columns = self.ufls_assignment.columns.astype(str)
        self.uvls_assignment = uvls_assignment.copy()
        self.uvls_assignment.columns = self.uvls_assignment.columns.astype(str)

        self.ufls = SchemeReview(
            review_year=self.review_year,
            local_load=self.local_load,
            ls_load_pocket=self.pocket_load,
            load_by_subs=self.load_by_subs,
            dn_excluded_list=self.dn_excluded_list,
            ls_assignment=self.ufls_assignment,
            log_defeated=log_defeated.copy(),
            relay_location=relay_location.copy(),
            substation_masterlist=substation_masterlist.copy(),
            ls_setting=ufls_setting.copy(),
        )

    def find_subs_load(self, mnemonic):
        return self.load_by_subs[self.load_by_subs["mnemonic"] == mnemonic]
