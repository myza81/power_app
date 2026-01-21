import streamlit as st
import pandas as pd
import numpy as np
from pages.load_shedding.tab4_simulator import build_master_df, potential_ls_candidate


def critical_list_analytic():
    st.subheader("Critical List Analytic")

    barchart_container = st.container()

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    raw_cand = potential_ls_candidate(ls_obj)

    # st.write(raw_cand)

    with barchart_container:
        barchart1, barchart2, barchart3 = st.columns(3)

        trip_duplicates = raw_cand[raw_cand.duplicated(subset=['local_trip_id'], keep=False)]
        st.write("trip_duplicates")
        st.write(trip_duplicates)
        drop_duplicate = raw_cand.drop_duplicates(subset=["local_trip_id"])
        st.write("drop_duplicate")
        st.write(drop_duplicate)

        with barchart1:

          pass

          

            # df_final = pd.concat([same_vals, different_vals_cleaned]).sort_index()

            # zone_list = zone_list.drop_duplicates(subset=["local_trip_id"])
            # st.write(different_vals)

            # zone_list["load_type"] = np.where(
            #     zone_list["critical_list"].notna(), "critical", "non_critical")

            # st.write((zone_list.loc[zone_list["zone"] == "South"]))
            # st.write((zone_list.loc[zone_list["zone"] == "South"])["critical_load"].sum() )

            # sum_cols = ["critical_load", "non_critical_load"]

            # agg_dict = ({col: "sum" for col in sum_cols}
            # )

            # zone_list_grp = (
            #     zone_list
            #     .groupby(
            #         ["zone"],
            #         dropna=False,
            #         as_index=False
            #     )
            #     .agg(agg_dict)
            #     # .reset_index()
            # )
            # st.write(zone_list_grp)

        #     df_melted_staging = staging_ls.melt(
        #         id_vars=['zone', scheme],
        #         value_vars=['Shedding'],
        #         var_name='load_type',
        #         value_name='mw'
        #     )

        # scheme_list = staging_ls[scheme].unique().tolist()

        # if not scheme_list:
        #     sorted_stages = []
        # else:
        #     sorted_stages = sorted(scheme_list, key=stage_sort)

        # dynamic_color_map = get_dynamic_colors(categories=sorted_stages)

        # create_stackedBar_chart(
        #     df=df_melted_staging,
        #     x_col="zone",
        #     y_col="mw",
        #     y_label="Load Shedd Quantum (MW)",
        #     color_col=scheme,
        #     color_discrete_map=dynamic_color_map,
        #     title=f"{scheme} Operational Staging - by Regional Zone",
        #     category_order={scheme: sorted_stages},
        #     key=f"regional_load_shedding_staging_stackedBar{scheme}"
        # )
