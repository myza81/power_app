import pandas as pd

from pages.underfrequency.LoadShedding_df import LoadShedding


load_profile_2025 = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/2025_load_profile.xlsx"
dn_excluded_list = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/dn_exluded_list.xlsx"
ls_load_local = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ls_load_local.xlsx"
ls_load_pocket = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ls_load_pocket.xlsx"
relay_location = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/relay_location.xlsx"
substation_masterlist = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/substation_masterlist.xlsx"
ufls_assignment = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ufls_assignment.xlsx"
uvls_assignment = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/uvls_assignment.xlsx"
ufls_setting = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/ufls_setting.xlsx"
uvls_setting = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/uvls_setting.xlsx"
log_defeated_relay = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/database/log_defeated_relay.xlsx"

# masterlist_relay_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/db_masterlist_ls_relay.xlsx"

# input
review_year = "2024"
group_tripId = "nlai_proi_kjng_nuni"
subzone = "KL"
geo_loc = "KlangValley"
substation = "TJID"
stage = "stage_3"

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# read file
load_profile = pd.read_excel(load_profile_2025)
ufls_assignment = pd.read_excel(ufls_assignment)
uvls_assignment = pd.read_excel(uvls_assignment)
ls_load_local = pd.read_excel(ls_load_local)
ls_load_pocket = pd.read_excel(ls_load_pocket)
dn_excluded_list = pd.read_excel(dn_excluded_list)
log_defeated = pd.read_excel(log_defeated_relay)
relay_location = pd.read_excel(relay_location)
substation_masterlist = pd.read_excel(substation_masterlist)
ufls_setting = pd.read_excel(ufls_setting)
uvls_setting = pd.read_excel(uvls_setting)

ls = LoadShedding(
    review_year=review_year,
    load_profile=load_profile,
    ufls_assignment=ufls_assignment,
    uvls_assignment=uvls_assignment,
    ls_load_local=ls_load_local,
    ls_load_pocket=ls_load_pocket,
    dn_excluded_list=dn_excluded_list,
    log_defeated=log_defeated,
    relay_location=relay_location,
    substation_masterlist=substation_masterlist,
    ufls_setting=ufls_setting,
    uvls_setting=uvls_setting,
)

def sort_by_stage(df, review_year, export_file_name):
    df["sort_key"] = df[review_year].str.extract(r"stage_(\d+)").astype(int)
    df_sorted = df.sort_values(by="sort_key", ascending=True)
    df_sorted = df_sorted.drop(columns=["sort_key"]).reset_index(drop=True)
    print(df_sorted)
    df_sorted.to_excel(
        rf"C:\Users\fairizat\Desktop\{export_file_name}.xlsx", index=False
    )


# all_load

# print("substation with load", ls.masterlist_load.head(30))
# print("Load by subs", ls.load_by_subs)
# mnemonic='TGLN'
# print(f"Load for {mnemonic}", ls.find_subs_load(mnemonic=mnemonic))

# print("Load by subs", ls.ufls.ls_active)
# print("LS active filter by Delivery Point", ls.ufls.ls_active_by_dp)
# print("LS active filter by Tripping Group", ls.ufls.ls_active_by_grpId)
# sort_by_stage(ls.ufls.ls_active_by_dp, review_year, "ufls_2024_list")

print(
    f"list of ufls substation by stage {stage}",
    ls.ufls.ls_active_by_stage(stage=stage),
    f"with total load {ls.ufls.ls_active_by_stage(stage=stage)["Pload (MW)"].sum()}",
)
# print(
#     f"UFLS {stage} with total load {ls.ufls.ls_active_by_stage(stage=stage)["Pload (MW)"].sum()}",
# )
# sort_by_stage(ls.ufls.ls_active_by_stage(stage=stage), review_year, "ufls_2025_stage1_list")

# print(
#     f"List ulfs assignment by location {geo_loc} is ",
#     ls.ufls.ls_active_by_geoLoc(geo_loc=geo_loc),
#     "and total quantum is ",
#     ls.ufls.ls_active_by_geoLoc(geo_loc=geo_loc)["Pload (MW)"].sum(),
# )

# print(
#     f"List ufls by location {geo_loc} and stage {stage}",
#     ls.ufls.ls_active_by_geoLoc_stage(stage=stage, geo_loc=geo_loc),
# )

# print(
#     f"Subtation UFLS for {substation}", ls.ufls.ls_active_by_subs(subs_name=substation)
# )


# print(
#     "DN Excluded list",
#     ls.dn_excluded_list
# )


# print(f"list of ufls all substation", ls.ufls.ls_active_by_dp)

# print(f"List of DN exclusion", ls.ufls.dn_excluded_list)
# sort_by_stage(ls.ufls.dn_excluded_list, review_year, "DN_2025_exclusion_list")


# print(
#     f"list of ufls grp assignment by stage {stage}",
#     ls.ufls.review_by_stage_grpId(stage=stage),
# )
# print(
#     f"Total sum of ufls grp assignment by stage {stage}",
#     ls.ufls.review_by_stage_grpId(stage=stage)['Pload (MW)'].sum(),
# )

# print(f"list of quantum ufls {review_year}", ls.ufls.quantum_stage_by_grpId())


# # print(ufls_grpId)
# # all_load.to_excel(r"C:/Users/fairizat/Desktop/masterlist_25Nov.xlsx", index=False)
# ls.ufls.filter_by_geoLoc_stage(stage=stage, geo_loc=geo_loc).to_excel(
#     r"C:/Users/fairizat/Desktop/masterlist_25Nov.xlsx", index=False
# )
# existing assigned
# grp_trip_list, quantum = ufls.assigned_quantum_filter_by_group_id(
#     group_id=group_tripId
# )
# gmsubzone_list, subzone_quantum = ufls.assigned_quantum_filter_by_GMSubzone(
#     subzone=subzone
# )
# geoloc_list, geoloc_quantum = ufls.assigned_quantum_filter_by_geo_loc(
#     geo_loc=geo_loc
# )
# subs_list, subs_quantum = ufls.assigned_quantum_filter_by_substation(
#     substation=substation
# )

# # available ls - assigned + non-assigned
# avail_geoloc, geoloc_availquantum = ufls.available_quantum_filter_by_geo_loc(
#     geo_loc=geo_loc
# )
# avail_subzone, subzone_availquantum = ufls.available_quantum_filter_by_GMSubzone(
#     subzone=subzone
# )
# avail_subs, subs_availquantum = ufls.available_quantum_filter_by_substation(
#     substation=substation
# )
# # print(grp_trip_list)
# # print(gmsubzone_list)
# # print(geoloc_list)
# # print(subs_list)
# # print(ufls.quantum_assigned_ls)
# print(all_load)
# print("Available load by subzone", avail_subzone)
# print('Available load by Substation', avail_subs)
# print('Available ls', ufls.available_quantum_ls)
