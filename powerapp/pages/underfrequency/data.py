import pandas as pd

load_profile_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/load_profile.xlsx"
ufls_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/UFLS_UVLS/2025_Review/ufls.xlsx"
group_tripId = 'GBID_KSTL'


load_profile = pd.read_excel(load_profile_path)
ufls = pd.read_excel(ufls_path)
# print(load_profile)
# print(ufls)
ufls_load = ufls.merge(
    load_profile, 
    left_on=['Mnemonic', 'Assigned_Feeders'], 
    right_on=['Mnemonic', 'Id'], 
    how='inner')
# print(ufls_load)



def quantum_by_groupId(df, groupId):
    group_trip = df[df['TripGroup_id'] == groupId]
    total_grp_load = group_trip['Pload (MW)'].sum()
    print(f'Total Group Load: {groupId} is {total_grp_load}')
    return group_trip, total_grp_load

def total_loadquantum_ufls(df):
    total_load = df.loc[df['TripGroup_id'].notna(),'Pload (MW)'].sum()
    print(f'Total Load Quantum is {total_load}')
    return total_load



print(quantum_by_groupId(df=ufls_load, groupId=group_tripId))
print(total_loadquantum_ufls(df=ufls_load))





