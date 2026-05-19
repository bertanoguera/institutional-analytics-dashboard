import dash
from dash import Input, Output, State
import plotly.graph_objects as go


COURSE_COLORS = {
    "A": "#378ADD",
    "B": "#EF9F27",
    "C": "#1D9E75",
}

# maps the raw csv indicator name to a readable label with the original scale
INDICATOR_DISPLAY = {
    "Grades":                       "Grades (0-10)",
    "Workload":                     "Workload satisfaction (0-10)",
    "Subject":                      "Subject satisfaction (0-10)",
    "Methodology":                  "Methodology satisfaction (0-10)",
    "Course_Interaction_Frequency": "Course interaction frequency (0-31000)",
    "Daily_Access_Frequency":       "Daily access frequency (0-70)",
    "Course_Interaction_Span":      "Course interaction span (0-528 days)",
    "Unique_AR_Indexn":             "Unique A/R index (0-53)",
    "AR_Interaction_Span":          "A/R interaction span (0-50 days)",
    "AR_Interaction_Frequency":     "A/R interaction frequency (0-10)",
    "AR_First_Access_Interval":     "A/R first access interval (0-40 days)",
    "Instruction":                  "Instruction (0-150 hours)",
    "Preparation":                  "Preparation (0-100 hours)",
    "Consolidation":                "Consolidation (0-145 hours)",
    "Discovery":                    "Discovery (0-104 hours)",
    "Social Classroom":             "Social classroom (0-9 activities)",
    "Social Group":                 "Social group (0-17 activities)",
    "Social Individual":            "Social individual (0-12 activities)",
    "Modality Presential":          "Modality presential (0-15 activities)",
    "Modality Remote":              "Modality remote (0-13 activities)",
}

# convert normalised scores back to original units for the tooltip
INDICATOR_MAX = {
    "Grades":                       10,
    "Workload":                     10,
    "Subject":                      10,
    "Methodology":                  10,
    "Course_Interaction_Frequency": 31000,
    "Daily_Access_Frequency":       70,
    "Course_Interaction_Span":      528,
    "Unique_AR_Indexn":             53,
    "AR_Interaction_Span":          50,
    "AR_Interaction_Frequency":     10,
    "AR_First_Access_Interval":     40,
    "Instruction":                  150,
    "Preparation":                  100,
    "Consolidation":                145,
    "Discovery":                    104,
    "Social Classroom":             9,
    "Social Group":                 17,
    "Social Individual":            12,
    "Modality Presential":          15,
    "Modality Remote":              13,
}

INDICATOR_DESCRIPTION = {
    "Grades":                       "Final grade obtained by the student in the course.",
    "Workload":                     "Student satisfaction with the amount of work required by the course.",
    "Subject":                      "Student satisfaction with the subject content and its relevance.",
    "Methodology":                  "Student satisfaction with the teaching methodology used.",
    "Course_Interaction_Frequency": "Total number of interactions recorded with any LMS course element.",
    "Daily_Access_Frequency":       "Average number of daily sessions in which students accessed the LMS.",
    "Course_Interaction_Span":      "Number of days across which students interacted with course materials.",
    "Unique_AR_Indexn":             "Number of distinct learning resources or activities accessed at least once.",
    "AR_Interaction_Span":          "Number of days across which students accessed learning resources.",
    "AR_Interaction_Frequency":     "Average number of accesses per learning resource.",
    "AR_First_Access_Interval":     "Days elapsed between course start and the student's first resource access.",
    "Instruction":                  "Planned hours assigned to direct instruction activities (e.g. lectures, demonstrations).",
    "Preparation":                  "Planned hours assigned to preparation activities (e.g. readings, pre-class tasks).",
    "Consolidation":                "Planned hours assigned to consolidation activities (e.g. exercises, practice).",
    "Discovery":                    "Planned hours assigned to discovery or exploratory activities (e.g. projects, research).",
    "Social Classroom":             "Number of activities designed for whole-class social interaction.",
    "Social Group":                 "Number of activities designed for small-group collaboration.",
    "Social Individual":            "Number of activities designed for individual work.",
    "Modality Presential":          "Number of activities delivered in person (face-to-face).",
    "Modality Remote":              "Number of activities delivered remotely (online or hybrid).",
}

