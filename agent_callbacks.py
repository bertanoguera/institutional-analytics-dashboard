import time
from collections import Counter, defaultdict
import dash
from dash import Input, Output, State, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from callbacks.case2_callbacks import build_case2_main_figure, build_case2_gap_figure
from callbacks.case4_callbacks import build_case4_figure
from agent.classifier import classify
from agent.filter import apply_filters
from agent.explain import explain
from agent.tracing import trace_query, log_to_run


def _build_case2_gap_figure_safe(df):
    """Wraps build_case2_gap_figure and fixes the x-axis range when only one
    methodology is present.  The original function computes padding as
    (gap_max − gap_min) * 0.18, which collapses to 0 for a single value and
    produces a zero-width or reversed range — causing Plotly to swap / mangle
    the axis."""
    fig = build_case2_gap_figure(df)
    n_methods = df["Teaching_Methodology"].nunique()
    if n_methods == 1 and fig.data:
        x_vals = [v for trace in fig.data for v in (list(trace.x) if trace.x is not None else [])]
        if x_vals:
            mid = sum(x_vals) / len(x_vals)
            fig.update_xaxes(range=[max(0, mid - 0.015), mid + 0.015])
    return fig


_FACULTY_ORDER = ["Economics", "Engineering", "Law", "Humanities", "Translation"]
_COLORS        = {"Female": "#378ADD", "Male": "#EF9F27"}
_HOVER_BG      = {"Female": "#AFD0F1", "Male": "#F6D4B0"}

_LAYOUT_COMMON = dict(
    barmode="group",
    bargap=0.18,
    bargroupgap=0.12,
    hovermode="closest",
    height=520,
    margin={"t": 80, "b": 85, "l": 70, "r": 20},

    legend=dict(
        title="Professor gender",
        orientation="h",
        yanchor="bottom",
        y=1.12,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0)",
    ),
)

_PLACEHOLDER = (
    "Ask about the data or filter it by any dimension — "
    "e.g. 'What does the satisfaction score measure?' or "
    "'Show me only Engineering and Law'. "
    "Use Reset filters to restore the full dataset."
)

# maps every case 3 indicator to the group it belongs to (used for validation).
_C3_INDICATOR_GROUP = {
    "Grades": "outcomes", "Workload": "outcomes",
    "Subject": "outcomes", "Methodology": "outcomes",
    "Course_Interaction_Frequency": "lms", "Daily_Access_Frequency": "lms",
    "Course_Interaction_Span": "lms", "Unique_AR_Indexn": "lms",
    "AR_Interaction_Span": "lms", "AR_Interaction_Frequency": "lms",
    "AR_First_Access_Interval": "lms",
    "Instruction": "tasks", "Preparation": "tasks",
    "Consolidation": "tasks", "Discovery": "tasks",
    "Social Classroom": "social", "Social Group": "social",
    "Social Individual": "social", "Modality Presential": "social",
    "Modality Remote": "social",
}

_C3_GROUP_LABELS = {
    "outcomes": "Student Outcomes",
    "lms":      "LMS Usage",
    "tasks":    "Task Types",
    "social":   "Social & Modality",
}

_RESET_BTN_ACTIVE = {
    "background": "#EEF5FE",
    "border": "1.5px solid #378ADD",
    "borderRadius": "20px",
    "color": "#185FA5",
    "fontSize": "12px",
    "fontWeight": "600",
    "cursor": "pointer",
    "whiteSpace": "nowrap",
    "fontFamily": "Arial, sans-serif",
    "padding": "5px 13px",
}

_RESET_BTN_INACTIVE = {
    "background": "transparent",
    "border": "1px solid #e0e0e0",
    "borderRadius": "20px",
    "color": "#ccc",
    "fontSize": "12px",
    "fontWeight": "500",
    "cursor": "not-allowed",
    "whiteSpace": "nowrap",
    "fontFamily": "Arial, sans-serif",
    "padding": "5px 13px",
}


