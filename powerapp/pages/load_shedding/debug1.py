import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any

from applications.load_shedding.data_processing.LoadShedding import (
    LoadShedding,
    LS_Data,
)

load_profile_2025 = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/2025_load_profile.xlsx"
load_profile = pd.read_excel(load_profile_2025)
ls_scheme = "UFLS"
review_year = "2025"


load_shed = LoadShedding(
    review_year=review_year,
    load_profile=load_profile,
    scheme=ls_scheme,
)
ls = load_shed.ls_active()
print(ls)
