import pandas as pd
import streamlit as st
from typing import List, Optional, Sequence, Tuple, Any

from applications.load_shedding.LoadShedding import LoadShedding
from applications.load_shedding.LoadProfile import LoadProfile
from applications.load_shedding.LoadShedding import read_ls_data, get_path
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# load_profile_2025 = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/2025_load_profile.xlsx"
# load_profile = pd.read_excel(load_profile_2025)

load_file = read_ls_data(get_path("2025_load_profile.xlsx", "data"))
loadprofile = LoadProfile(load_profile=load_file)
load_profile_df = loadprofile.df

ls_scheme = ["UFLS"]
review_year = "2025"


loadshedding = LoadShedding(load_df=load_profile_df)


assignment = loadshedding.ls_assignment_masterlist()


print(assignment)





# shedding_data = {
#     "North": 2163, 
#     "KlangValley": 3931, 
#     "South": 2660, 
#     "East": 1014
# }

# # 1. Prepare the data for plotting
# plot_data = []
# for region, shed_mw in shedding_data.items():
#     # Use the regional MD variable (you need to define or fetch these)
#     total_md = globals().get(f"{region.lower()}_mw", 0) # Placeholder to get the MD
    
#     # Calculate the remaining (unshed) load
#     remaining_load = total_md - shed_mw
    
#     # Add data points for the stacked chart
#     plot_data.append({'Region': region, 'Type': 'Load Shedding', 'MW': shed_mw})
#     plot_data.append({'Region': region, 'Type': 'Remaining Load', 'MW': remaining_load})

# df_shedding = pd.DataFrame(plot_data)
# print(df_shedding)