INDICATOR_UNIT = {
    "Grades":                       "/ 10",
    "Workload":                     "/ 10",
    "Subject":                      "/ 10",
    "Methodology":                  "/ 10",
    "Course_Interaction_Frequency": "interactions",
    "Daily_Access_Frequency":       "accesses / day",
    "Course_Interaction_Span":      "days",
    "Unique_AR_Indexn":             "index",
    "AR_Interaction_Span":          "days",
    "AR_Interaction_Frequency":     "times",
    "AR_First_Access_Interval":     "days",
    "Instruction":                  "hours",
    "Preparation":                  "hours",
    "Consolidation":                "hours",
    "Discovery":                    "hours",
    "Social Classroom":             "activities",
    "Social Group":                 "activities",
    "Social Individual":            "activities",
    "Modality Presential":          "activities",
    "Modality Remote":              "activities",
}

GROUP_INDICATORS = {
    "outcomes": [
        "Grades", "Workload", "Subject", "Methodology",
    ],
    "lms": [
        "Course_Interaction_Frequency", "Daily_Access_Frequency",
        "Course_Interaction_Span", "Unique_AR_Indexn",
        "AR_Interaction_Span", "AR_Interaction_Frequency",
        "AR_First_Access_Interval",
    ],
    "tasks": [
        "Instruction", "Preparation", "Consolidation", "Discovery",
    ],
    "social": [
        "Social Classroom", "Social Group", "Social Individual",
        "Modality Presential", "Modality Remote",
    ],
}

GROUP_NAMES = {
    "outcomes": "Student outcomes",
    "lms":      "LMS usage",
    "tasks":    "Task types",
    "social":   "Social & modality",
}

# shorter names used as axis labels (the full display name is too long)
GROUP_SHORT_NAMES = {
    "outcomes": [
        "Grades", "Workload satisfaction",
        "Subject satisfaction", "Methodology satisfaction",
    ],
    "lms": [
        "Course interaction frequency", "Daily access frequency",
        "Course interaction span", "Unique A/R index",
        "A/R interaction span", "A/R interaction frequency",
        "A/R first access interval",
    ],
    "tasks": ["Instruction", "Preparation", "Consolidation", "Discovery"],
    "social": [
        "Social classroom", "Social group", "Social individual",
        "Modality presential", "Modality remote",
    ],
}

TAB_HEIGHTS = {
    "outcomes": 400,
    "lms":      520,
    "tasks":    400,
    "social":   450,
}

INSIGHTS = {
    "outcomes": (
        "Course A performs above the institutional average on both grades and workload satisfaction, though "
        "it falls below average on methodology satisfaction. Course B stands out for notably high subject "
        "and methodology satisfaction. Course C consistently underperforms across all four indicators, with "
        "workload satisfaction particularly far below the average."
    ),
    "lms": (
        "Course A shows the broadest LMS engagement, leading on both interaction frequency and overall "
        "interaction span. Course B stands out for the highest daily access rate. Course C presents a "
        "contrasting profile: it makes diverse use of learning resources — reflected in a high unique A/R "
        "index — yet records the lowest daily access frequency and the shortest first access interval, "
        "suggesting more concentrated but less regular platform use."
    ),
    "tasks": (
        "Course A devotes a notably higher share of time to consolidation activities compared to the "
        "institutional average. Course B leads on both instruction and preparation hours but allocates "
        "considerably less time to consolidation. Course C falls below average across all four task types, "
        "with discovery activities particularly underrepresented."
    ),
    "social": (
        "Course A relies heavily on classroom-based social activities while making almost no use of group "
        "formats. Course C shows the opposite pattern: it favours group activities and individual work, "
        "with minimal classroom interaction and near-absent presential delivery. Course B has the most "
        "balanced profile, remaining close to the institutional average across all social and modality "
        "indicators."
    ),
}

_SEL_BTN = {
    "background": "#378ADD",
    "color": "white",
    "border": "1px solid #378ADD",
    "borderRadius": "8px",
    "padding": "10px 20px",
    "margin": "4px",
    "cursor": "pointer",
    "minWidth": "120px",
    "textAlign": "center",
}

_UNSEL_BTN = {
    "background": "white",
    "color": "#444",
    "border": "1px solid #ccc",
    "borderRadius": "8px",
    "padding": "10px 20px",
    "margin": "4px",
    "cursor": "pointer",
    "minWidth": "120px",
    "textAlign": "center",
}

_TAB_ACTIVE = {
    "color": "#378ADD",
    "borderBottom": "2px solid #378ADD",
    "fontWeight": "500",
    "background": "none",
    "borderTop": "none",
    "borderLeft": "none",
    "borderRight": "none",
    "padding": "8px 14px",
    "cursor": "pointer",
}

