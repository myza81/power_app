import time
import textwrap
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Optional, Sequence, Any
from collections import defaultdict
from applications.load_shedding.load_profile import (
    load_profile_metric,
)


def display_ls_metrics(scheme, df, load_profile):

    st.dataframe(df)

    col1, col2, col3 = st.columns([2.0, 3.5, 2.5])

    total_MD = load_profile["Pload (MW)"].sum()
    is_scheme_valid = df[scheme].notna() & (df[scheme] != "nan") & (df[scheme] != "#na")

    total_scheme_ls = df.loc[is_scheme_valid, "Pload (MW)"].sum()

    if total_MD == 0:
        pct_scheme_ls = 0
    else:
        pct_scheme_ls = (total_scheme_ls / total_MD) * 100

    zones = ["North", "KlangValley", "South", "East"]
    zone_data = {
        zone: load_profile_metric(df=df, zone=zone, scheme=scheme) for zone in zones
    }
    zone_MD = {zone: load_profile_metric(df=load_profile, zone=zone) for zone in zones}

    with col1:
        st.metric(
            label=f"Total {scheme} Load Quantum",
            value=f"{int(total_scheme_ls):,} MW",
        )
        st.metric(
            label=f"% {scheme} Quantum Over MD",
            value=f"{pct_scheme_ls:.1f}%",
        )

    with col2:
        col2a, col2b = st.columns(2)

        with col2a:
            zone_metric(col2a, "North", zone_data, zone_MD)
            zone_metric(col2a, "KlangValley", zone_data, zone_MD)

        with col2b:
            zone_metric(col2b, "South", zone_data, zone_MD)
            zone_metric(col2b, "East", zone_data, zone_MD)

    with col3:
        pass


def zone_metric(col, zone_name, zone_data, zone_MD):
    ls = int(zone_data[zone_name])
    md = int(zone_MD[zone_name])
    pct = (ls / md) * 100

    with col:
        st.metric(
            label=f"{zone_name} Load Shedding",
            value=f"{ls:,} MW",
        )
        st.markdown(
            f"<p style='margin-top:-25px; color:gray; font-size:13px;'>{pct:.1f}% of total {zone_name} MD</p>",
            unsafe_allow_html=True,
        )


def show_temporary_message(message_type, message, duration=3):
    placeholder = st.empty()

    if message_type == "info":
        placeholder.info(message)
    elif message_type == "success":
        placeholder.success(message)
    elif message_type == "warning":
        placeholder.warning(message)

    time.sleep(duration)

    placeholder.empty()


def find_latest_assignment(ls_scheme_list):
    # Filter: remove items with extra characters after numbers
    pattern = r"^(\w+)_(\d+)$"  # word_numbers (nothing after numbers)
    filtered = []

    for item in ls_scheme_list:
        match = re.match(pattern, item)
        if match:
            prefix = match.group(1)
            number = match.group(2)
            filtered.append((prefix, int(number), item))

    # Group by prefix and find max number
    groups = defaultdict(list)

    for prefix, number, item in filtered:
        groups[prefix].append((number, item))

    # Get latest for each group
    result = []
    for prefix, items_list in sorted(groups.items()):
        if items_list:
            # Sort by number (descending) and get first
            items_list.sort(key=lambda x: x[0], reverse=True)
            result.append(items_list[0][1])

    return result


def create_donut_chart(
    df,
    values_col=None,
    names_col="",
    title="",
    title_width=30,
    title_x=0,
    title_font_size=18,
    key=None,
    annotations="",
    height=250,
    margin=dict(t=30, b=20, l=10, r=10),
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
):
    fig = px.pie(df, values=values_col, names=names_col, hole=0.5)

    fig.update_traces(
        hoverinfo="label+percent+value",
        texttemplate="<b>%{label}</b><br>%{value:,.0f} MW<br>(%{percent})",
        textfont_size=10,
        textposition="auto",
    )

    fig.update_layout(
        title=chart_title(title, title_width, title_x, title_font_size),
        showlegend=showlegend,
        height=height,
        margin=margin,
        annotations=[
            dict(text=annotations, x=0.5, y=0.5, font_size=18, showarrow=False)
        ],
        legend=chart_legend(orientation=legend_orient, loc_x=legend_x, loc_y=legend_y),
    )
    st.plotly_chart(fig, width="content", key=key)


