import dash
from dash import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


# spreads dots horizontally in the boxplot when two professors have the same median score
# so they don't stack on top of each other (unique values stay centered)
def _jitter_x(y_vals, center, step=0.10):
    from collections import Counter, defaultdict
    counts   = Counter(y_vals)
    idx_seen = defaultdict(int)
    x_pos = []
    for y in y_vals:
        n = counts[y]
        i = idx_seen[y]
        if n == 1:
            x_pos.append(center)
        else:
            # spread symetrically around center 
            x_pos.append(center + (i - (n - 1) / 2.0) * step)
        idx_seen[y] += 1
    return x_pos


def register_case1_callbacks(app, df):

    faculties = ["Economics", "Engineering", "Law", "Humanities", "Translation"]

    selected_style = {
        "background": "#378ADD",
        "border": "1px solid #378ADD",
        "borderRadius": "20px",
        "padding": "6px 16px",
        "margin": "4px",
        "fontSize": "13px",
        "color": "white",
        "cursor": "pointer"
    }

    unselected_style = {
        "background": "white",
        "border": "1px solid #ccc",
        "borderRadius": "20px",
        "padding": "6px 16px",
        "margin": "4px",
        "fontSize": "13px",
        "color": "#444",
        "cursor": "pointer"
    }

    @app.callback(
        Output("case1-selected-faculties", "data"),
        [
            Input("case1-faculty-btn-Economics", "n_clicks"),
            Input("case1-faculty-btn-Engineering", "n_clicks"),
            Input("case1-faculty-btn-Law", "n_clicks"),
            Input("case1-faculty-btn-Humanities", "n_clicks"),
            Input("case1-faculty-btn-Translation", "n_clicks")
        ],
        State("case1-selected-faculties", "data"),
        prevent_initial_call=True
    )
    def update_selected_faculties(ec_clicks, eng_clicks, law_clicks, hum_clicks, trans_clicks, current_selection):
        if current_selection is None:
            current_selection = faculties.copy()

        current_selection = current_selection.copy() if isinstance(current_selection, list) else list(current_selection)

        ctx = dash.callback_context
        if not ctx.triggered:
            return current_selection

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        faculty = button_id.replace("case1-faculty-btn-", "")

        # toggle: remove if already selected (min 1), add if not
        if faculty in current_selection:
            if len(current_selection) > 1:
                current_selection.remove(faculty)
        else:
            current_selection.append(faculty)
            current_selection = sorted(current_selection, key=lambda x: faculties.index(x))

        return current_selection

    @app.callback(
        [
            Output("case1-faculty-btn-Economics", "style"),
            Output("case1-faculty-btn-Engineering", "style"),
            Output("case1-faculty-btn-Law", "style"),
            Output("case1-faculty-btn-Humanities", "style"),
            Output("case1-faculty-btn-Translation", "style")
        ],
        Input("case1-selected-faculties", "data")
    )
    def update_button_styles(selected_faculties):
        styles = []
        for faculty in faculties:
            if faculty in selected_faculties:
                styles.append(selected_style)
            else:
                styles.append(unselected_style)
        return styles

    @app.callback(
        Output("case1-bar-chart", "figure"),
        Input("case1-selected-faculties", "data")
    )
    def update_bar_chart(selected_faculties):
        if not selected_faculties or len(selected_faculties) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Please select at least one faculty.")
            return fig
        filtered_df = df[df["Faculty"].isin(selected_faculties)].copy()
        aggregations = []
        for faculty in selected_faculties:
            faculty_df = filtered_df[filtered_df["Faculty"] == faculty]
            for prof_gender in ["Female", "Male"]:
                prof_gender_df = faculty_df[faculty_df["Professor_Gender"] == prof_gender]
                for stud_gender in ["Female", "Male"]:
                    stud_gender_df = prof_gender_df[prof_gender_df["Student_Gender"] == stud_gender]

                    if len(stud_gender_df) > 0:
                        scores = stud_gender_df["Satisfaction_Score"]
                        prof_medians = stud_gender_df.groupby("Professor_ID")["Satisfaction_Score"].median()

                        agg_dict = {
                            "Faculty": faculty,
                            "Professor_Gender": prof_gender,
                            "Student_Gender": stud_gender,
                            "Median": scores.median(),
                            "Count_Professors": len(prof_medians)
                        }
                        aggregations.append(agg_dict)

        agg_df = pd.DataFrame(aggregations)

        if len(agg_df) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No data available.")
            return fig

        colors        = {"Female": "#378ADD", "Male": "#EF9F27"}
        hoverlabel_bg = {"Female": "#AFD0F1", "Male": "#F6D4B0"}

        if len(selected_faculties) > 1:
            fig = make_subplots(
                rows=1,
                cols=len(selected_faculties),
                shared_yaxes=True,
                horizontal_spacing=0.08,
                subplot_titles=selected_faculties
            )

            for col_idx, faculty in enumerate(selected_faculties, 1):
                faculty_agg = agg_df[agg_df["Faculty"] == faculty]

                for prof_gender in ["Female", "Male"]:
                    prof_data = faculty_agg[faculty_agg["Professor_Gender"] == prof_gender]

                    x_vals = prof_data["Student_Gender"].tolist()
                    y_vals = prof_data["Median"].tolist()

                    hover_texts = []
                    for _, row in prof_data.iterrows():
                        hover_text = (
                            f"<b>Professor gender:</b> {row['Professor_Gender']}<br>"
                            f"<b>Student gender:</b> {row['Student_Gender']}<br>"
                            f"<b>Faculty:</b> {row['Faculty']}<br>"
                            f"<b>Median:</b> {row['Median']:.2f}<br>"
                            f"<b>Professors:</b> {int(row['Count_Professors'])}"
                        )
                        hover_texts.append(hover_text)

                    fig.add_trace(
                        go.Bar(
                            x=x_vals,
                            y=y_vals,
                            name=prof_gender,
                            offsetgroup=prof_gender,
                            width=0.35,
                            marker=dict(color=colors[prof_gender], line=dict(width=1, color="#ffffff")),
                            hovertext=hover_texts,
                            hovertemplate="%{hovertext}<extra></extra>",
                            hoverlabel=dict(
                                bgcolor=hoverlabel_bg[prof_gender],
                                bordercolor=colors[prof_gender],
                                font=dict(color="#333", size=12, family="Arial"),
                            ),
                            showlegend=(col_idx == 1),
                            legendgroup=prof_gender
                        ),
                        row=1,
                        col=col_idx
                    )

            fig.update_yaxes(range=[0, 10], title_text="Student satisfaction score (0–10)", row=1, col=1, tick0=0, dtick=1, showgrid=True, gridcolor="lightgray", gridwidth=1)
            for col_idx in range(2, len(selected_faculties) + 1):
                fig.update_yaxes(range=[0, 10], row=1, col=col_idx, tick0=0, dtick=1, showgrid=True, gridcolor="lightgray", gridwidth=1)

            for col_idx in range(1, len(selected_faculties) + 1):
                fig.update_xaxes(
                    row=1,
                    col=col_idx,
                    title_text="",
                    categoryorder="array",
                    categoryarray=["Female", "Male"],
                    tickmode="array",
                    tickvals=["Female", "Male"],
                    ticktext=["Female<br>students", "Male<br>students"],
                    showgrid=False,
                )

            fig.update_layout(
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

        else:
            fig = go.Figure()

            for prof_gender in ["Female", "Male"]:
                prof_data = agg_df[agg_df["Professor_Gender"] == prof_gender]

                x_vals = prof_data["Student_Gender"].tolist()
                y_vals = prof_data["Median"].tolist()

                hover_texts = []
                for _, row in prof_data.iterrows():
                    hover_text = (
                        f"<b>Professor gender:</b> {row['Professor_Gender']}<br>"
                        f"<b>Student gender:</b> {row['Student_Gender']}<br>"
                        f"<b>Faculty:</b> {row['Faculty']}<br>"
                        f"<b>Median:</b> {row['Median']:.2f}<br>"
                        f"<b>Professors:</b> {int(row['Count_Professors'])}"
                    )
                    hover_texts.append(hover_text)

                fig.add_trace(
                    go.Bar(
                        x=x_vals,
                        y=y_vals,
                        name=prof_gender,
                        offsetgroup=prof_gender,
                        width=0.35,
                        marker=dict(color=colors[prof_gender], line=dict(width=1, color="#ffffff")),
                        hovertext=hover_texts,
                        hovertemplate="%{hovertext}<extra></extra>",
                        hoverlabel=dict(
                            bgcolor=hoverlabel_bg[prof_gender],
                            bordercolor=colors[prof_gender],
                            font=dict(color="#333", size=12, family="Arial"),
                        ),
                    )
                )

            fig.update_xaxes(
                title_text="",
                categoryorder="array",
                categoryarray=["Female", "Male"],
                tickmode="array",
                tickvals=["Female", "Male"],
                ticktext=["Female<br>students", "Male<br>students"],
                showgrid=False,
            )
            fig.update_yaxes(
                title_text="Student satisfaction score (0–10)",
                range=[0, 10],
                tick0=0,
                dtick=1,
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray"
            )

            fig.update_layout(
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

        return fig

    @app.callback(
        [
            Output("case1-detail-div", "style"),
            Output("case1-expand-btn", "children")
        ],
        Input("case1-expand-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_detail_section(n_clicks):
        if n_clicks is None or n_clicks % 2 == 0:
            return {"display": "none"}, "▸ View full distribution (for advanced users)"
        else:
            return {"display": "block"}, "▾ Hide full distribution"

    @app.callback(
        Output("case1-dot-plot", "figure"),
        Input("case1-selected-faculties", "data")
    )
    def update_dot_plot(selected_faculties):
        if not selected_faculties or len(selected_faculties) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Please select at least one faculty.")
            return fig

        faculty_order = ["Economics", "Engineering", "Law", "Humanities", "Translation"]
        selected_faculties = [f for f in faculty_order if f in selected_faculties]

        fig = make_subplots(
            rows=1,
            cols=len(selected_faculties),
            subplot_titles=selected_faculties,
            shared_yaxes=True,
            horizontal_spacing=0.10,
        )

        colors        = {"Female": "#378ADD", "Male": "#EF9F27"}
        hoverlabel_bg = {"Female": "#AFD0F1", "Male": "#F6D4B0"}

        # female students map to x = 0, male students to x = 1
        x_center = {"Female": 0, "Male": 1}

        for col_idx, faculty in enumerate(selected_faculties, 1):
            faculty_df = df[df["Faculty"] == faculty]

            for stud_gender in ["Female", "Male"]:
                xc  = x_center[stud_gender]
                sub = faculty_df[faculty_df["Student_Gender"] == stud_gender]
                if len(sub) == 0:
                    continue

                # aggregate to professor level medians
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

                scores = grouped["Satisfaction_Score"]

                total_prof = grouped["Professor_ID"].nunique()
                median_val = scores.median()
                q1         = scores.quantile(0.25)
                q3         = scores.quantile(0.75)
                min_val    = scores.min()
                max_val    = scores.max()

                #  any dot outside these is an outlier
                iqr         = float(q3 - q1)
                lower_fence = float(q1 - 1.5 * iqr)
                upper_fence = float(q3 + 1.5 * iqr)

                # box is drawn from inliers only so whiskers stop at the fence
                # and outlier dots appear clearly outside the box
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
                        v       = row["Satisfaction_Score"]
                        is_out  = v < lower_fence or v > upper_fence
                        symbols.append("diamond" if is_out else "circle")
                        label   = "<b>⚠ Outlier</b><br>" if is_out else ""
                        per_dot_hover.append(
                            f"{label}"
                            f"<b>Professor gender:</b> {prof_gender}<br>"
                            f"<b>Student gender:</b> {stud_gender}<br>"
                            f"<b>Faculty:</b> {faculty}<br>"
                            f"<b>Score:</b> {v:.2f}<br>"
                            f"<b>Total professors:</b> {total_prof}<br>"
                            f"<b>Group median:</b> {median_val:.2f}<br>"
                            f"<b>Q1–Q3:</b> {q1:.2f} – {q3:.2f}<br>"
                            f"<b>Range:</b> {min_val:.2f} – {max_val:.2f}"
                        )

                    fig.add_trace(
                        go.Scatter(
                            x=dots["x_jitter"].tolist(),
                            y=dots["Satisfaction_Score"].tolist(),
                            mode="markers",
                            name=f"{prof_gender} professor",
                            legendgroup=prof_gender,
                            showlegend=(col_idx == 1 and stud_gender == "Female"),
                            marker=dict(
                                size=8,
                                color=colors[prof_gender],
                                opacity=0.82,
                                symbol=symbols,
                                line=dict(width=0.5, color="white"),
                            ),
                            hovertext=per_dot_hover,
                            hovertemplate="%{hovertext}<extra></extra>",
                            hoverlabel=dict(
                                bgcolor=hoverlabel_bg[prof_gender],
                                bordercolor=colors[prof_gender],
                                font=dict(color="#333", size=12, family="Arial"),
                            ),
                        ),
                        row=1, col=col_idx,
                    )

        n = len(selected_faculties)
        for col_idx in range(1, n + 1):
            fig.update_xaxes(
                tickmode="array",
                tickvals=[0, 1],
                ticktext=["Female<br>students", "Male<br>students"],
                range=[-0.45, 1.45],
                showgrid=False,
                title_text="",
                row=1,
                col=col_idx,
            )
            fig.update_yaxes(
                autorange=True,
                showgrid=True,
                gridcolor="lightgray",
                gridwidth=1,
                title_text="Student satisfaction score (0–10)" if col_idx == 1 else "",
                row=1,
                col=col_idx,
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