# case 1 figure builder (mirrors case1_callbacks.py:update_bar_chart)
def _build_case1_figure(df: pd.DataFrame) -> go.Figure:
    selected_faculties = [f for f in _FACULTY_ORDER if f in df["Faculty"].values]

    if not selected_faculties:
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected filters.")
        return fig
    aggregations = []
    for faculty in selected_faculties:
        fdf = df[df["Faculty"] == faculty]
        for prof_gender in ["Female", "Male"]:
            pgdf = fdf[fdf["Professor_Gender"] == prof_gender]
            for stud_gender in ["Female", "Male"]:
                sub = pgdf[pgdf["Student_Gender"] == stud_gender]
                if len(sub) > 0:
                    scores    = sub["Satisfaction_Score"]
                    prof_meds = sub.groupby("Professor_ID")["Satisfaction_Score"].median()
                    aggregations.append({
                        "Faculty":          faculty,
                        "Professor_Gender": prof_gender,
                        "Student_Gender":   stud_gender,
                        "Median":           scores.median(),
                        "Count_Professors": len(prof_meds),
                    })

    agg_df = pd.DataFrame(aggregations)
    if agg_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected filters.")
        return fig

    def _hover(row):
        return (
            f"<b>Professor gender:</b> {row['Professor_Gender']}<br>"
            f"<b>Student gender:</b> {row['Student_Gender']}<br>"
            f"<b>Faculty:</b> {row['Faculty']}<br>"
            f"<b>Median:</b> {row['Median']:.2f}<br>"
            f"<b>Professors:</b> {int(row['Count_Professors'])}"
        )

    if len(selected_faculties) > 1:
        fig = make_subplots(
            rows=1, cols=len(selected_faculties),
            shared_yaxes=True, horizontal_spacing=0.08,
            subplot_titles=selected_faculties,
        )
        for col_idx, faculty in enumerate(selected_faculties, 1):
            fac_agg = agg_df[agg_df["Faculty"] == faculty]
            for prof_gender in ["Female", "Male"]:
                pdata = fac_agg[fac_agg["Professor_Gender"] == prof_gender]
                fig.add_trace(
                    go.Bar(
                        x=pdata["Student_Gender"].tolist(),
                        y=pdata["Median"].tolist(),
                        name=prof_gender,
                        offsetgroup=prof_gender,
                        width=0.35,
                        marker=dict(color=_COLORS[prof_gender], line=dict(width=1, color="#ffffff")),
                        hovertext=[_hover(r) for _, r in pdata.iterrows()],
                        hovertemplate="%{hovertext}<extra></extra>",
                        hoverlabel=dict(
                            bgcolor=_HOVER_BG[prof_gender],
                            bordercolor=_COLORS[prof_gender],
                            font=dict(color="#333", size=12, family="Arial"),
                        ),
                        showlegend=(col_idx == 1),
                        legendgroup=prof_gender,
                    ),
                    row=1, col=col_idx,
                )
        fig.update_yaxes(
            range=[0, 10], title_text="Student satisfaction score (0-10)",
            row=1, col=1, tick0=0, dtick=1,
            showgrid=True, gridcolor="lightgray", gridwidth=1,
        )
        for col_idx in range(2, len(selected_faculties) + 1):
            fig.update_yaxes(
                range=[0, 10], row=1, col=col_idx,
                tick0=0, dtick=1, showgrid=True, gridcolor="lightgray", gridwidth=1,
            )
        for col_idx in range(1, len(selected_faculties) + 1):
            fig.update_xaxes(
                row=1, col=col_idx, title_text="",
                categoryorder="array", categoryarray=["Female", "Male"],
                tickmode="array", tickvals=["Female", "Male"],
                ticktext=["Female<br>students", "Male<br>students"],
                showgrid=False,
            )
        fig.update_layout(**_LAYOUT_COMMON)

    else:
        fig = go.Figure()
        for prof_gender in ["Female", "Male"]:
            pdata = agg_df[agg_df["Professor_Gender"] == prof_gender]
            fig.add_trace(
                go.Bar(
                    x=pdata["Student_Gender"].tolist(),
                    y=pdata["Median"].tolist(),
                    name=prof_gender,
                    offsetgroup=prof_gender,
                    width=0.35,
                    marker=dict(color=_COLORS[prof_gender], line=dict(width=1, color="#ffffff")),
                    hovertext=[_hover(r) for _, r in pdata.iterrows()],
                    hovertemplate="%{hovertext}<extra></extra>",
                    hoverlabel=dict(
                        bgcolor=_HOVER_BG[prof_gender],
                        bordercolor=_COLORS[prof_gender],
                        font=dict(color="#333", size=12, family="Arial"),
                    ),
                )
            )
        fig.update_xaxes(
            categoryorder="array", categoryarray=["Female", "Male"],
            tickmode="array", tickvals=["Female", "Male"],
            ticktext=["Female<br>students", "Male<br>students"],
            showgrid=False,
        )
        fig.update_yaxes(
            title_text="Student satisfaction score (0-10)",
            range=[0, 10], tick0=0, dtick=1,
            showgrid=True, gridwidth=1, gridcolor="lightgray",
        )
        fig.update_layout(**_LAYOUT_COMMON)

    return fig


