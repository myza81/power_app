import streamlit as st
import pandas as pd
import numpy as np
from pages.load_shedding.helper import stage_sort
from applications.load_shedding.helper import scheme_col_sorted
from applications.load_shedding.ufls_setting import UFLS_TARGET_QUANTUM
from applications.load_shedding.uvls_setting import UVLS_TARGET_QUANTUM
from css.streamlit_css import custom_metric


def sim_dashboard(simulator_df, candidate_df, scheme):
    st.subheader("📊 Load Shedding Assignment Simulator")

    ls_obj = st.session_state.get("loadshedding")
    lprofile_obj = st.session_state["loadprofile"]

    if not ls_obj or not lprofile_obj:
        st.error("Load shedding data not found in session state.")
        return

    ls_quantum = {
        "UFLS": UFLS_TARGET_QUANTUM,
        "UVLS": UVLS_TARGET_QUANTUM
    }
    target_quantum = ls_quantum.get(scheme, 0)

    total_system_mw = lprofile_obj.totalMW()
    target_quantum_ls = target_quantum * total_system_mw

    st.caption(
        f"Target Load Shed: {target_quantum_ls:,.1f} MW ({target_quantum*100}% of {total_system_mw:,.0f} MW)")

    # Merge simulator data with candidate data
    simulator = simulator_df.copy().rename(
        columns={"Assignment": "assignment_id", })

    sim_ls = pd.merge(
        candidate_df,
        simulator[["assignment_id", "Sim. Oper. Stage"]],
        on="assignment_id",
        how="left"
    ).rename(columns={"Load (MW)": "Load Shed (MW)"})

    # Optional: Show merged data
    # st.dataframe(sim_ls)

    # Check if we have data
    if sim_ls.empty:
        st.warning("No load shedding assignments found for simulation.")
        return

    c1, c2, _, c3 = st.columns([2, 2.5, 0.2, 2])

    with c1:
        st.markdown("**📈 By Stage**")

        # Group by stage
        sim_stage = sim_ls.groupby(["Sim. Oper. Stage"], as_index=False)[
            "Load Shed (MW)"].sum()

        if not sim_stage.empty:
            # Round and convert to int
            sim_stage["Load Shed (MW)"] = sim_stage["Load Shed (MW)"].round().astype(
                int)

            # Calculate percentage contribution to target quantum
            sim_stage["% Contribution"] = np.where(
                total_system_mw > 0,
                (sim_stage["Load Shed (MW)"] /
                 total_system_mw * 100).round(1),
                0
            )

            # Sort by stage
            ls_table = scheme_col_sorted(
                sim_stage, "Sim. Oper. Stage")

            # Display with formatting
            display_df = ls_table.style.format({
                "Load Shed (MW)": "{:,}",
                "% Contribution": "{:.1f}%"
            })

            st.dataframe(display_df, hide_index=True,
                         width="content", height=300)

            # Add total row
            total_shed_stage = sim_stage["Load Shed (MW)"].sum()
            percentage_of_target = (
                total_shed_stage / target_quantum_ls * 100) if target_quantum_ls > 0 else 0

            st.caption(
                f"**Total Shed by Stage:** {total_shed_stage:,.0f} MW "
                f"({percentage_of_target:.1f}% of target)"
            )
        else:
            st.info("No stage-based load shedding data available")

    with c2:
        st.markdown("**🗺️ By Zone & Stage**")

        # Group by zone and stage
        sim_zone_stage = sim_ls.groupby(
            ["zone", "Sim. Oper. Stage"], as_index=False
        ).agg({"Load Shed (MW)": "sum"})

        if not sim_zone_stage.empty:
            # Round and convert to int
            sim_zone_stage["Load Shed (MW)"] = sim_zone_stage["Load Shed (MW)"].round(
            ).astype(int)

            # Merge with load profile to get zone totals
            load_profile = ls_obj.load_profile.groupby(
                "zone")["Load (MW)"].sum().reset_index()
            sim_merged = pd.merge(
                sim_zone_stage, load_profile, on="zone", how="left")

            # Calculate percentage of zone load
            sim_merged["% of Zone Load"] = np.where(
                sim_merged["Load (MW)"] > 0,
                (sim_merged["Load Shed (MW)"] /
                 sim_merged["Load (MW)"] * 100).round(1),
                0
            )

            # Sort and select columns
            sim_zone = scheme_col_sorted(sim_merged, "Sim. Oper. Stage")[
                ["Sim. Oper. Stage", "zone",
                    "Load Shed (MW)", "% of Zone Load"]
            ]

            # Display with formatting
            display_zone = sim_zone.style.format({
                "Load Shed (MW)": "{:,}",
                "% of Zone Load": "{:.1f}%",
            })

            st.dataframe(display_zone, hide_index=True,
                         width="content", height=300)
        else:
            st.info("No zone-based load shedding data available")

    with c3:
        st.markdown("**📊 Summary Metrics**")

        # Calculate total load shed
        total_shed_stage = sim_stage["Load Shed (MW)"].sum()

        # System metrics
        custom_metric(
            "Simulator Total Quantum",
            f"{total_shed_stage:,.0f} MW",
            f"{(total_shed_stage/total_system_mw)*100:.1f}% of System Load",
        )

        custom_metric(
            "Target Quantum",
            f"{target_quantum_ls:,.0f} MW",
            f"{target_quantum*100}% of System Load",
        )

        achievement = (total_shed_stage / target_quantum_ls *
                       100) if target_quantum_ls > 0 else 0

        value_color = "#2E86C1" if achievement > 95 else "#B41C17"
        delta_color = "#2ECC71" if achievement > 95 else "#EC5353"
        delta_bgcolor = "#0E3421" if achievement > 95 else "#780630"

        custom_metric(
            label="Target Achievement",
            value=f"{achievement:.1f}%",
            value_color=value_color,
            delta_text=f"{total_shed_stage:,.0f} / {target_quantum_ls:,.0f} MW",
            delta_color=delta_color,
            delta_bgcolor=delta_bgcolor
        )

    # Zone-wise breakdown
    st.markdown("---")
    st.markdown("**🌍 Zone-wise Breakdown**")

    zones = sim_zone_stage["zone"].dropna().unique(
    ) if "zone" in sim_zone_stage.columns else []

    if len(zones) > 0:
        num_zones = len(zones)
        num_cols = min(4, num_zones)
        if num_cols < 2 and num_zones > 1:
            num_cols = 2

        zone_cols = st.columns(num_cols)

        for idx, zone in enumerate(zones):
            col_idx = idx % num_cols

            with zone_cols[col_idx]:
                zone_data = sim_zone_stage[sim_zone_stage["zone"] == zone]
                zone_total_shed = zone_data["Load Shed (MW)"].sum()
                zone_profile_total = lprofile_obj.regional_loadprofile(zone)

                if zone_profile_total > 0:
                    percentage = (zone_total_shed / zone_profile_total) * 100

                    custom_metric(
                        label=f"{zone}",
                        value=f"{zone_total_shed:,.0f} MW",
                        delta_text=f"{percentage:.1f}% of zone load",
                    )


def safe_divide(numerator, denominator, default=0):
    """Safe division function to handle zero denominator."""
    return numerator / denominator if denominator != 0 else default
