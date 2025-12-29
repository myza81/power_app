# tab4a_sim_conflict.py
import pandas as pd
import streamlit as st
from pages.load_shedding.helper import join_unique_non_empty, find_latest_assignment


# Update your stage_conflict.py file:

def handle_ufls_case(df, ls_latest_cols):
    """Handle UFLS review year logic"""
    stage_mask = df['Sim. Oper. Stage'].isin(['stage_1', 'stage_2', 'stage_3'])
    has_values_mask = df[ls_latest_cols].notna().any(axis=1)
    condition = stage_mask & has_values_mask
    
    if condition.any():
        def get_conflict_cols(row):
            cols_with_values = [f"{col} ({row[col]})"  for col in ls_latest_cols if pd.notna(row[col])]
            return ", ".join(cols_with_values) if cols_with_values else ""
        
        conflict_cols = df[condition].apply(get_conflict_cols, axis=1)
        df.loc[condition, 'Conflict_Columns'] = conflict_cols
        
        # FIX: Handle None/NaN values properly
        for idx in df[condition].index:
            current_flag = df.at[idx, 'Flag']
            # Convert to string and handle NaN/None
            if pd.isna(current_flag):
                current_flag = ''
            else:
                current_flag = str(current_flag)
            
            # Remove any existing "Conflict:" to avoid duplicates
            if 'Conflict:' in current_flag:
                current_flag = current_flag.replace('Conflict:', '').strip()
            
            # Append "Conflict:" only if not empty
            if current_flag:
                df.at[idx, 'Flag'] = f"{current_flag} Conflict:"
            else:
                df.at[idx, 'Flag'] = "Conflict:"
    
    return df


def handle_uvls_case(df, ls_latest_cols):
    """Handle UVLS (non-UFLS) review year logic"""
    ufls_cols = [col for col in ls_latest_cols if col.startswith('UFLS')]
    
    for ufls_col in ufls_cols:
        if ufls_col not in df.columns:
            continue
            
        condition = (
            df['Sim. Oper. Stage'].notna() &
            df[ufls_col].isin(['stage_1', 'stage_2', 'stage_3'])
        )
        
        if condition.any():
            # Create conflict text with column name and value
            conflict_text = f"{ufls_col} (" + df.loc[condition, ufls_col].astype(str) + ")"
            df.loc[condition, 'Conflict_Columns'] = conflict_text
            
            # FIX: Handle None/NaN values properly
            for idx in df[condition].index:
                current_flag = df.at[idx, 'Flag']
                # Convert to string and handle NaN/None
                if pd.isna(current_flag):
                    current_flag = ''
                else:
                    current_flag = str(current_flag)
                
                # Remove any existing "Conflict:" to avoid duplicates
                if 'Conflict:' in current_flag:
                    current_flag = current_flag.replace('Conflict:', '').strip()
                
                # Append "Conflict:" only if not empty
                if current_flag:
                    df.at[idx, 'Flag'] = f"{current_flag} Conflict:"
                else:
                    df.at[idx, 'Flag'] = "Conflict:"
    
    return df


def stage_conflict(master_df, valid_candidate, ls_obj, review_year):
    """Main function to detect and flag conflicts"""
    
    df = master_df.copy()
    
    # Get shedding columns
    lshedding_columns = [
        col for col in valid_candidate.columns
        if any(k in col for k in ls_obj.LOADSHED_SCHEME)
        and not col.startswith(review_year[:4])
    ]
    
    ls_latest_cols = find_latest_assignment(lshedding_columns)
    
    # Merge with candidate data
    df_merge = pd.merge(
        df,
        valid_candidate[["assignment_id"] + ls_latest_cols],
        left_on="Assignment",
        right_on="assignment_id",
        how="left"
    )
    
    # Ensure Flag column exists
    if 'Flag' not in df_merge.columns:
        df_merge['Flag'] = ''
    
    # Apply conflict detection logic
    if review_year[:4] == "UFLS":
        df_merge = handle_ufls_case(df_merge, ls_latest_cols)
    else:
        df_merge = handle_uvls_case(df_merge, ls_latest_cols)
    
    # Clean up temporary columns
    df_merge = df_merge.drop(columns=["assignment_id"] + ls_latest_cols)
    
    return df_merge











# import pandas as pd
# import streamlit as st

# from pages.load_shedding.helper import join_unique_non_empty, find_latest_assignment
# from pages.load_shedding.tab4b_sim_dashboard import sim_dashboard
# from applications.load_shedding.helper import scheme_col_sorted
# from css.streamlit_css import custom_metric


# def handle_ufls_case(df, ls_latest_cols):
#     """Handle UFLS review year logic"""
#     stage_mask = df['Sim. Oper. Stage'].isin(['stage_1', 'stage_2', 'stage_3'])
#     has_values_mask = df[ls_latest_cols].notna().any(axis=1)
#     condition = stage_mask & has_values_mask

#     if condition.any():
#         def get_conflict_cols(row):
#             cols_with_values = [
#                 f"{col}({row[col]})" for col in ls_latest_cols if pd.notna(row[col])]
#             return ", ".join(cols_with_values) if cols_with_values else ""

#         conflict_cols = df[condition].apply(get_conflict_cols, axis=1)
#         df.loc[condition, 'Conflict_Columns'] = conflict_cols
#         df.loc[condition, 'Flag'] = df.loc[condition,
#                                            'Flag'] + 'Conflict:'  

#     return df


# def handle_uvls_case(df, ls_latest_cols):
#     """Handle UVLS (non-UFLS) review year logic"""
#     ufls_cols = [col for col in ls_latest_cols if col.startswith('UFLS')]

#     for ufls_col in ufls_cols:
#         condition = (
#             df['Sim. Oper. Stage'].notna() &
#             df[ufls_col].isin(['stage_1', 'stage_2', 'stage_3'])
#         )

#         if condition.any():
#             conflict_text = f"{ufls_col}(" + \
#                 df.loc[condition, ufls_col].astype(str) + ")"
#             df.loc[condition, 'Conflict_Columns'] = conflict_text
#             df.loc[condition, 'Flag'] = df.loc[condition,
#                                                'Flag'] + 'Conflict:'  

#     return df


# def stage_conflict(master_df, valid_candidate, ls_obj, review_year):
#     df = master_df.copy()

#     lshedding_columns = [
#         col for col in valid_candidate.columns
#         if any(k in col for k in ls_obj.LOADSHED_SCHEME)
#         and not col.startswith(review_year[:4])
#     ]

#     ls_latest_cols = find_latest_assignment(lshedding_columns)
#     df_merge = pd.merge(
#         df,
#         valid_candidate[["assignment_id"] + ls_latest_cols],
#         left_on="Assignment",
#         right_on="assignment_id",
#         how="left"
#     )

#     df_merge['Flag'] = df_merge['Flag'].str.replace(
#         r'Conflict:.*', '', regex=True)
#     df_merge['Flag'] = df_merge['Flag'].fillna('').str.strip()

#     df_merge['Conflict_Columns'] = ''

#     if review_year[:4] == "UFLS":
#         df_merge = handle_ufls_case(df_merge, ls_latest_cols)
#     else:
#         df_merge = handle_uvls_case(df_merge, ls_latest_cols)

#     df_merge["Flag"] = df_merge["Flag"] + df_merge["Conflict_Columns"]

#     df_merge = df_merge.drop(columns=["assignment_id"] + ls_latest_cols)

#     return df_merge