# case 1 dot-plot builder (mirrors case1_callbacks.py:update_dot_plot)         #

def _jitter_x(y_vals: list, center: float, step: float = 0.10) -> list:
    counts   = Counter(y_vals)
    idx_seen = defaultdict(int)
    x_pos    = []
    for y in y_vals:
        n = counts[y]
        i = idx_seen[y]
        x_pos.append(center if n == 1 else center + (i - (n - 1) / 2.0) * step)
        idx_seen[y] += 1
    return x_pos

def _build_case1_dot_figure(df: pd.DataFrame) -> go.Figure:
    selected_faculties = [f for f in _FACULTY_ORDER if f in df["Faculty"].values]
    if not selected_faculties:
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected filters.")
        return fig
    fig = make_subplots(
        rows=1, cols=len(selected_faculties),
        subplot_titles=selected_faculties,
        shared_yaxes=True,
        horizontal_spacing=0.10,
    )

    x_center = {"Female": 0, "Male": 1}

    # determine which student gender to use as the "first" for legend anchoring
    present_stud_genders = [g for g in ["Female", "Male"] if g in df["Student_Gender"].values]
    first_stud_gender    = present_stud_genders[0] if present_stud_genders else "Female"

    for col_idx, faculty in enumerate(selected_faculties, 1):
        faculty_df = df[df["Faculty"] == faculty]

        for stud_gender in ["Female", "Male"]:
            xc  = x_center[stud_gender]
            sub = faculty_df[faculty_df["Student_Gender"] == stud_gender]
            if len(sub) == 0:
                continue
            grouped = (
                sub.groupby(["Professor_ID", "Professor_Gender"], as_index=False)
                ["Satisfaction_Score"].median()
            )
            if len(grouped) == 0:
                continue
            grouped = grouped.sort_values("Satisfaction_Score").reset_index(drop=True)
            grouped["x_jitter"] = _jitter_x(
                grouped["Satisfaction_Score"].tolist(), center=xc, step=0.10
            )

            scores      = grouped["Satisfaction_Score"]
            total_prof  = grouped["Professor_ID"].nunique()
            median_val  = scores.median()
            q1          = scores.quantile(0.25)
            q3          = scores.quantile(0.75)
            min_val     = scores.min()
            max_val     = scores.max()
            iqr         = float(q3 - q1)
            lower_fence = float(q1 - 1.5 * iqr)
            upper_fence = float(q3 + 1.5 * iqr)
            scores_inliers = scores[(scores >= lower_fence) & (scores <= upper_fence)]
            fig.add_trace(
                go.Box(
                    y=scores_inliers,
                    x=[xc] * len(scores_inliers),
                    name=stud_gender,
                    boxpoints=False,
                    width=0.32,
                    fillcolor="rgba(220,220,220,0.45)",
                    line=dict(color="#8c8c8c", width=1.6),
                    whiskerwidth=0.7,
                    marker=dict(color="#8c8c8c"),
                    hoverinfo="none",
                    showlegend=False,
                ),
                row=1, col=col_idx,
            )

            for prof_gender in ["Female", "Male"]:
                dots = grouped[grouped["Professor_Gender"] == prof_gender]
                if len(dots) == 0:
                    continue

                symbols, per_dot_hover = [], []
                for _, row in dots.iterrows():
                    v      = row["Satisfaction_Score"]
                    is_out = v < lower_fence or v > upper_fence
                    symbols.append("diamond" if is_out else "circle")
                    label  = "<b>Outlier</b><br>" if is_out else ""
                    per_dot_hover.append(
                        f"{label}"
                        f"<b>Professor gender:</b> {prof_gender}<br>"
                        f"<b>Student gender:</b> {stud_gender}<br>"
                        f"<b>Faculty:</b> {faculty}<br>"
                        f"<b>Score:</b> {v:.2f}<br>"
                        f"<b>Total professors:</b> {total_prof}<br>"
                        f"<b>Group median:</b> {median_val:.2f}<br>"
                        f"<b>Q1-Q3:</b> {q1:.2f} - {q3:.2f}<br>"
                        f"<b>Range:</b> {min_val:.2f} - {max_val:.2f}"
                    )

                fig.add_trace(
                    go.Scatter(
                        x=dots["x_jitter"].tolist(),
                        y=dots["Satisfaction_Score"].tolist(),
                        mode="markers",
                        name=f"{prof_gender} professor",
                        legendgroup=prof_gender,
                        showlegend=(col_idx == 1 and stud_gender == first_stud_gender),
                        marker=dict(
                            size=8,
                            color=_COLORS[prof_gender],
                            opacity=0.82,
                            symbol=symbols,
                            line=dict(width=0.5, color="white"),
                        ),
                        hovertext=per_dot_hover,
                        hovertemplate="%{hovertext}<extra></extra>",
                        hoverlabel=dict(
                            bgcolor=_HOVER_BG[prof_gender],
                            bordercolor=_COLORS[prof_gender],
                            font=dict(color="#333", size=12, family="Arial"),
                        ),
                    ),
                    row=1, col=col_idx,
                )

    for col_idx in range(1, len(selected_faculties) + 1):
        fig.update_xaxes(
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["Female<br>students", "Male<br>students"],
            range=[-0.45, 1.45],
            showgrid=False,
            title_text="",
            row=1, col=col_idx,
        )
        fig.update_yaxes(
            autorange=True,
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            title_text="Student satisfaction score (0-10)" if col_idx == 1 else "",
            row=1, col=col_idx,
        )

    fig.update_layout(
        height=560,
        hovermode="closest",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"t": 110, "b": 80, "l": 65, "r": 20},
        font=dict(family="Arial", color="#444"),
        legend=dict(
            title="Professor gender",
            orientation="h",
            yanchor="bottom",
            y=1.10,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(font_size=12, font_family="Arial"),
    )

    return fig


