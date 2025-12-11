import os
import sys
import pandas as pd
import numpy as np
from functools import reduce
from typing import Optional, Dict, List

from applications.load_shedding.helper import columns_list
from applications.load_shedding.ufls_setting import UFLS_SETTING
from applications.load_shedding.uvls_setting import UVLS_SETTING


def read_ls_data(file_path: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_excel(file_path)
        df = df.apply(
            lambda s: s.astype(str).str.strip() if s.dtype == "object" else s,
            axis=0,
        )
        return df
    except FileNotFoundError:
        log_error(f"File not found: {file_path}")
        return None
    except Exception as e:
        log_error(f"Error processing file '{file_path}': {str(e)}")
        return None


def log_error(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)


def get_path(filename: str, data_dir: str = "data") -> str:
    return os.path.join(data_dir, filename)


def loadshedding_masterlist(ls_df, scheme):
    ls_assignment = ls_df.copy() if ls_df is not None else pd.DataFrame()
    mapping_cols = {
        col: f"{scheme}_{col}"
        for col in ls_assignment.columns
        if col != "assignment_id"
    }
    ls_assignment.rename(columns=mapping_cols, inplace=True)

    return ls_assignment


def ls_active(ls_df, review_year, scheme) -> pd.DataFrame:
    ls_assignment = ls_df.copy() if ls_df is not None else pd.DataFrame()

    review_year_list = columns_list(
        ls_assignment, unwanted_el=["assignment_id"])

    latest_review = review_year

    if latest_review not in review_year_list:
        review_year_list.sort(reverse=True)
        latest_review = review_year_list[0]

    ls_assignment.rename(columns={latest_review: scheme}, inplace=True)
    ls_review = ls_assignment[["assignment_id", scheme]]

    ls_review = ~ls_review[scheme].isin(["nan", "#na"])
    ls_review_active = ls_assignment.loc[ls_review, ["assignment_id", scheme]]

    ls_review_active["sort_key"] = (
        ls_review_active[scheme].str.extract(r"stage_(\d+)").astype(int)
    )

    ls_sorted = ls_review_active.sort_values(by="sort_key", ascending=True)
    ls_sorted = ls_sorted.drop(columns=["sort_key"]).reset_index(drop=True)

    return pd.DataFrame(ls_sorted)


class LoadShedding:
    def __init__(self, load_profile: pd.DataFrame, data_dir: str = "data") -> None:
        self.load_profile = load_profile.copy()

        self.ufls_assignment = read_ls_data(
            get_path("assignment_ufls.xlsx", data_dir))
        if self.ufls_assignment is not None:
            self.ufls_assignment.columns = self.ufls_assignment.columns.astype(
                str)
        self.uvls_assignment = read_ls_data(
            get_path("assignment_uvls.xlsx", data_dir))
        if self.uvls_assignment is not None:
            self.uvls_assignment.columns = self.uvls_assignment.columns.astype(
                str)
        self.emls_assignment = read_ls_data(
            get_path("assignment_emls.xlsx", data_dir))
        if self.emls_assignment is not None:
            self.emls_assignment.columns = self.emls_assignment.columns.astype(
                str)
        self.ufls_setting = pd.DataFrame(UFLS_SETTING)
        self.uvls_setting = pd.DataFrame(UVLS_SETTING)

        # dp_incomer.xlsx = incomer (LVCB) data point to map to load profile --> interface to get MW load quantum
        self.ls_incomer = read_ls_data(get_path("dp_incomer.xlsx", data_dir))

        # dp_hvcb.xlsx = hvcb (HVCB) data point to map incomer_dp and then map to load profile --> interface to get MW load quantum
        self.ls_hvcb = read_ls_data(get_path("dp_hvcb.xlsx", data_dir))

        # rly_hvcb.xlsx = UFLS & UVLS relay bay assignment installed for LPC and pocket
        self.hvcb_rly_loc = read_ls_data(get_path("rly_hvcb.xlsx", data_dir))

        # rly_lvcb.xlsx = UFLS & UVLS relay bay assignment installed for incomer (LVCB)
        self.incomer_rly_loc = read_ls_data(
            get_path("rly_incomer.xlsx", data_dir))

        self.flaglist_gso = read_ls_data(
            get_path("flaglist_gso.xlsx", data_dir))
        self.flaglist_incomer = read_ls_data(
            get_path("flaglist_incomer.xlsx", data_dir)
        )

        self.subs_meta = read_ls_data(get_path("subs_metadata.xlsx", data_dir))
        self.zone_mapping = {
            "North-Perda": "North",
            "North-Ipoh": "North",
            "North-Kedah_Perlis": "North",
            "KL": "KlangValley",
            "Selangor": "KlangValley",
            "South-N9": "South",
            "South-Melaka": "South",
            "South-Kluang": "South",
            "South-JB": "South",
            "East-KB": "East",
            "East-Dungun": "East",
            "East-Kuantan": "East",
        }

    def subs_metadata_enrichment(self):
        if self.subs_meta is None:
            return pd.DataFrame()

        subs_meta = self.subs_meta.copy()
        subs_meta["zone"] = subs_meta["gm_subzone"].map(self.zone_mapping)

        return subs_meta

    def merged_dp(self) -> pd.DataFrame:
        """This list is a combination of incomer Delivery Point and HVCB Delivery Point (pocket assignment) and generate with a common assignment_id. This list act as an interface to 'communicate' with load profile file to identify and to get the load quantum value (asscociated assignment_id with load profile id)."""
        if self.ls_incomer is None or self.ls_hvcb is None:
            return pd.DataFrame()
        incomer_dp = self.ls_incomer.copy(deep=True)
        incomer_dp["ls_dp"] = "Incomer"

        hvcb_dp = self.ls_hvcb.copy(deep=True)
        hvcb_dp["ls_dp"] = hvcb_dp.apply(
            lambda row: (
                "LPC"
                if "132" in row["group_trip_id"] or "275" in row["group_trip_id"]
                else ("Interconnector" if "230" in row["group_trip_id"] else "Pocket")
            ),
            axis=1,
        )

        df_combined = pd.concat([incomer_dp, hvcb_dp], ignore_index=True)
        df_combined["assignment_id"] = df_combined["group_trip_id"].fillna(
            df_combined["local_trip_id"]
        )

        df_combined_meta = pd.merge(
            df_combined,
            self.subs_metadata_enrichment(),
            on="mnemonic",
            how="left",
        )

        return df_combined_meta

    def merged_dp_with_flaglist(self):
        """This list is a continuation of merged_dp along with the critical load flaglist."""
        merged_dp = self.merged_dp()
        flaglist = self.flaglist()

        if merged_dp.empty or flaglist.empty:
            return pd.DataFrame()

        df_combined = pd.merge(
            merged_dp,
            flaglist,
            left_on="local_trip_id",
            right_on="local_trip_id",  # "local_trip_id"
            how="left",
        )

        return df_combined

    def dp_grpId_loadquantum(self) -> pd.DataFrame:
        """This master list is the continuation of merged_dp_with_flaglist function list, which merges the trip point mapping with the load profile to get the actual load quantum that will be shed when a particular assignment_id is activated."""
        if self.load_profile is None:
            return pd.DataFrame()

        load_profile = self.load_profile.copy(deep=True)[
            ["Mnemonic", "Id", "Pload (MW)", "Qload (Mvar)"]
        ]

        load = pd.merge(
            self.merged_dp_with_flaglist(),
            load_profile,
            left_on=["mnemonic", "feeder_id"],
            right_on=["Mnemonic", "Id"],
            how="left",
        )

        load = load.fillna("nan")
        load = load.astype(str)
        load["Pload (MW)"] = pd.to_numeric(load["Pload (MW)"], errors="coerce").fillna(
            0
        )
        load["Qload (Mvar)"] = pd.to_numeric(
            load["Qload (Mvar)"], errors="coerce"
        ).fillna(0)

        load_cols = load.columns
        cols_to_remove = ["Mnemonic", "Id"]
        grp_cols = [col for col in load_cols if col not in cols_to_remove]

        load = load[grp_cols]

        load_grouped = load.groupby(
            [
                "mnemonic",
                "kV",
                "zone",
                "gm_subzone",
                "substation_name",
                "local_trip_id",
                "group_trip_id",
                "assignment_id",
                "ls_dp",
                "critical_list",
                "short_text",
                "long_text",
            ],
            as_index=False,
        ).agg(
            {
                "Pload (MW)": "sum",
                "Qload (Mvar)": "sum",
                "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
                "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
            }
        )

        return load_grouped

    def ls_assignment_masterlist(self):
        ufls = loadshedding_masterlist(self.ufls_assignment, "UFLS")
        uvls = loadshedding_masterlist(self.uvls_assignment, "UVLS")
        emls = loadshedding_masterlist(self.emls_assignment, "EMLS")

        if ufls.empty or uvls.empty or emls.empty:
            return pd.DataFrame()

        ls_masterlist = reduce(
            lambda left, right: pd.merge(
                left, right, on="assignment_id", how="outer"),
            [ufls, uvls, emls],
        )
        ls_masterlist = ls_masterlist.fillna("nan")
        ls_masterlist = ls_masterlist.astype(str)

        ls_master_w_load = pd.DataFrame()
        if not self.dp_grpId_loadquantum().empty:
            ls_master_w_load = pd.merge(
                ls_masterlist,
                self.dp_grpId_loadquantum(),
                left_on="assignment_id",
                right_on="assignment_id",
                how="left",
            )

        return ls_master_w_load

    def loadshedding_assignments_filter(
        self, review_year: Optional[str] = None, scheme: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """Combines UFLS, UVLS, or EMLS assignments into a single DataFrame - based on the selected schemes. It return a list of selected load shedding on a selected year of review with its associated load quantum i.e ['UFLS assignment', 'UVLS assignment', ...].

        If the review year is not found, it defaults to the latest year available in the data.
        if no scheme is selected, it defaults to all schemes.
        """
        current_datetime = pd.to_datetime("now")
        current_year = current_datetime.year

        if (
            self.ufls_assignment is None
            and self.uvls_assignment is None
            and self.emls_assignment is None
        ):
            print("Warning: No load shedding assignments found.")
            return pd.DataFrame()

        if review_year is None:
            review_year = str(current_year)

        if scheme is None or not scheme:
            scheme = ["UFLS", "UVLS", "EMLS"]

        assignments: Dict[str, pd.DataFrame] = {
            "UFLS": ls_active(
                self.ufls_assignment, review_year=review_year, scheme="UFLS"
            ),
            "UVLS": ls_active(
                self.uvls_assignment, review_year=review_year, scheme="UVLS"
            ),
            "EMLS": ls_active(
                self.emls_assignment, review_year=review_year, scheme="EMLS"
            ),
        }

        selected_scheme_dfs: List[pd.DataFrame] = [
            assignments[ls_scheme] for ls_scheme in scheme
        ]

        if not selected_scheme_dfs:
            print("Warning: No schemes selected or processed.")
            return pd.DataFrame()

        if len(selected_scheme_dfs) > 1:
            ls_merged = reduce(
                lambda left, right: pd.merge(
                    left, right, on="assignment_id", how="outer"
                ),
                selected_scheme_dfs,
            )
        else:
            ls_merged = selected_scheme_dfs[0]

        ls_w_load = pd.DataFrame()
        if not self.dp_grpId_loadquantum().empty:
            ls_w_load = pd.merge(
                ls_merged,
                self.dp_grpId_loadquantum(),
                left_on="assignment_id",
                right_on="assignment_id",
                how="left",
            )

        return ls_w_load

    def flaglist(self):
        """Combination of all substation that has been identified as critical list from DSO list & GSO critical list. The list refer to group_trip_id."""
        if self.flaglist_incomer is None or self.flaglist_gso is None:
            return pd.DataFrame()

        defeated_list = self.flaglist_gso.copy(deep=True)
        incomer_critical_list = self.flaglist_incomer.copy(deep=True)

        combined_flaglist = pd.concat(
            [defeated_list, incomer_critical_list], ignore_index=True
        )
        combined_flaglist = combined_flaglist.fillna("nan")
        combined_flaglist = combined_flaglist.astype(str)

        return combined_flaglist

    def automatic_loadshedding_rly(self):
        """This list a combination of bay assignment (incomer and HVCB) that have been installed with load shedding relay. This list indicates how much the load quantum potentially can be assigned to be shed when the relay is activated."""
        if (
            self.ls_hvcb is None
            or self.incomer_rly_loc is None
            or self.ls_incomer is None
        ):
            return pd.DataFrame()

        required_columns = [
            "local_trip_id",
            "mnemonic",
            "assignment_id",
            "feeder_id",
            "breaker_id",
        ]
        hvcb_dp = self.ls_hvcb.copy(deep=True)
        hvcb_dp["assignment_id"] = hvcb_dp["group_trip_id"]
        hvcb_rly = hvcb_dp.groupby(
            ["group_trip_id", "mnemonic", "local_trip_id", "assignment_id"],
            as_index=False,
        ).agg(
            {
                "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
                "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
            }
        )[
            required_columns
        ]

        incomer_relay = self.incomer_rly_loc.copy(deep=True)
        incomer_relay["assignment_id"] = incomer_relay["local_trip_id"]
        incomer_richment = pd.merge(
            incomer_relay, self.ls_incomer, on="local_trip_id", how="left"
        )
        incomer_rly = incomer_richment.groupby(
            ["local_trip_id", "assignment_id", "mnemonic", "kV"], as_index=False
        ).agg(
            {
                "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
                "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
            }
        )[
            required_columns
        ]

        available_rly = pd.concat([hvcb_rly, incomer_rly], ignore_index=True)

        available_rly_with_load = pd.merge(
            available_rly,
            self.dp_grpId_loadquantum(),
            on=[
                "mnemonic",
                "local_trip_id",
                "assignment_id",
                "feeder_id",
                "breaker_id",
            ],
            how="left",
        )

        return available_rly_with_load

    def available_potential_quantum(self) -> float:
        """Calculates the total available potential load quantum (in MW) that can be shed based on the automatic load shedding relay assignments."""
        available_assignment = self.automatic_loadshedding_rly()

        if available_assignment.empty:
            return 0.0

        remove_duplicate = available_assignment.drop_duplicates(
            subset=["local_trip_id", "mnemonic"], keep="first"
        )

        total_potential_mw = remove_duplicate["Pload (MW)"].sum()

        return total_potential_mw

    def filtered_data(self, filters: Dict, df: pd.DataFrame) -> pd.DataFrame:
        """Applies filtering on the loadshedding assignments based on the provided filter criteria in the 'filters' dictionary. It merges the load shedding assignments with the substation metadata for enriched filtering."""

        LOADSHED_SCHEME = ["UFLS", "UVLS", "EMLS"]
        review_year = filters.get("review_year", None)
        scheme = filters.get("scheme", [])
        op_stage = filters.get("op_stage", [])

        if df is None or df.empty:
            return pd.DataFrame()

        filtered_df = df.copy()
        all_df_columns = df.columns
        selected_ls_review = []
        selected_ls_cols_dict = {}

        if review_year is not None and scheme:
            selected_ls_review = [
                f"{ls_scheme}_{review_year}" for ls_scheme in scheme]
            
            df_ls_cols = [
                col
                for col in all_df_columns
                if any(keyword in col for keyword in LOADSHED_SCHEME)
            ]
     
            drop_ls_cols = [
                col for col in df_ls_cols if col not in selected_ls_review
            ]
  
            filtered_df = filtered_df.drop(columns=drop_ls_cols, axis=1, errors='ignore')

        valid_ls_review = [ls_review for ls_review in selected_ls_review if ls_review in all_df_columns]

        for ls_review in valid_ls_review:
            selected_ls_cols_dict[ls_review] = op_stage

        filters.update(selected_ls_cols_dict)

        ## Data Filteration #######
        for col, selected in filters.items():
            if selected is None or selected == [] or col not in filtered_df.columns:
                continue
            if isinstance(selected, (list, tuple, set)):
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
            else:
                filtered_df = filtered_df[filtered_df[col] == selected]

        if filtered_df.empty:
            return pd.DataFrame()

        if valid_ls_review:
            filtered_df[valid_ls_review] = filtered_df[valid_ls_review].replace([
                'nan', '#na'], np.nan)
            filtered_df = filtered_df.dropna(
                subset=valid_ls_review, how='all')

        return filtered_df
