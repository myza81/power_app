import os
import sys
import pandas as pd
import numpy as np
from functools import reduce
from typing import Optional, Dict, List
from .SchemeReview import SchemeReview
from applications.load_shedding.data_processing.helper import columns_list


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


def ls_active(ls_df, review_year, scheme) -> pd.DataFrame:

    ls_assignment = ls_df.copy() if ls_df is not None else pd.DataFrame()

    review_year_list = columns_list(
        ls_assignment, unwanted_el=["group_trip_id"])

    latest_review = review_year

    if latest_review not in review_year_list:
        review_year_list.sort(reverse=True)
        latest_review = review_year_list[0]

    ls_assignment.rename(columns={latest_review: scheme}, inplace=True)
    # print(ls_assignment)

    ls_review = ls_assignment[["group_trip_id", scheme]]

    ls_review = ~ls_review[scheme].isin(["nan", "#na"])
    ls_review_active = ls_assignment.loc[ls_review, ["group_trip_id", scheme]]

    ls_review_active["sort_key"] = (
        ls_review_active[scheme].str.extract(r"stage_(\d+)").astype(int)
    )

    ls_sorted = ls_review_active.sort_values(by="sort_key", ascending=True)
    ls_sorted = ls_sorted.drop(columns=["sort_key"]).reset_index(drop=True)

    return pd.DataFrame(ls_sorted)


class LS_Data:
    def __init__(self, load_profile: pd.DataFrame, data_dir: str = "data") -> None:
        self.load_profile = load_profile.copy()
        self.dn_excluded_list = read_ls_data(
            get_path("dn_exluded_list.xlsx", data_dir))
        self.ufls_assignment = read_ls_data(
            get_path("ufls_assignment.xlsx", data_dir))
        if self.ufls_assignment is not None:
            self.ufls_assignment.columns = self.ufls_assignment.columns.astype(
                str)
        self.uvls_assignment = read_ls_data(
            get_path("uvls_assignment.xlsx", data_dir))
        if self.uvls_assignment is not None:
            self.uvls_assignment.columns = self.uvls_assignment.columns.astype(
                str)
        self.ls_incomer = read_ls_data(get_path("incomer_dp.xlsx", data_dir))
        self.ls_hvcb = read_ls_data(get_path("hvcb_dp.xlsx", data_dir))
        self.pocket_rly_loc = read_ls_data(get_path("hvcb_rly.xlsx", data_dir))
        self.subs_meta = read_ls_data(get_path("subs_metadata.xlsx", data_dir))
        self.ufls_setting = read_ls_data(
            get_path("ufls_setting.xlsx", data_dir))
        self.uvls_setting = read_ls_data(
            get_path("uvls_setting.xlsx", data_dir))
        self.log_defeat = read_ls_data(get_path("log_defeated.xlsx", data_dir))
        self.emls_assignment = read_ls_data(
            get_path("emls_assignment.xlsx", data_dir))
        self.available_ls = read_ls_data(
            get_path("available_ls.xlsx", data_dir))


class LoadShedding(LS_Data):

    def __init__(
        self, review_year: str, scheme: list[str], load_profile: pd.DataFrame
    ) -> None:

        super().__init__(load_profile)
        self.review_year = review_year
        self.scheme = scheme

    def subs_metadata_enrichment(self):
        ZONE_MAPPING = {
            'North-Perda': 'North',
            'North-Ipoh': 'North',
            'North-Kedah_Perlis': 'North',
            'KL': 'KlangValley',
            'Selangor': 'KlangValley',
            'South-N9': 'South',
            'South-Melaka': 'South',
            'South-Kluang': 'South',
            'South-JB': 'South',
            'East-KB': 'East',
            'East-Dungun': 'East',
            'East-Kuantan': 'East',
        }

        if self.subs_meta is None:
            return pd.DataFrame()

        subs_meta = self.subs_meta.copy()
        subs_meta['zone'] = subs_meta['gm_subzone'].map(ZONE_MAPPING)

        return subs_meta

    def ls_combined(self) -> pd.DataFrame:
        incomer_dp = self.ls_incomer if self.ls_incomer is not None else pd.DataFrame()
        incomer_dp["ls_dp"] = "incomer"
        hvcb_dp = self.ls_hvcb if self.ls_hvcb is not None else pd.DataFrame()
        hvcb_dp["ls_dp"] = "pocket"
        return pd.concat([incomer_dp, hvcb_dp], ignore_index=True)

    def mlist_load(self) -> pd.DataFrame:
        load = pd.merge(
            self.ls_combined(),
            self.load_profile,
            left_on=["mnemonic", "feeder_id"],
            right_on=["Mnemonic", "Id"],
            how="inner",
        )[
            [
                "mnemonic",
                "kV",
                "local_trip_id",
                "feeder_id",
                "breaker_id",
                "group_trip_id",
                "Pload (MW)",
                "Qload (Mvar)",
                "ls_dp",
            ]
        ]
        load["local_trip_id"] = load["local_trip_id"].fillna(
            load["group_trip_id"])
        return load

    def mlist_load_grpby_tripId(self):
        return (
            self.mlist_load()
            .groupby(
                ["mnemonic", "kV", "local_trip_id", "group_trip_id", "ls_dp"],
                as_index=False,
            )
            .agg(
                {
                    "Pload (MW)": "sum",
                    "Qload (Mvar)": "sum",
                    "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
                }
            )
        )

    def ls_list(self) -> pd.DataFrame:
        assignments: Dict[str, pd.DataFrame] = {
            "UFLS": pd.DataFrame(self.ufls_assignment),
            "UVLS": pd.DataFrame(self.uvls_assignment),
            "EMLS": pd.DataFrame(self.emls_assignment),
        }

        processed_schemes: Dict[str, pd.DataFrame] = {
            scheme_name: ls_active(
                df, review_year=self.review_year, scheme=scheme_name)
            for scheme_name, df in assignments.items()
        }

        selected_scheme_dfs: List[pd.DataFrame] = [
            processed_schemes[ls_scheme] for ls_scheme in self.scheme
        ]

        if not selected_scheme_dfs:
            print("Warning: No schemes selected or processed.")
            return pd.DataFrame()

        if len(selected_scheme_dfs) > 1:
            ls_merged = reduce(
                lambda left, right: pd.merge(
                    left, right, on="group_trip_id", how="outer"
                ),
                selected_scheme_dfs,
            )
        else:
            ls_merged = selected_scheme_dfs[0]

        master_load = self.mlist_load_grpby_tripId()
        ls_w_load = pd.merge(ls_merged, master_load,
                             on="group_trip_id", how="left")

        return ls_w_load

    def filtered_data(self, filters):
        ls_w_load = self.ls_list().copy()
        subs_meta = self.subs_metadata_enrichment()

        if ls_w_load.empty:
            return "Warning: No schemes selected."

        if subs_meta is not None:
            ls_w_load = pd.merge(ls_w_load, subs_meta,
                                 on="mnemonic", how="left")

        for col, selected in filters.items():
            if selected is None or selected == []:
                continue
            if col not in ls_w_load.columns:
                continue
            if isinstance(selected, (list, tuple, set)):
                ls_w_load = ls_w_load[ls_w_load[col].isin(selected)]
            else:
                ls_w_load = ls_w_load[ls_w_load[col] == selected]

        if ls_w_load.empty:
            return "Filtering resulted in an empty DataFrame."

        return ls_w_load
