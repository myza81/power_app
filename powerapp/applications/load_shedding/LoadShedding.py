import os
import sys
from warnings import filters
import pandas as pd
import numpy as np
import streamlit as st
from functools import reduce
from typing import Optional, Dict, List

from applications.load_shedding.helper import columns_list
from pages.load_shedding.helper import join_unique_non_empty
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


class LoadShedding:
    def __init__(self, load_df: pd.DataFrame, filedir: str = "data") -> None:
        self.load_profile = load_df

        self.ufls_filepath = get_path("assignment_ufls.xlsx", filedir)
        self.uvls_filepath = get_path("assignment_uvls.xlsx", filedir)
        self.emls_filepath = get_path("assignment_emls.xlsx", filedir)

        self.ufls_assignment = read_ls_data(self.ufls_filepath)
        self.uvls_assignment = read_ls_data(self.uvls_filepath)
        self.emls_assignment = read_ls_data(self.emls_filepath)
        self.ufls_setting = pd.DataFrame(UFLS_SETTING)
        self.uvls_setting = pd.DataFrame(UVLS_SETTING)

        # delivery_point.xlsx = one-to-one mirror to load profile file to match load with assignment. to update reqularly as system updated
        self.delivery_point = read_ls_data(
            get_path("delivery_point.xlsx", filedir))

        self.pocket_assign = read_ls_data(
            get_path("pocket_assign.xlsx", filedir))

        # rly_pocket.xlsx = associted breakers where the pocket loads are disconnected
        self.rly_pocket = read_ls_data(get_path("rly_pocket.xlsx", filedir))

        # rly_lvcb.xlsx = UFLS & UVLS relay bay assignment installed for incomer (LVCB)
        self.rly_incomer = read_ls_data(get_path("rly_incomer.xlsx", filedir))

        self.flaglist = read_ls_data(get_path("flaglist.xlsx", filedir))

        self.substations = read_ls_data(get_path("substations.xlsx", filedir))

        self.LOADSHED_SCHEME = ["UFLS", "UVLS", "EMLS"]

    def subs_meta(self):
        if self.substations is None:
            return pd.DataFrame()

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
        df = self.substations.copy()
        df["zone"] = df["gm_subzone"].map(self.zone_mapping)

        return df

    def loadprofile_df(self):
        if self.load_profile is None or self.subs_meta().empty:
            return pd.DataFrame()

        subs_meta_df = self.subs_meta()
        load_profile = self.load_profile[[
            "mnemonic", "feeder_id", "Load (MW)", "state", "zone"]].copy()
        load_profile["state"] = load_profile["state"].str.title()

        df = pd.merge(
            subs_meta_df,
            load_profile,
            on=["mnemonic"],
            how="outer",
            suffixes=("_meta", "_profile"),
        )

        df["state_meta"] = df["state_meta"].replace('nan', np.nan)
        df["state"] = df["state_meta"].combine_first(df["state_profile"])
        df["zone"] = df["zone_profile"].combine_first(df["zone_meta"])
        df = df.drop(
            columns=["state_meta", "state_profile", "zone_meta", "zone_profile"])

        mask = df["substation_name"].notna()
        df["subs_fullname"] = df["mnemonic"].where(
            ~mask,
            df["mnemonic"] + " (" + df["substation_name"].fillna("") + ")"
        )

        return df

    def profile_metadata(self):
        df_raw = self.loadprofile_df()

        if df_raw.empty:
            return pd.DataFrame()

        required_cols = ["state", "zone", "gm_subzone", "substation_name",
                         "mnemonic", "subs_fullname", "coordinate"]

        df = df_raw[required_cols].copy()
        df_unique = df.drop_duplicates(
            subset=required_cols,
            keep='first'
        ).reset_index(drop=True)

        return df_unique

    def zone_load_profile(self, zone):
        loadprofile_df = self.loadprofile_df()
        zone_df = loadprofile_df.loc[loadprofile_df["zone"] == zone]
        zone_mw = zone_df["Load (MW)"].sum()

        return zone_mw

    def load_dp(self) -> pd.DataFrame:
        if (
            self.delivery_point is None
            or self.load_profile is None
            or self.flaglist is None
            or self.profile_metadata().empty
        ):
            return pd.DataFrame()

        delivery_point = self.delivery_point.drop_duplicates()
        profile_metadata = self.profile_metadata().copy()

        df = pd.merge(
            delivery_point,
            self.load_profile[["mnemonic", "feeder_id", "Load (MW)"]],
            on=["mnemonic", "feeder_id"],
            how="left",
        )

        df_meta = pd.merge(
            df,
            profile_metadata,
            on="mnemonic",
            how="left",
        )

        df_flaglist = pd.merge(
            df_meta,
            self.flaglist,
            left_on="local_trip_id",
            right_on="local_trip_id",
            how="left",
        )

        df_flaglist = df_flaglist.replace(["nan"], np.nan)

        return df_flaglist

    def flaglist_subs(self):
        if self.load_dp().empty:
            return pd.DataFrame()

        flaglist = self.load_dp().loc[self.load_dp()[
            "critical_list"].notna()].copy()

        flaglist_grp = flaglist.groupby(
            ["local_trip_id", "mnemonic", "substation_name", "kV", "coordinate",
                "gm_subzone", "zone", "state", "critical_list", "short_text", "long_text"],
            as_index=False,
            dropna=False
        ).agg({
            "Load (MW)": "sum",
            "feeder_id": lambda x: ", ".join(x.astype(str).unique()),
            "breaker_id": lambda x: ", ".join(x.astype(str).unique()),
        })
        flaglist_grp["critical_list"] = flaglist_grp["critical_list"].str.upper()

        return flaglist_grp

    def load_pocket(self) -> pd.DataFrame:
        load_dp = self.load_dp()

        if self.pocket_assign is None or load_dp.empty:
            return pd.DataFrame()

        df = pd.merge(self.pocket_assign, load_dp, on=["mnemonic"], how="left")

        return df

    def assignment_loadquantum(self) -> pd.DataFrame:
        load_dp = self.load_dp()
        load_pocket = self.load_pocket()

        if load_dp.empty and load_pocket.empty:
            return pd.DataFrame()

        df = pd.concat([load_dp, load_pocket], ignore_index=True, axis=0)
        df["assignment_id"] = df["group_trip_id"].fillna(df["local_trip_id"])

        id_col = df["assignment_id"].fillna("na").astype(str)
        conditions = [
            id_col.str.contains("132|275"),
            id_col.str.contains("230"),
            id_col.str.contains("11|22|33"),
            id_col.str.contains("na"),
        ]
        choices = ["LPC", "Interconnector", "Local_Load", ""]

        df["dp_type"] = np.select(conditions, choices, default="Pocket")

        return df

    def pocket_relay(self):
        if self.rly_pocket is None or self.profile_metadata().empty:
            return pd.DataFrame()

        profile_metadata = self.profile_metadata().copy()

        df = pd.merge(
            self.rly_pocket.astype(str),
            profile_metadata,
            left_on="Mnemonic",
            right_on="mnemonic",
            how="left",
        ).drop(columns=["mnemonic"])

        df = df.rename(
            columns={
                "zone": "Zone",
                "state": "State",
                "gm_subzone": "Subzone",
                "substation_name": "Substation",
                "coordinate": "Coordinate"
            }
        )

        return df

    def incomer_relay(self):
        if self.rly_incomer is None or self.load_dp().empty:
            return pd.DataFrame()

        df = pd.merge(
            self.rly_incomer,
            self.load_dp(),
            on="local_trip_id",
            how="left"
        )
        df["assignment_id"] = df["local_trip_id"]

        return df

    def ls_assignment_masterlist(self):
        ufls = loadshedding_masterlist(self.ufls_assignment, "UFLS")
        uvls = loadshedding_masterlist(self.uvls_assignment, "UVLS")
        emls = loadshedding_masterlist(self.emls_assignment, "EMLS")

        if (
            ufls.empty
            or uvls.empty
            or emls.empty
            or self.assignment_loadquantum().empty
        ):
            return pd.DataFrame()

        ls_masterlist = reduce(
            lambda left, right: pd.merge(
                left, right, on="assignment_id", how="outer"),
            [ufls, uvls, emls],
        )

        ls_masterlist = ls_masterlist.replace(["nan", "#na"], np.nan)

        df = pd.merge(
            ls_masterlist,
            self.assignment_loadquantum(),
            on="assignment_id",
            how="left",
        )

        return df

    def filtered_data(self, filters: Dict, df: pd.DataFrame) -> pd.DataFrame:
        """Applies filtering on the loadshedding assignments based on the provided filter criteria in the 'filters' dictionary. It merges the load shedding assignments with the substation metadata for enriched filtering."""

        scheme = filters.get("scheme", None)
        op_stage = filters.get("op_stage", [])

        if df is None or df.empty or scheme is None:
            return pd.DataFrame()

        filtered_df = df.copy()
        selected_inp_scheme = filters.get("scheme", [])
        selected_ls_cols_dict = {}

        available_scheme = set(selected_inp_scheme).intersection(
            set(filtered_df.columns)
        )

        if len(available_scheme) == 0:
            return pd.DataFrame()

        drop_cols = [
            col
            for col in filtered_df.columns
            if any(keyword in col for keyword in self.LOADSHED_SCHEME)
            and col not in available_scheme
        ]

        filtered_df = filtered_df.drop(
            columns=drop_cols, axis=1, errors="ignore")

        for ls_review in available_scheme:
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

        available_scheme_list = list(available_scheme)
        filtered_df[available_scheme_list] = (
            filtered_df[available_scheme_list]
            .mask(lambda df: df.isin(["nan", "#na"]))
        )
        filtered_df = filtered_df.dropna(
            subset=available_scheme_list, how="all")

        return filtered_df

    def simple_filtered(self, filters: Dict, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        data = df.copy()

        for col, selected in filters.items():
            if selected is None or selected == [] or col not in data.columns:
                continue
            if isinstance(selected, (list, tuple, set)):
                data = data[data[col].isin(selected)]
            else:
                data = data[data[col] == selected]

        if data.empty:
            return pd.DataFrame()

        return data
