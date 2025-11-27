import pandas as pd
import os
import sys

class LoadSheddingData:
    def __init__(self, data_dir="data"):

        def get_path(filename):
            # Assuming 'data' folder is next to the script, you might need
            # to adjust the path based on your project structure.
            return os.path.join(data_dir, filename)

        self.dn_excluded_list = read_ls_data(get_path("dn_exluded_list.xlsx"))
        self.ufls_assignment = read_ls_data(get_path("ufls_assignment.xlsx"))
        self.uvls_assignment = read_ls_data(get_path("uvls_assignment.xlsx"))
        self.ls_load_local = read_ls_data(get_path("ls_load_local.xlsx"))
        self.ls_load_pocket = read_ls_data(get_path("ls_load_pocket.xlsx"))
        self.relay_location = read_ls_data(get_path("relay_location.xlsx"))
        self.substation_masterlist = read_ls_data(
            get_path("substation_masterlist.xlsx")
        )
        self.ufls_setting = read_ls_data(get_path("ufls_setting.xlsx"))
        self.uvls_setting = read_ls_data(get_path("uvls_setting.xlsx"))


def read_ls_data(file_path):
    try: 
        return pd.read_excel(file_path)
    except FileNotFoundError:
        log_error(f"File not found: {file_path}")
        return None
    except Exception as e:
        log_error(f"Error processing file '{file_path}': {str(e)}")
        return None


def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)


# data = LoadSheddingData()
# print(data.substation_masterlist)