# chat history rendering                                                        #
def _render_history(history: list) -> html.Div:
    """Convert a list of message dicts into styled chat bubbles."""
    if not history:
        return html.Div(
            _PLACEHOLDER,
            style={"fontSize": "13px", "color": "#aaa", "lineHeight": "1.6", "fontStyle": "italic"},
        )

    items = []
    for msg in history:
        if msg["role"] == "user":
            items.append(
                html.Div(
                    msg["text"],
                    style={
                        "alignSelf": "flex-end",
                        "background": "#EFEFEF",
                        "borderRadius": "12px 12px 2px 12px",
                        "padding": "8px 12px",
                        "fontSize": "13px",
                        "color": "#333",
                        "maxWidth": "85%",
                        "lineHeight": "1.5",
                        "wordBreak": "break-word",
                    },
                )
            )
        elif msg["intent"] == "thinking":
            items.append(
                html.Div(
                    "· · ·",
                    style={
                        "alignSelf": "flex-start",
                        "background": "#f0f0f0",
                        "borderRadius": "12px",
                        "padding": "10px 18px",
                        "fontSize": "20px",
                        "color": "#aaa",
                        "letterSpacing": "4px",
                        "lineHeight": "1",
                    },
                )
            )
        elif msg["intent"] == "filter":
            items.append(
                html.Div(
                    msg["text"],
                    style={
                        "alignSelf": "flex-start",
                        "background": "#E6F1FB",
                        "borderLeft": "3px solid #378ADD",
                        "borderRadius": "0 6px 6px 0",
                        "padding": "9px 13px",
                        "fontSize": "13px",
                        "color": "#0C447C",
                        "maxWidth": "95%",
                        "lineHeight": "1.6",
                    },
                )
            )
        else:  # explain
            items.append(
                html.Div(
                    msg["text"],
                    style={
                        "alignSelf": "flex-start",
                        "background": "white",
                        "border": "1px solid #e0e0e0",
                        "borderRadius": "0 8px 8px 8px",
                        "padding": "10px 13px",
                        "fontSize": "13px",
                        "color": "#333",
                        "maxWidth": "95%",
                        "lineHeight": "1.6",
                    },
                )
            )

    return html.Div(
        items,
        style={"display": "flex", "flexDirection": "column", "gap": "8px"},
    )