def create_bar_chart(
    df,
    x_col="zone",
    y_col="mw",
    title="Regional Load Breakdown",
    title_width=30,
    title_x=0,
    title_font_size=18,
    color_discrete_map={},
    color_discrete_sequence=["#1f77b4"],
    y_label="Demand (MW)",
    height=400,
    key=None,
):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color_discrete_map=color_discrete_map,
        color_discrete_sequence=color_discrete_sequence,
    )

    fig.update_layout(
        title=chart_title(title, title_width, title_x, title_font_size),
        xaxis_title=None,
        yaxis_title=y_label,
        height=height,
        legend=dict(
            title=None,
            orientation="v",  # v=vertical. h=horizontal
            yanchor="middle",  # Center it vertically relative to the chart
            y=0.5,  # 0.5 is the middle of the Y-axis
            x=1.02,
        ),
        margin=dict(t=80, b=40, l=40, r=20),  # Standardize margins
        legend_title_text="",
    )

    st.plotly_chart(fig, width="content", key=key)


def create_stackedBar_chart(
    df,
    x_col="zone",
    y_col="mw",
    color_col="load_type",
    title="Regional Load Breakdown",
    title_width=30,
    title_x=0,
    title_font_size=18,
    y_label="Demand (MW)",
    color_discrete_map={},
    category_order={},
    height=450,
    key=None,
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode="stack",
        color_discrete_map=color_discrete_map,
        category_orders=category_order,
    )

    fig.update_layout(
        title=chart_title(title, title_width, title_x, title_font_size),
        xaxis_title=None,
        yaxis_title=y_label,
        height=height,
        showlegend=showlegend,
        legend=chart_legend(orientation=legend_orient, loc_x=legend_x, loc_y=legend_y),
    )

    st.plotly_chart(fig, width="content", key=key)


def create_groupBar_chart(
    df,
    x_col="zone",
    y_col="mw",
    color_col="load_type",
    title="Regional Load Breakdown",
    title_width=30,
    title_x=0,
    title_font_size=18,
    y_label="Demand (MW)",
    color_discrete_map={},
    category_order={},
    height=450,
    key=None,
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode="group",
        color_discrete_map=color_discrete_map,
        category_orders=category_order,
    )

    fig.update_layout(
        title=chart_title(title, title_width, title_x, title_font_size),
        xaxis_title=None,
        yaxis_title=y_label,
        height=height,
        showlegend=showlegend,
        legend=chart_legend(orientation=legend_orient, loc_x=legend_x, loc_y=legend_y),
    )
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, width="content", key=key)


def chart_title(title, title_width, title_x, title_font_size):
    display_title = "<br>".join(textwrap.wrap(title, width=title_width))
    return dict(
        text=display_title,
        x=title_x,
        font={"size": title_font_size},
        xanchor="center",
    )


def chart_legend(orientation, loc_x, loc_y):
    return dict(
        y=loc_y,
        x=loc_x,
        title=None,
        orientation=orientation,
    )


def get_dynamic_colors(categories, fix_color={}):

    standard_colors = px.colors.qualitative.Safe
    color_idx = 0
    for cat in categories:
        if cat not in fix_color:
            fix_color[cat] = standard_colors[color_idx % len(standard_colors)]
            color_idx += 1

    return fix_color


def stage_sort(stage_str):
    try:
        parts = stage_str.split("_")
        if len(parts) > 1 and parts[1].isdigit():
            return int(parts[1])
    except (ValueError, IndexError):
        pass
    return 999


def join_unique_non_empty(series):
    unique_vals = [str(v) for v in series.dropna().unique() if str(v).strip() != ""]
    return ", ".join(unique_vals) if unique_vals else None


