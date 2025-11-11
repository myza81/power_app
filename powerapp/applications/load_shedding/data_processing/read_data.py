import pandas as pd
import xlrd
import re
from pathlib import Path


def find_project_root(start_path, folder_name):
    for parent in start_path.parents:
        if parent.name == folder_name:
            return parent
    raise FileNotFoundError(f"Could not find a parent directory named '{folder_name}' from {start_path}")


script_dir = Path(__file__).resolve()
data_path = find_project_root(script_dir, 'work')
psse_load_data = data_path / 'data' / 'psse_load_2025.xlsx'
load_data_df = pd.read_excel(psse_load_data, skiprows=None)
relay_population = data_path / 'data' / 'ufls_population.xlsx'
relay_data_df = pd.read_excel(relay_population, skiprows=None)


# print('data_folder', load_data_df)
print('relay_data_df', relay_data_df)

# emls_df = pd.read_excel(file_path, skiprows=2, usecols=list(range(12)))
# header = emls_df.columns
# emls_subs_list = emls_df["SUBSTATION"].values
# # print(emls_subs_list)

# workbook = xlrd.open_workbook(file_path)
# print(workbook)

# sheet = workbook.sheet_by_index(0)
# print(sheet)

# merged_cells = sheet.merged_cells
# # print(merged_cells)

# for r_start, r_end, c_start, c_end in merged_cells:
#     merged_value = emls_df.iloc[r_start, c_start]