def _filter_summary(params: dict, case_id: str) -> str:
    parts = []
    if case_id == "case1":
        if "faculty" in params:
            facs = params["faculty"]
            if isinstance(facs, str):
                facs = [facs]
            parts.append(", ".join(facs))
        if "student_gender" in params:
            parts.append(f"{params['student_gender'].lower()} students")
        if "professor_gender" in params:
            parts.append(f"{params['professor_gender'].lower()} professors")
    elif case_id in ("case2", "case4"):
        if "teaching_methodology" in params:
            methods = params["teaching_methodology"]
            if isinstance(methods, str):
                methods = [methods]
            parts.append(", ".join(methods))
    elif case_id == "case3":
        if "course" in params:
            courses = params["course"]
            if isinstance(courses, str):
                courses = [courses]
            label = "courses" if len(courses) > 1 else "course"
            parts.append(f"{label} {', '.join(courses)}")
        if "variable_group" in params:
            parts.append(params["variable_group"])
        if "indicator" in params:
            inds = params["indicator"]
            if isinstance(inds, str):
                inds = [inds]
            parts.append(f"indicators: {', '.join(inds)}")
        if "hide_indicator" in params:
            inds = params["hide_indicator"]
            if isinstance(inds, str):
                inds = [inds]
            parts.append(f"hiding: {', '.join(inds)}")
    return ("Showing " + ", ".join(parts) + ".") if parts else "Filter applied."


# history / data helper functions
_RESET_PHRASES = [
    "reset", "clear filter", "show all", "all data",
    "original data", "show original", "see original",
    "remove all filter", "no filter", "undo filter",
    "full data", "unfilter", "remove filter",
]

def _is_reset_query(query: str) -> bool:
    """Return True when the user is explicitly asking to clear all filters."""
    q = query.lower()
    return any(phrase in q for phrase in _RESET_PHRASES)


def _recent_messages(history: list, n: int = 8) -> list:
    """Return the last n non-empty, non-thinking messages for LLM context."""
    msgs = [
        m for m in history
        if m.get("intent") != "thinking" and m.get("text", "").strip()
    ]
    return msgs[-n:]


def _merge_params(current: dict, new: dict, case_id: str) -> dict:
    """Merge new filter params onto the currently active params.
    Rules:
    - New values override old values for the same dimension.
    - Dimensions absent from `new` keep their old values (accumulation).
    - Case 3: changing variable_group clears any indicator / hide_indicator
      filter (indicators belong to a specific group — switching group resets
      them to 'show all').
    - indicator and hide_indicator are mutually exclusive: setting one clears
      the other.
    """
    merged = {**current, **new}

    if case_id == "case3" and "variable_group" in new:
        merged.pop("indicator", None)
        merged.pop("hide_indicator", None)

    if "indicator" in new:
        merged.pop("hide_indicator", None)
    elif "hide_indicator" in new:
        merged.pop("indicator", None)

    return merged


def _compute_data_summary(case_id: str, df: pd.DataFrame) -> str:
    """Build a compact plain-text summary of the key data values for a case."""
    if case_id == "case1":
        lines = ["DATA VALUES — median satisfaction score (0–10) per group:"]
        faculties = [f for f in ["Economics", "Engineering", "Law", "Humanities", "Translation"]
                     if f in df["Faculty"].values]
        for fac in faculties:
            fdf = df[df["Faculty"] == fac]
            parts = []
            for pg in ["Female", "Male"]:
                for sg in ["Female", "Male"]:
                    sub = fdf[(fdf["Professor_Gender"] == pg) & (fdf["Student_Gender"] == sg)]
                    if len(sub):
                        parts.append(
                            f"Prof {pg}/Student {sg}: {sub['Satisfaction_Score'].median():.2f}"
                        )
            if parts:
                lines.append(f"  {fac}: " + " | ".join(parts))
        return "\n".join(lines)

    if case_id == "case2":
        method_full = {
            "LECT": "Lectures", "PJBL": "Project-Based Learning",
            "PRBL": "Problem-Based Learning", "FLIP": "Flipped Classroom",
            "CASE": "Case Studies",
        }
        lines = ["DATA VALUES — mean weighted performance (0–1) by methodology and workload group:"]
        for m in ["LECT", "PJBL", "PRBL", "FLIP", "CASE"]:
            mdf = df[df["Teaching_Methodology"] == m]
            top_s = mdf[mdf["Class"] == "TOP"]["Weighted_Performance"]
            bot_s = mdf[mdf["Class"] == "BOTTOM"]["Weighted_Performance"]
            if len(top_s) and len(bot_s):
                t, b = top_s.mean(), bot_s.mean()
                lines.append(
                    f"  {method_full[m]} ({m}): "
                    f"TOP={t:.3f}, BOTTOM={b:.3f}, gap={t - b:+.3f}"
                )
        return "\n".join(lines)

    if case_id == "case3":
        lines = ["DATA VALUES — normalised scores (0–1) per course and indicator:"]
        for course in ["A", "B", "C", "AVG"]:
            cdf = df[df["Course"] == course]
            if cdf.empty:
                continue
            label = "Institutional average (AVG)" if course == "AVG" else f"Course {course}"
            parts = [f"{r['Indicator']}={r['Score']:.3f}" for _, r in cdf.iterrows()]
            lines.append(f"  {label}: " + ", ".join(parts))
        return "\n".join(lines)

    if case_id == "case4":
        method_full = {
            "LECT": "Lectures", "PJBL": "Project-Based Learning",
            "PRBL": "Problem-Based Learning", "FLIP": "Flipped Classroom",
            "CASE": "Case Studies",
        }
        lines = ["DATA VALUES — Shannon Diversity Index by methodology and workload group:"]
        for m in ["LECT", "PJBL", "PRBL", "FLIP", "CASE"]:
            mdf = df[df["Teaching_Methodology"] == m]
            top_s = mdf[mdf["Class"] == "TOP"]["Shannon_Index"]
            bot_s = mdf[mdf["Class"] == "BOTTOM"]["Shannon_Index"]
            if len(top_s) and len(bot_s):
                t, b = float(top_s.iloc[0]), float(bot_s.iloc[0])
                lines.append(
                    f"  {method_full[m]} ({m}): "
                    f"TOP={t:.3f}, BOTTOM={b:.3f}, gap={t - b:+.3f}"
                )
        return "\n".join(lines)

    return ""