def custom_table(table_title, table_content):
    display_title = "<br>".join(textwrap.wrap(table_title, width=40))

    # st.markdown(
    #     f"""<style>
    #         .table-container {{overflow: hidden; border: 1px solid #e6e9ef; border-radius: 5px; margin-top:10px;}}
    #         .custom-table {{width: 100%; border-collapse: collapse; font-family: 'Source Sans Pro', sans-serif; font-size: 12px; margin-bottom: 0 !important; display: flex; flex-direction: column; border: 1px solid transparent }}
    #         .custom-table thead {{display: table; width: 100%; table-layout: fixed; background-color: #BDBDBD;}}
    #         .custom-table tr {{text-align: center !important; display: table; width: 100%; table-layout: fixed;}}
    #         .custom-table tbody {{ display: block; max-height: 400px; overflow-y: scroll; width: 100%;}}
    #         .custom-table th, .custom-table td {{padding: 10px; border: 1px solid #e6e9ef; text-align: center; vertical-align: top;}}
    #         .custom-table tbody tr:nth-child(even) {{background-color: #f9f9f9;}}
    #         .table-title{{margin-top:30px; font-size:16px; font-weight: 600;}}</style><div class='table-title'>{display_title}</div><div class='table-container'>{table_content}</div>""",
    #     unsafe_allow_html=True
    # )

    st.markdown(
        f"""<style>
        .table-container {{max-height: 400px;overflow-y: auto;border: 1px solid #e6e9ef;border-radius: 5px;margin-top: 10px;}}
        .custom-table {{width: 100%;border-collapse: collapse; font-family: inherit; font-size: 13px; margin-bottom: 0 !important}}
        .custom-table thead th {{position: sticky;top: 0;background-color: #BDBDBD; color: black;z-index: 10;padding: 12px;text-align: center;border-bottom: 2px solid #e6e9ef;border-right: 1px solid #e6e9ef;}}
        .custom-table td {{padding: 10px;border: 1px solid #f0f2f6;text-align: center;vertical-align: top;}}
        .custom-table tbody tr:nth-child(even) {{background-color: #f9f9f9;}}
        .table-title {{margin-top: 30px;font-size: 16px;font-weight: 600;}}
        </style><div class='table-title'>{display_title}</div><div class='table-container'>{table_content}</div>
        """,
        unsafe_allow_html=True,
    )


def process_display_data(
    searched_df: pd.DataFrame, pocket_relay: pd.DataFrame, scheme_cols: List[str]
) -> pd.DataFrame:
    """Handles the merging and grouping logic for the main table."""

    df_merged = pd.merge(searched_df, pocket_relay, on="assignment_id", how="left")

    mappings = {
        "Zone": "zone",
        "State": "state",
        "Subzone": "gm_subzone",
        "Mnemonic": "mnemonic",
        "Substation": "substation_name",
        "Breaker(s)": "breaker_id",
        "Feeder Assignment": "feeder_id",
        "Voltage Level": "kV",
    }

    for display_col, raw_col in mappings.items():
        if display_col in df_merged.columns:
            df_merged[display_col] = df_merged[display_col].fillna(df_merged[raw_col])
        else:
            df_merged[display_col] = df_merged[raw_col]

    group_cols = scheme_cols + [
        "Substation",
        "Mnemonic",
        "assignment_id",
        "dp_type",
    ]
    agg_map = {
        "Zone": lambda x: ", ".join(x.astype(str).unique()),
        "Subzone": lambda x: ", ".join(x.astype(str).unique()),
        "State": lambda x: ", ".join(x.astype(str).unique()),
        "Breaker(s)": lambda x: ", ".join(x.astype(str).unique()),
        "Feeder Assignment": lambda x: ", ".join(x.astype(str).unique()),
        "Voltage Level": lambda x: ", ".join(x.astype(str).unique()),
    }

    return df_merged.groupby(group_cols, as_index=False, dropna=False).agg(agg_map)