_TAB_INACTIVE = {
    "color": "#888",
    "borderBottom": "2px solid transparent",
    "background": "none",
    "borderTop": "none",
    "borderLeft": "none",
    "borderRight": "none",
    "padding": "8px 14px",
    "cursor": "pointer",
}

_TABS    = ["outcomes", "lms", "tasks", "social"]
_COURSES = ["A", "B", "C"]



def _fmt_original(score, ind):
    # reverse-normalise and format with unit label
    orig = score * INDICATOR_MAX[ind]
    unit = INDICATOR_UNIT[ind]
    if INDICATOR_MAX[ind] >= 100:
        return f"{round(orig)} {unit}"
    else:
        return f"{orig:.1f} {unit}"


def _build_figure(df, selected_courses, active_tab):
    indicators    = GROUP_INDICATORS[active_tab]
    display_names = [INDICATOR_DISPLAY[ind] for ind in indicators]
    short_names   = GROUP_SHORT_NAMES[active_tab]
    n             = len(indicators)

    avg_df  = df[df["Course"] == "AVG"]
    avg_val = {}
    for ind in indicators:
        row = avg_df[avg_df["Indicator"] == ind]
        avg_val[ind] = float(row["Score"].iloc[0]) if len(row) > 0 else 0.0

    # extend x left to make room for the label text (labels sit at x = -0.01)
    all_x = list(avg_val.values())
    for course in selected_courses:
        cdf = df[df["Course"] == course]
        for ind in indicators:
            row = cdf[cdf["Indicator"] == ind]
            if len(row) > 0:
                all_x.append(float(row["Score"].iloc[0]))
    x_max = (max(all_x) * 1.12) if all_x else 1.1
    x_min = -0.30

    fig = go.Figure()

    for course in selected_courses:
        course_df = df[df["Course"] == course]
        x_vals, custom = [], []
        for ind in indicators:
            row   = course_df[course_df["Indicator"] == ind]
            score = float(row["Score"].iloc[0]) if len(row) > 0 else 0.0
            delta = score - avg_val[ind]
            sign  = "+" if delta >= 0 else ""
            x_vals.append(score)
            custom.append([
                f"Course {course}",
                INDICATOR_DISPLAY[ind],
                f"{sign}{delta:.3f}",
                _fmt_original(score, ind),
                _fmt_original(avg_val[ind], ind),
            ])

        fig.add_trace(
            go.Bar(
                x=x_vals,
                y=display_names,
                orientation="h",
                name=f"Course {course}",
                marker_color=COURSE_COLORS[course],
                customdata=custom,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "<b>Indicator:</b> %{customdata[1]}<br>"
                    "<b>Normalized score:</b> %{x:.3f}<br>"
                    "<b>Original value:</b> %{customdata[3]}<br>"
                    "<b>vs. institutional avg:</b> %{customdata[2]} "
                    "(avg: %{customdata[4]})"
                    "<extra></extra>"
                ),
                hoverlabel=dict(
                    bgcolor=COURSE_COLORS[course],
                    bordercolor=COURSE_COLORS[course],
                    font=dict(color="white", size=12, family="Arial"),
                ),
            )
        )

    # institutional average shown as a vertical tick mark (line-ns marker)
    # size is calculated so it covers roughly half of each bar-group slot
    usable_px  = TAB_HEIGHTS[active_tab] - 120
    marker_px  = max(14, int((usable_px / n) * 0.50))

    avg_scores = [avg_val[ind] for ind in indicators]
    avg_custom = [
        [INDICATOR_DISPLAY[ind], f"{avg_val[ind]:.3f}", _fmt_original(avg_val[ind], ind)]
        for ind in indicators
    ]

    fig.add_trace(
        go.Scatter(
            x=avg_scores,
            y=display_names,
            mode="markers",
            marker=dict(
                symbol="line-ns",
                size=marker_px,
                color="rgba(0,0,0,0)",
                line=dict(color="#444", width=2.5),
            ),
            name="Institutional average",
            showlegend=True,
            customdata=avg_custom,
            hovertemplate=(
                "<b>Institutional average</b><br>"
                "<b>Indicator:</b> %{customdata[0]}<br>"
                "<b>Normalized score:</b> %{x:.3f}<br>"
                "<b>Original value:</b> %{customdata[2]}"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="#e8e8e8",
                bordercolor="#999",
                font=dict(color="#333", size=12, family="Arial"),
            ),
        )
    )

    # y-axis tick labels are hidden, instead we draw a text + markers trace
    # just to the left of x = 0 so that the label text is hoverable
    # this was the only way to attach a tooltip to the axis labels,
    # since plotly doesn't support tooltips on tick labels natively
    label_custom = [
        [short_names[i], INDICATOR_DESCRIPTION[indicators[i]]]
        for i in range(n)
    ]

    fig.add_trace(
        go.Scatter(
            x=[-0.01] * n,
            y=display_names,
            mode="text+markers",
            text=short_names,
            textposition="middle left",
            textfont=dict(size=11.5, color="#444", family="Arial"),
            marker=dict(symbol="square", size=18, opacity=0, color="rgba(0,0,0,0)"),
            showlegend=False,
            name="",
            customdata=label_custom,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="#f5f5f5",
                bordercolor="#aaaaaa",
                font=dict(color="#333", size=12, family="Arial"),
            ),
        )
    )

    category_array = list(reversed(display_names))

    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        height=TAB_HEIGHTS[active_tab],
        margin={"t": 60, "b": 60, "l": 8, "r": 20},
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            title=dict(text="Course"),
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
        title_text="Normalized score (0-1)",
        range=[x_min, x_max],
        tickvals=[0, 0.25, 0.50, 0.75, 1.00],
        ticktext=["0.00", "0.25", "0.50", "0.75", "1.00"],
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#bbb",
        zerolinewidth=1,
    )

    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        categoryorder="array",
        categoryarray=category_array,
        automargin=False,
    )
    return fig


