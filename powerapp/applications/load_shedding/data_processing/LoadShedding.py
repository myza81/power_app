import os
import sys
import pandas as pd

from typing import Optional
from .SchemeReview import SchemeReview


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


class LS_Data:
    def __init__(self, load_profile: pd.DataFrame, data_dir: str = "data") -> None:
        self.load_profile = load_profile.copy()
        self.dn_excluded_list = read_ls_data(get_path("dn_exluded_list.xlsx", data_dir))
        self.ufls_assignment = read_ls_data(get_path("ufls_assignment.xlsx", data_dir))
        if self.ufls_assignment is not None:
            self.ufls_assignment.columns = self.ufls_assignment.columns.astype(str)

        self.uvls_assignment = read_ls_data(get_path("uvls_assignment.xlsx", data_dir))
        if self.uvls_assignment is not None:
            self.uvls_assignment.columns = self.uvls_assignment.columns.astype(str)
        self.ls_load_local = read_ls_data(get_path("ls_load_local.xlsx", data_dir))
        self.ls_load_pocket = read_ls_data(get_path("ls_load_pocket.xlsx", data_dir))
        self.relay_location = read_ls_data(get_path("relay_location.xlsx", data_dir))
        self.substation_masterlist = read_ls_data(
            get_path("substation_masterlist.xlsx", data_dir)
        )
        self.ufls_setting = read_ls_data(get_path("ufls_setting.xlsx", data_dir))
        self.uvls_setting = read_ls_data(get_path("uvls_setting.xlsx", data_dir))
        self.log_defeat = read_ls_data(get_path("log_defeated_relay.xlsx", data_dir))
        self.emls_assignment = read_ls_data(get_path("emls_assignment.xlsx", data_dir))


class LoadShedding(LS_Data):

    def __init__(
        self, review_year: str, scheme: str, load_profile: pd.DataFrame
    ) -> None:

        super().__init__(load_profile)
        self.review_year = review_year
        self.scheme = scheme

    def combined_all_load(self) -> pd.DataFrame:
        frames = [
            df for df in (self.ls_load_local, self.ls_load_pocket) if df is not None
        ]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def mlist_load(self) -> pd.DataFrame:
        load = pd.merge(
            self.combined_all_load(),
            self.load_profile,
            left_on=["mnemonic", "feeder_id"],
            right_on=["Mnemonic", "Id"],
            how="inner",
        )[
            [
                "mnemonic",
                "local_trip_id",
                "feeder_id",
                "group_trip_id",
                "Pload (MW)",
                "Qload (Mvar)",
            ]
        ]
        load["local_trip_id"] = load["local_trip_id"].fillna(load["group_trip_id"])
        return load

    def mlist_load_grpby_tripId(self):
        return self.mlist_load().groupby(
            ["mnemonic", "local_trip_id", "group_trip_id"], as_index=False
        )[["Pload (MW)", "Qload (Mvar)"]].sum()

    def find_subs_load(self, mnemonic: str) -> pd.DataFrame:
        substation_load = self.mlist_load_grpby_tripId()
        return substation_load[substation_load["mnemonic"] == mnemonic]

    def ls_active(self) -> pd.DataFrame:
        ls_assignment = self.ufls_assignment
        if self.scheme == "UVLS":
            ls_assignment = self.uvls_assignment

        if ls_assignment is not None:
            mask = ~ls_assignment[self.review_year].isin(["nan", "#na"])
            active = ls_assignment.loc[
                mask, ["group_trip_id", self.review_year]
            ]
            active["sort_key"] = (
                active[self.review_year].str.extract(r"stage_(\d+)").astype(int)
            )
            ls_sorted = active.sort_values(by="sort_key", ascending=True)
            ls_sorted = ls_sorted.drop(columns=["sort_key"]).reset_index(drop=True)

            master_load = self.mlist_load_grpby_tripId()
            ls_w_load = pd.merge(ls_sorted, master_load, on="group_trip_id", how="left")

            return ls_w_load

        return pd.DataFrame()

    def ls_active_with_metadata(self):
        if self.substation_masterlist is not None:
            ls_active = self.ls_active()
            ls_meta = pd.merge(ls_active, self.substation_masterlist, on="mnemonic", how="left")
            return ls_meta
        return pd.DataFrame()
