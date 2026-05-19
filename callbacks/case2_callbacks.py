import dash
from dash import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

METHOD_LABELS = {
    "LECT": "Lectures",
    "PJBL": "Project-based learning",
    "FLIP": "Flipped classroom",
    "PRBL": "Problem-based learning",
    "CASE": "Case studies"
}

# tooltip colors match the grade band so user gets a visual cue
GRADE_TOOLTIP_COLORS = {
    "Fail":      {"bg": "#F6B4B0", "border": "#E8443A"},
    "Pass":      {"bg": "#F6D4B0", "border": "#E8943A"},
    "Notable":   {"bg": "#AFD0F1", "border": "#378ADD"},
    "Excellent": {"bg": "#A5D8C8", "border": "#1D9E75"},
}


def grade_band(score):
    if score < 0.38:
        return "Fail"
    if score < 0.46:
        return "Pass"
    if score < 0.54:
        return "Notable"
    return "Excellent"


def build_case2_main_figure(df):
    grouped = df.groupby(["Teaching_Methodology", "Class"], as_index=False)["Weighted_Performance"].median()

    # sort methodologies by top-course performance descending
    top_order = grouped[grouped["Class"] == "TOP"][["Teaching_Methodology", "Weighted_Performance"]].sort_values("Weighted_Performance", ascending=False)
    methodologies = [m for m in top_order["Teaching_Methodology"].tolist()]
    for method in METHOD_LABELS:
        if method not in methodologies and method in grouped["Teaching_Methodology"].values:
            methodologies.append(method)

    y_labels = methodologies

    def median_for(method, class_label):
        match = grouped[(grouped["Teaching_Methodology"] == method) & (grouped["Class"] == class_label)]
        return float(match["Weighted_Performance"].iloc[0]) if len(match) > 0 else 0.0

    top_values    = [median_for(method, "TOP")    for method in methodologies]
    bottom_values = [median_for(method, "BOTTOM") for method in methodologies]

    top_custom    = [[METHOD_LABELS.get(method, method), "Top courses",    grade_band(val)] for method, val in zip(methodologies, top_values)]
    bottom_custom = [[METHOD_LABELS.get(method, method), "Bottom courses", grade_band(val)] for method, val in zip(methodologies, bottom_values)]

    top_bg     = [GRADE_TOOLTIP_COLORS[grade_band(v)]["bg"]     for v in top_values]
    top_border = [GRADE_TOOLTIP_COLORS[grade_band(v)]["border"] for v in top_values]
    bot_bg     = [GRADE_TOOLTIP_COLORS[grade_band(v)]["bg"]     for v in bottom_values]
    bot_border = [GRADE_TOOLTIP_COLORS[grade_band(v)]["border"] for v in bottom_values]

    fig = go.Figure()

    # bottom trace added first so top courses appear above in each group
    fig.add_trace(
        go.Bar(
            x=bottom_values,
            y=y_labels,
            orientation="h",
            name="Bottom courses",
            marker_color="#EF9F27",
            customdata=bottom_custom,
            hovertemplate="<b>%{customdata[0]}</b><br><b>Course group:</b> %{customdata[1]}<br><b>Median performance:</b> %{x:.3f}<br><b>Grade:</b> %{customdata[2]}<extra></extra>",
            hoverlabel=dict(
                bgcolor=bot_bg,
                bordercolor=bot_border,
                font=dict(color="#333333", size=12, family="Arial"),
            )
        )
    )
    fig.add_trace(
        go.Bar(
            x=top_values,
            y=y_labels,
            orientation="h",
            name="Top courses",
            marker_color="#378ADD",
            customdata=top_custom,
            hovertemplate="<b>%{customdata[0]}</b><br><b>Course group:</b> %{customdata[1]}<br><b>Median performance:</b> %{x:.3f}<br><b>Grade:</b> %{customdata[2]}<extra></extra>",
            hoverlabel=dict(
                bgcolor=top_bg,
                bordercolor=top_border,
                font=dict(color="#333333", size=12, family="Arial"),
            )
        )
    )

    fig.update_layout(
        barmode="group",
        height=380,
        margin={"t": 20, "b": 60, "l": 130, "r": 40},
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            title=dict(text="Course group"),
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0)"
        ),
        hovermode="closest",
    )
    # axis starts at 0.25 to emphasize the differences between groups
    fig.update_xaxes(
        title_text="Weighted performance score (axis starts at 0.25 to show differences clearly)",
        range=[0.25, 0.62],
        tickformat=".2f",
        tick0=0.25,
        dtick=0.05,
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=y_labels,
        automargin=True,
        ticklabelstandoff=6,
    )

    return fig


def build_case2_gap_figure(df):
    grouped = df.groupby(["Teaching_Methodology", "Class"], as_index=False)["Weighted_Performance"].median()
    pivot = grouped.pivot(index="Teaching_Methodology", columns="Class", values="Weighted_Performance").reset_index()
    pivot["TOP"]    = pivot["TOP"].fillna(0.0)
    pivot["BOTTOM"] = pivot["BOTTOM"].fillna(0.0)
    pivot["Gap"]    = pivot["TOP"] - pivot["BOTTOM"]
    pivot = pivot.sort_values("Gap", ascending=True)

    y_labels   = pivot["Teaching_Methodology"].tolist()
    gap_values = pivot["Gap"].tolist()
    gap_custom = [[METHOD_LABELS.get(m, m)] for m in y_labels]

    gap_min = min(gap_values)
    gap_max = max(gap_values)
    padding = (gap_max - gap_min) * 0.18
    x_range = [max(0, gap_min - padding), gap_max + padding]

    fig = go.Figure(
        go.Bar(
            x=gap_values,
            y=y_labels,
            orientation="h",
            marker_color="#A0A0A0",
            customdata=gap_custom,
            hovertemplate="<b>%{customdata[0]}</b><br><b>Performance gap (Top − Bottom):</b> %{x:.3f}<extra></extra>",
            hoverlabel=dict(
                bgcolor="#F0F0F0",
                bordercolor="#A0A0A0",
                font=dict(color="#333333", size=12, family="Arial"),
            )
        )
    )

    fig.update_layout(
        height=280,
        margin={"t": 20, "b": 40, "l": 130, "r": 30},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            title_text="Performance gap (Top − Bottom) - axis scaled to highlight differences",
            tickformat=".3f",
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            range=x_range,
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=y_labels,
            automargin=True,
            ticklabelstandoff=6,
        ),
        hovermode="closest",
    )

    return fig


def register_case2_callbacks(app, df):
    @app.callback(
        Output("case2-bar-chart", "figure"),
        Input("active-case", "data")
    )
    def update_case2_bar_chart(active_case):
        if active_case != "case2":
            return dash.no_update
        return build_case2_main_figure(df)

    @app.callback(
        [
            Output("case2-detail-div", "style"),
            Output("case2-expand-btn", "children")
        ],
        Input("case2-expand-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_case2_gap_section(n_clicks):
        if n_clicks is None or n_clicks % 2 == 0:
            return {"display": "none"}, "▸ View performance gap (for advanced users)"
        return {"display": "block"}, "▾ Hide performance gap"

    @app.callback(
        Output("case2-gap-chart", "figure"),
        Input("active-case", "data")
    )
    def update_case2_gap_chart(active_case):
        if active_case != "case2":
            return dash.no_update
        return build_case2_gap_figure(df)
