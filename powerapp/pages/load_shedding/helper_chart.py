import textwrap
import plotly.express as px
import streamlit as st


def create_donut_chart(
    df,
    values_col,
    names_col,
    title,
    key,
    title_width=30,
    title_x=0,
    title_font_size=18,
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
    lagend_xanchor="left",
    annotations="",
    margin=dict(t=80, b=40, l=40, r=20),
    height=250,
    xaxis_label=None,
    yaxis_label=None,
    anno_x=0.5,
    anno_y=0.5,
    anno_fsize=18
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
        xaxis_title=xaxis_label,
        yaxis_title=yaxis_label,
        showlegend=showlegend,
        height=height,
        margin=margin,
        annotations=chart_annotations(annotations, anno_x, anno_y, anno_fsize),
        legend=chart_legend(orientation=legend_orient,
                            legend_x=legend_x, legend_y=legend_y, lagend_xanchor=lagend_xanchor),

    )
    st.plotly_chart(fig, width="content", key=key)


def create_bar_chart(
    df,
    x_col,
    y_col,
    title,
    key,
    title_width=30,
    title_x=0,
    title_font_size=18,
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
    lagend_xanchor="left",
    annotations="",
    margin=dict(t=80, b=40, l=40, r=20),
    color_discrete_map={},
    color_discrete_sequence=["#1f77b4"],
    height=400,
    xaxis_label=None,
    yaxis_label=None,
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
        xaxis_title=xaxis_label,
        yaxis_title=yaxis_label,
        height=height,
        showlegend=showlegend,
        legend=chart_legend(orientation=legend_orient,
                            legend_x=legend_x, legend_y=legend_y, lagend_xanchor=lagend_xanchor),
        margin=margin,
        legend_title_text="",
    )

    st.plotly_chart(fig, width="content", key=key)


def create_stackedBar_chart(
    df,
    x_col,
    y_col,
    color_col,
    title,
    key,
    title_width=30,
    title_x=0,
    title_fsize=18,
    showlegend=False,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
    lagend_xanchor="left",
    annotations="",
    margin=dict(t=80, b=40, l=40, r=20),
    color_discrete_map={},
    category_order={},
    height=400,
    xaxis_label=None,
    yaxis_label=None,
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
        title=chart_title(title, title_width, title_x, title_fsize),
        xaxis_title=xaxis_label,
        yaxis_title=yaxis_label,
        height=height,
        showlegend=showlegend,
        legend=chart_legend(orientation=legend_orient,
                            legend_x=legend_x, legend_y=legend_y, lagend_xanchor=lagend_xanchor),
        margin=margin,
    )

    st.plotly_chart(fig, width="content", key=key)


def create_groupBar_chart(
    df,
    x_col,
    y_col,
    color_col,
    title,
    key,
    title_fsize=18,
    title_width=30,
    title_x=0,
    legend_x=0,
    legend_y=-0.2,
    legend_orient="h",
    lagend_xanchor="left",
    margin=dict(t=80, b=40, l=40, r=20),
    color_discrete_map={},
    category_order={},
    height=450,
    showlegend=False,
    xaxis_label=None,
    yaxis_label=None,
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
        title=chart_title(title, title_width, title_x, title_fsize),
        xaxis_title=xaxis_label,
        yaxis_title=yaxis_label,
        height=height,
        showlegend=showlegend,
        legend=chart_legend(orientation=legend_orient,
                            legend_x=legend_x, legend_y=legend_y, lagend_xanchor=lagend_xanchor),
        margin=margin,
    )
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, width="content", key=key)


def chart_title(title, title_width, title_x, title_fsize):
    display_title = "<br>".join(textwrap.wrap(title, width=title_width))
    return dict(
        text=display_title,
        font={"size": title_fsize},
        x=title_x,
        xanchor="left",
    )


def chart_legend(orientation, legend_x, legend_y, lagend_xanchor):
    return dict(
        y=legend_y,
        x=legend_x,
        xanchor=lagend_xanchor,
        orientation=orientation,
        title=None,
    )


def chart_annotations(annotations, anno_x, anno_y, anno_fsize):
    return ([
        dict(
            text=annotations,
            x=anno_x,
            y=anno_y,
            font_size=anno_fsize,
            showarrow=False
        )
    ])


def get_dynamic_colors(categories, fix_color={}):

    standard_colors = px.colors.qualitative.Safe
    color_idx = 0
    for cat in categories:
        if cat not in fix_color:
            fix_color[cat] = standard_colors[color_idx % len(standard_colors)]
            color_idx += 1

    return fix_color
