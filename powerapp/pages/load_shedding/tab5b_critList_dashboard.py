import streamlit as st
from css.streamlit_css import custom_metric_one_line
from pages.load_shedding.tab4_simulator import potential_ls_candidate
from pages.load_shedding.helper import remove_duplicates_keep_nan


def critical_list_metric():
    st.markdown("---")
    st.markdown("**🌍 Zone-wise Breakdown**")

    ls_obj = st.session_state.get("loadshedding")

    if not ls_obj:
        st.error("Load shedding data not found in session state.")
        return

    df_raw_cand, cand_with_crit, cand_without_crit = potential_ls_candidate(
        ls_obj)

    cand_with_crit_uniq = remove_duplicates_keep_nan(
        cand_with_crit, "local_trip_id")

    cand_without_crit_uniq = remove_duplicates_keep_nan(
        cand_without_crit, "local_trip_id")

    crit_zone = cand_with_crit_uniq.groupby(
        ["zone"], as_index=False, dropna=False
    ).agg({"Load (MW)": "sum"})

    no_crit_zone = cand_without_crit_uniq.groupby(
        ["zone"], as_index=False, dropna=False
    ).agg({"Load (MW)": "sum"})

    zones = df_raw_cand["zone"].dropna().unique(
    ) if "zone" in df_raw_cand.columns else []

    if len(zones) > 0:
        num_zones = len(zones)
        num_cols = min(4, num_zones)
        if num_cols < 2 and num_zones > 1:
            num_cols = 2

        zone_cols = st.columns(num_cols)

        for idx, zone in enumerate(zones):
            col_idx = idx % num_cols

            with zone_cols[col_idx]:
                zoneDemand = ls_obj.zone_load_profile(zone)
                crit_zoneMW = crit_zone.loc[crit_zone["zone"] == zone]["Load (MW)"].sum(
                )
                no_crit_zoneMW = no_crit_zone.loc[no_crit_zone["zone"] == zone]["Load (MW)"].sum(
                )
                potential_quantum = crit_zoneMW + no_crit_zoneMW

                zone_no_crit = cand_without_crit.loc[cand_without_crit["zone"] == zone]
                pocket_no_crit = zone_no_crit.loc[zone_no_crit["dp_type"] == "Pocket"]["Load (MW)"].sum(
                )
                local_no_crit = zone_no_crit.loc[zone_no_crit["dp_type"]
                                                 == "Local_Load"]["Load (MW)"].sum()
                lpc_no_crit = zone_no_crit.loc[zone_no_crit["dp_type"] == "LPC"]["Load (MW)"].sum(
                )

                zone_crit = cand_with_crit.loc[cand_with_crit["zone"] == zone]
                pocket_crit = zone_crit.loc[zone_crit["dp_type"] == "Pocket"]["Load (MW)"].sum(
                )
                local_crit = zone_crit.loc[zone_crit["dp_type"]
                                           == "Local_Load"]["Load (MW)"].sum()
                lpc_crit = zone_crit.loc[zone_crit["dp_type"] == "LPC"]["Load (MW)"].sum(
                )

                custom_metric_one_line(
                    title=f"🇱🇷 {zone}:",
                    values_obj={
                        "Demand": f"{zoneDemand:,.0f} MW",
                        "Potential Quantum": f"{potential_quantum:,.0f} MW",
                        "Critical List": f"{crit_zoneMW:,.0f} MW",

                    },
                    title_size="18px",
                    item_color="#9ca3af",
                    item_size="13px",
                    item_weight=700,
                    value_size="15px",
                    value_weight=700,
                    value_color="#2E86C1",
                )

                custom_metric_one_line(
                    title=f"Potential 1:",
                    values_obj={
                        "W/out Critical List": f"{no_crit_zoneMW:,.0f} MW ({no_crit_zoneMW/zoneDemand*100:,.2f})%",
                        "Net LPC": f"{lpc_no_crit:,.0f} MW",
                        "Net Local Load": f"{local_no_crit:,.0f} MW",
                        "Net Pocket Load": f"{pocket_no_crit:,.0f} MW",
                        "Net Local + LPC": f"{local_no_crit+lpc_no_crit:,.0f} MW ({(local_no_crit+lpc_no_crit)/zoneDemand*100:,.2f})%",
                    },
                    title_size="18px",
                    item_color="#9ca3af",
                    item_size="13px",
                    item_weight=700,
                    value_size="15px",
                    value_weight=700,
                    value_color="#2E86C1",
                )

                custom_metric_one_line(
                    title=f"Potential 2:",
                    values_obj={
                        "Potential Quantum": f"{potential_quantum:,.0f} MW ({potential_quantum/zoneDemand*100:,.2f})%",
                        "LPC": f"{lpc_crit+lpc_no_crit:,.0f} MW",
                        "Local Load": f"{local_crit+local_no_crit:,.0f} MW",
                        "Pocket Load": f"{pocket_crit+pocket_no_crit:,.0f} MW",
                        "Local + LPC": f"{local_crit+local_no_crit+lpc_no_crit+lpc_crit:,.0f} MW ({(local_crit+local_no_crit+lpc_no_crit+lpc_crit)/zoneDemand*100:,.2f})%",
                    },
                    title_size="18px",
                    item_color="#9ca3af",
                    item_size="13px",
                    item_weight=700,
                    value_size="15px",
                    value_weight=700,
                    value_color="#2E86C1",
                )