# callback registration
def register_agent_callbacks(app, dfs: dict):

    # precompute data summaries once at startup so explain() has real numbers
    _data_summaries = {cid: _compute_data_summary(cid, dfs[cid]) for cid in dfs}

    # render callback: single writer for agent-response-output
    # fires whenever the history store changes (new message added, or cleared on tab switch).

    @app.callback(
        Output("agent-response-output", "children"),
        Input("agent-chat-history", "data"),
    )
    def render_chat_history(history):
        return _render_history(history or [])

    @app.callback(
        [
            Output("agent-reset-btn", "style"),
            Output("agent-reset-btn", "disabled"),
        ],
        Input("agent-filter-active", "data"),
    )
    def update_reset_button(is_active):
        if is_active:
            return _RESET_BTN_ACTIVE, False
        return _RESET_BTN_INACTIVE, True

    # render user message + thinking dots
    # fires immediately on Send, no AI call here

    @app.callback(
        [
            Output("agent-chat-history",  "data",  allow_duplicate=True),
            Output("agent-query-input",   "value"),
            Output("agent-pending-query", "data"),
        ],
        Input("agent-submit-btn", "n_clicks"),
        [
            State("agent-query-input",   "value"),
            State("active-case",         "data"),
            State("agent-chat-history",  "data"),
        ],
        prevent_initial_call=True,
    )
    def submit_query(n_clicks, query, active_case, history):
        nu = dash.no_update
        if not query or not query.strip():
            return nu, nu, nu

        active_case = active_case or "case1"
        history     = list(history or [])
        query       = query.strip()

        history.append({"role": "user",      "text": query})
        history.append({"role": "assistant", "intent": "thinking", "text": ""})

        return history, "", {"query": query, "active_case": active_case, "ts": time.time()}

    # AI call to classify + filter/explain 
    # triggered by the pending-query store, replaces the thinking dots
    # current filter stores are read as state so new params can be merged onto the existing active filters (history-aware accumulation)

    @app.callback(
        [
            Output("agent-chat-history",  "data",  allow_duplicate=True),
            Output("agent-case1-filter",  "data",  allow_duplicate=True),
            Output("agent-case2-filter",  "data",  allow_duplicate=True),
            Output("agent-case3-filter",  "data",  allow_duplicate=True),
            Output("agent-case4-filter",  "data",  allow_duplicate=True),
            Output("agent-filter-active", "data",  allow_duplicate=True),
        ],
        Input("agent-pending-query", "data"),
        [
            State("agent-chat-history",  "data"),
            State("agent-case1-filter",  "data"),
            State("agent-case2-filter",  "data"),
            State("agent-case3-filter",  "data"),
            State("agent-case4-filter",  "data"),
        ],
        prevent_initial_call=True,
    )
    def process_pending_query(pending, history, cur_f1, cur_f2, cur_f3, cur_f4):
        nu        = dash.no_update
        no_stores = [nu, nu, nu, nu]

        if not pending:
            return nu, *no_stores, nu

        query       = pending["query"]
        active_case = pending["active_case"]
        history     = list(history or [])

        # remove the thinking dots so that the real response takes its place
        if history and history[-1].get("intent") == "thinking":
            history = history[:-1]

        # wrap the full query cycle in a LangSmith trace
        with trace_query(query, active_case) as run:

            # detect explicit text-based reset
            if _is_reset_query(query):
                history.append({"role": "assistant", "intent": "filter", "text": "Filters cleared."})
                log_to_run(run, {"intent": "reset"})
                reset_data = {"reset": True, "params": {}, "ts": time.time()}
                store_map = {
                    "case1": [reset_data, nu,         nu,         nu        ],
                    "case2": [nu,         reset_data, nu,         nu        ],
                    "case3": [nu,         nu,         reset_data, nu        ],
                    "case4": [nu,         nu,         nu,         reset_data],
                }
                return history, *store_map.get(active_case, no_stores), False

            # retrieve current active filter params for this case
            cur_store = {"case1": cur_f1, "case2": cur_f2,
                         "case3": cur_f3, "case4": cur_f4}.get(active_case) or {}
            current_params = {} if cur_store.get("reset") else cur_store.get("params", {})

            # classify query
            classification = classify(query, active_case)

            if classification["intent"] == "explain":
                text = explain(
                    query,
                    active_case,
                    data_summary=_data_summaries.get(active_case, ""),
                    recent_history=_recent_messages(history),
                )
                history.append({"role": "assistant", "intent": "explain", "text": text})
                log_to_run(run, {"intent": "explain"})
                return history, *no_stores, nu

            new_params = classification["params"]

            # case 3: hard cap of 2 courses
            if active_case == "case3" and "course" in new_params:
                requested = new_params["course"]
                if isinstance(requested, str):
                    requested = [requested]
                if len(requested) > 2:
                    history.append({
                        "role": "assistant",
                        "intent": "explain",
                        "text": (
                            "This chart can only display two courses at a time. "
                            "Showing more would create cognitive overload and make the "
                            "comparison hard to read. Please choose any two: "
                            "A and B, A and C, or B and C."
                        ),
                    })
                    log_to_run(run, {"intent": "explain", "reason": "case3 course cap exceeded"})
                    return history, *no_stores, nu

            # case 3 indicators must all belong to the same group
            if active_case == "case3":
                for _key in ("indicator", "hide_indicator"):
                    if _key not in new_params:
                        continue
                    requested = new_params[_key]
                    if isinstance(requested, str):
                        requested = [requested]
                    groups = {_C3_INDICATOR_GROUP[ind] for ind in requested if ind in _C3_INDICATOR_GROUP}
                    if len(groups) > 1:
                        group_names = " / ".join(
                            _C3_GROUP_LABELS[g] for g in sorted(groups)
                        )
                        history.append({
                            "role": "assistant",
                            "intent": "explain",
                            "text": (
                                f"The selected indicators belong to different groups "
                                f"({group_names}), which cannot be combined in the same "
                                f"chart — each group uses its own normalisation scale and "
                                f"the values are not directly comparable across groups. "
                                f"Please pick indicators from a single group."
                            ),
                        })
                        log_to_run(run, {"intent": "explain", "reason": "cross-group indicators"})
                        return history, *no_stores, nu

            # merge new params onto currently active params so filters accumulate across turns
            params = _merge_params(current_params, new_params, active_case)

            msg = _filter_summary(params, active_case)
            history.append({"role": "assistant", "intent": "filter", "text": msg})
            log_to_run(run, {"intent": "filter", "final_params": params, "filter_summary": msg})

            filter_data = {"params": params, "ts": time.time()}
            store_map = {
                "case1": [filter_data, nu,          nu,          nu         ],
                "case2": [nu,          filter_data, nu,          nu         ],
                "case3": [nu,          nu,          filter_data, nu         ],
                "case4": [nu,          nu,          nu,          filter_data],
            }
            return history, *store_map.get(active_case, no_stores), True

    # per-case relay callbacks

    @app.callback(
        [
            Output("case1-selected-faculties", "data",   allow_duplicate=True),
            Output("case1-bar-chart",          "figure", allow_duplicate=True),
            Output("case1-dot-plot",           "figure", allow_duplicate=True),
        ],
        Input("agent-case1-filter", "data"),
        State("active-case", "data"),
        prevent_initial_call=True,
    )
    def apply_case1_filter(filter_data, active_case):
        nu = dash.no_update
        if not filter_data or active_case != "case1":
            return nu, nu, nu
        if filter_data.get("reset"):
            return _FACULTY_ORDER[:], nu, nu   # existing callbacks rebuild both charts
        params = filter_data["params"]
        result = apply_filters(params, "case1", dfs["case1"])
        if "student_gender" in params or "professor_gender" in params:
            filtered_df = result["df"]
            return nu, _build_case1_figure(filtered_df), _build_case1_dot_figure(filtered_df)
        faculty = params.get("faculty")
        if faculty is None:
            return nu, nu, nu
        if isinstance(faculty, str):
            faculty = [faculty]
        return faculty, nu, nu

    @app.callback(
        [
            Output("case2-bar-chart", "figure", allow_duplicate=True),
            Output("case2-gap-chart", "figure", allow_duplicate=True),
        ],
        Input("agent-case2-filter", "data"),
        State("active-case", "data"),
        prevent_initial_call=True,
    )
    def apply_case2_filter(filter_data, active_case):
        nu = dash.no_update
        if not filter_data or active_case != "case2":
            return nu, nu
        if filter_data.get("reset"):
            return build_case2_main_figure(dfs["case2"]), build_case2_gap_figure(dfs["case2"])
        params = filter_data["params"]
        methodology = params.get("teaching_methodology")
        if methodology is None:
            return nu, nu
        if isinstance(methodology, str):
            methodology = [methodology]
        # filter to only the selected methodologies
        # same pattern as case 1 faculties
        filtered_df = dfs["case2"][dfs["case2"]["Teaching_Methodology"].isin(methodology)]
        return build_case2_main_figure(filtered_df), _build_case2_gap_figure_safe(filtered_df)

    @app.callback(
        [
            Output("case3-selected-courses",    "data", allow_duplicate=True),
            Output("case3-active-tab",          "data", allow_duplicate=True),
            Output("case3-selected-indicators", "data", allow_duplicate=True),
        ],
        Input("agent-case3-filter", "data"),
        State("active-case", "data"),
        prevent_initial_call=True,
    )
    def apply_case3_filter(filter_data, active_case):
        nu = dash.no_update
        if not filter_data or active_case != "case3":
            return nu, nu, nu
        if filter_data.get("reset"):
            return ["A", "B"], "outcomes", None   # restore defaults, clear indicator filter
        store = apply_filters(filter_data["params"], "case3", dfs["case3"])["store_updates"]
        return (
            store.get("courses",    nu),
            store.get("tab",        nu),
            store.get("indicators", nu),
        )

    @app.callback(
        Output("case4-chart", "figure", allow_duplicate=True),
        Input("agent-case4-filter", "data"),
        State("active-case", "data"),
        prevent_initial_call=True,
    )
    def apply_case4_filter(filter_data, active_case):
        if not filter_data or active_case != "case4":
            return dash.no_update
        if filter_data.get("reset"):
            return build_case4_figure(dfs["case4"])
        result = apply_filters(filter_data["params"], "case4", dfs["case4"])
        return build_case4_figure(result["df"])

    # reset callback
    # restores the active case to its original (unfiltered) state and logsa confirmation message in the chat history.

    @app.callback(
        [
            Output("agent-chat-history", "data",          allow_duplicate=True),
            Output("agent-case1-filter", "data",          allow_duplicate=True),
            Output("agent-case2-filter", "data",          allow_duplicate=True),
            Output("agent-case3-filter", "data",          allow_duplicate=True),
            Output("agent-case4-filter", "data",          allow_duplicate=True),
            Output("agent-filter-active","data",          allow_duplicate=True),
        ],
        Input("agent-reset-btn", "n_clicks"),
        [
            State("active-case",        "data"),
            State("agent-chat-history", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_reset(n_clicks, active_case, history):
        nu = dash.no_update
        no_stores = [nu, nu, nu, nu]

        active_case = active_case or "case1"
        history = list(history or [])
        history.append({"role": "assistant", "intent": "filter", "text": "Filters cleared."})

        reset_data = {"reset": True, "params": {}, "ts": time.time()}
        store_map = {
            "case1": [reset_data, nu,         nu,         nu        ],
            "case2": [nu,         reset_data, nu,         nu        ],
            "case3": [nu,         nu,         reset_data, nu        ],
            "case4": [nu,         nu,         nu,         reset_data],
        }
        return [history, *store_map.get(active_case, no_stores), False]
