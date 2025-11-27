import pandas as pd

from pages.underfrequency.LoadShedding_df import LoadShedding
from pages.underfrequency.LoadSheddingData import LoadSheddingData

data = LoadSheddingData()
ufls_assignment = data.ufls_assignment

# ls = LoadShedding(
#     review_year=review_year,
#     load_profile=load_profile,
#     ufls_assignment=ufls_assignment,
#     uvls_assignment=uvls_assignment,
#     ls_load_local=ls_load_local,
#     ls_load_pocket=ls_load_pocket,
#     dn_excluded_list=dn_excluded_list,
#     log_defeated=log_defeated,
#     relay_location=relay_location,
#     substation_masterlist=substation_masterlist,
#     ufls_setting=ufls_setting,
#     uvls_setting=uvls_setting,
# )
