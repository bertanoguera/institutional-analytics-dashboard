import dash
from dash import Input, Output
import plotly.graph_objects as go

METHOD_ORDER = ["LECT", "PJBL", "PRBL", "FLIP", "CASE"]

METHOD_FULL = {
    "LECT": "Lectures",
    "PJBL": "Project-based learning",
    "PRBL": "Problem-based learning",
    "FLIP": "Flipped classroom",
    "CASE": "Case studies",
}

# multi-line tick labels    
METHOD_TICK = {
    "LECT": "Lectures",
    "PJBL": "Project-based<br>learning",
    "PRBL": "Problem-based<br>learning",
    "FLIP": "Flipped<br>classroom",
    "CASE": "Case studies",
}

COLOR_TOP     = "#378ADD"
COLOR_BOTTOM  = "#EF9F27"
COLOR_ANOMALY = "#E8443A"

# y axis starts here, truncated to make the small differences visible
Y_BASE = 1.5


def _gap_info(gap):
    sign = "+" if gap >= 0 else ""
    gap_str = f"{sign}{gap:.3f}"
    if gap > 0:
        pattern = "Normal pattern — top-rated courses show greater task diversity."
    else:
        pattern = (
            "Anomaly — bottom-rated courses show greater task diversity than "
            "top-rated courses. The reverse of all other methodologies."
        )
    return gap_str, pattern


def build_case4_figure(df):
    # Only include methodologies that are present in the (possibly filtered) df,
    # preserving the canonical display order.
    present = set(df["Teaching_Methodology"].unique())
    methods = [m for m in METHOD_ORDER if m in present]
    if not methods:
        return go.Figure()

    top_val, bot_val = {}, {}
    for m in methods:
        t = df[(df["Teaching_Methodology"] == m) & (df["Class"] == "TOP")]
        b = df[(df["Teaching_Methodology"] == m) & (df["Class"] == "BOTTOM")]
        top_val[m] = float(t["Shannon_Index"].iloc[0]) if len(t) > 0 else 0.0
        bot_val[m] = float(b["Shannon_Index"].iloc[0]) if len(b) > 0 else 0.0

    gaps = {m: top_val[m] - bot_val[m] for m in methods}

    top_custom, bot_custom = [], []
    for m in methods:
        gap_str, _ = _gap_info(gaps[m])
        top_custom.append([METHOD_FULL[m], "Top courses",    top_val[m], gap_str])
        bot_custom.append([METHOD_FULL[m], "Bottom courses", bot_val[m], gap_str])

    hovertemplate = (
        "<b>%{customdata[0]}</b><br>"
        "<b>Course group:</b> %{customdata[1]}<br>"
        "<b>Shannon Diversity Index:</b> %{customdata[2]:.3f}<br>"
        "<b>Gap (Top − Bottom):</b> %{customdata[3]}"
        "<extra></extra>"
    )

    top_bg     = ["#AFD0F1"] * len(methods)
    top_border = [COLOR_TOP]  * len(methods)
    bot_bg     = ["#F6D4B0" if m != "FLIP" else "#F6B4B0" for m in methods]
    bot_border = [COLOR_BOTTOM if m != "FLIP" else COLOR_ANOMALY for m in methods]

    # flip bottom bar gets the anomaly red colour since it inverts the pattern
    bot_colors = [COLOR_BOTTOM if m != "FLIP" else COLOR_ANOMALY for m in methods]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=methods,
        y=[top_val[m] - Y_BASE for m in methods],
        base=Y_BASE,
        name="Top courses",
        marker_color=COLOR_TOP,
        customdata=top_custom,
        hovertemplate=hovertemplate,
        hoverlabel=dict(
            bgcolor=top_bg,
            bordercolor=top_border,
            font=dict(color="#333", size=12, family="Arial"),
        ),
    ))

    fig.add_trace(go.Bar(
        x=methods,
        y=[bot_val[m] - Y_BASE for m in methods],
        base=Y_BASE,
        name="Bottom courses",
        marker_color=bot_colors,
        customdata=bot_custom,
        hovertemplate=hovertemplate,
        hoverlabel=dict(
            bgcolor=bot_bg,
            bordercolor=bot_border,
            font=dict(color="#333", size=12, family="Arial"),
        ),
    ))

    # annotation badge on the flip bottom bar to flag the anomaly
    if "FLIP" in methods:
        fig.add_annotation(
            x="FLIP",
            y=bot_val["FLIP"],
            xshift=14,
            text="<b>⚠ anomaly</b>",
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowcolor=COLOR_ANOMALY,
            ax=0,
            ay=-30,
            font=dict(size=10, color="white", family="Arial"),
            bgcolor=COLOR_ANOMALY,
            bordercolor=COLOR_ANOMALY,
            borderpad=4,
            borderwidth=0,
            xanchor="center",
            yanchor="bottom",
        )

    y_max = max(list(top_val.values()) + list(bot_val.values()))

    fig.update_layout(
        barmode="group",
        bargap=0.30,
        bargroupgap=0.06,
        height=420,
        margin={"t": 50, "b": 90, "l": 70, "r": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            title=dict(text="Course group"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=12, family="Arial"),
        ),
        hovermode="closest",
        font=dict(family="Arial", color="#444"),
    )


    fig.update_xaxes(
        tickmode="array",
        tickvals=methods,
        ticktext=[METHOD_TICK[m] for m in methods],
        showgrid=False,
        tickfont=dict(size=11),
        ticklabelstandoff=6,
    )

    # extra headroom above y_max to leave space for the anomaly badge
    fig.update_yaxes(
        title_text=(
            "Shannon Diversity Index<br>"
            "axis starts at 1.5 to show differences clearly"
        ),
        title_font=dict(size=11),
        range=[Y_BASE, y_max + 0.22],
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1,
        tickformat=".2f",
        tick0=Y_BASE,
        dtick=0.25,
    )
    return fig


def register_case4_callbacks(app, df):
    @app.callback(
        Output("case4-chart", "figure"),
        Input("active-case", "data"),
    )
    def update_case4_chart(active_case):
        # only recalculate when this tab is actually visible
        if active_case != "case4":
            return dash.no_update
        return build_case4_figure(df)
