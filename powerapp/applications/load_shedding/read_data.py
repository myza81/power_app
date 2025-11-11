import pandas as pd
import xlrd
import re

file_path = "D:/myIjat/Job/1_Operation/Network/System_Defences/EMLS/EMLS_2013_rawa_data.xls"

emls_df = pd.read_excel(file_path, skiprows=2, usecols=list(range(12)))
header = emls_df.columns
emls_subs_list = emls_df["SUBSTATION"].values
# print(emls_subs_list)

workbook = xlrd.open_workbook(file_path)
print(workbook)

sheet = workbook.sheet_by_index(0)
print(sheet)

merged_cells = sheet.merged_cells
# print(merged_cells)

for r_start, r_end, c_start, c_end in merged_cells:
    merged_value = emls_df.iloc[r_start, c_start]