def register_case3_callbacks(app, df):

    @app.callback(
        Output("case3-selected-courses", "data"),
        [
            Input("case3-btn-A", "n_clicks"),
            Input("case3-btn-B", "n_clicks"),
            Input("case3-btn-C", "n_clicks"),
        ],
        State("case3-selected-courses", "data"),
        prevent_initial_call=True,
    )
    def update_selected_courses(_a, _b, _c, current):
        current = list(current) if current else ["A", "B"]
        ctx = dash.callback_context
        if not ctx.triggered:
            return current
        course = ctx.triggered[0]["prop_id"].split(".")[0].replace("case3-btn-", "")
        # max 2 courses selected at a time
        if course in current:
            if len(current) > 1:
                current.remove(course)
        else:
            if len(current) < 2:
                current.append(course)
        return current

    @app.callback(
        [Output(f"case3-btn-{c}", "style") for c in _COURSES],
        Input("case3-selected-courses", "data"),
    )
    def update_btn_styles(selected):
        selected = selected or ["A", "B"]
        return [_SEL_BTN if c in selected else _UNSEL_BTN for c in _COURSES]

    @app.callback(
        Output("case3-active-tab", "data"),
        [Input(f"case3-tab-{t}", "n_clicks") for t in _TABS],
        prevent_initial_call=True,
    )
    def update_active_tab(*_):
        ctx = dash.callback_context
        if not ctx.triggered:
            return "outcomes"
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        return {f"case3-tab-{t}": t for t in _TABS}.get(btn_id, "outcomes")

    @app.callback(
        [Output(f"case3-tab-{t}", "style") for t in _TABS],
        Input("case3-active-tab", "data"),
    )
    def update_tab_styles(active):
        active = active or "outcomes"
        return [_TAB_ACTIVE if t == active else _TAB_INACTIVE for t in _TABS]

    @app.callback(
        Output("case3-variable-list", "children"),
        Input("case3-active-tab", "data"),
    )
    def update_variable_list(active):
        active = active or "outcomes"
        names  = GROUP_SHORT_NAMES[active]
        group  = GROUP_NAMES[active]
        return (
            f"Showing: {group} ({len(names)} variables) — {', '.join(names)}. "
            "Hover over a variable name on the axis to read its definition."
        )

    @app.callback(
        Output("case3-bar-chart", "figure"),
        [
            Input("case3-selected-courses", "data"),
            Input("case3-active-tab", "data"),
        ],
    )
    def update_chart(selected_courses, active_tab):
        selected_courses = selected_courses or ["A"]
        active_tab       = active_tab or "outcomes"
        return _build_figure(df, selected_courses, active_tab)

    @app.callback(
        Output("case3-insight-text", "children"),
        Input("case3-active-tab", "data"),
    )
    def update_insight(active):
        return INSIGHTS.get(active or "outcomes", "")
