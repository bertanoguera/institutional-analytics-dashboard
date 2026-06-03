import dash
from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def case1_layout(df):
    faculties = ["Economics", "Engineering", "Law", "Humanities", "Translation"]

    # compute overall median per faculty for the kpi cards at the top
    kpi_data = {}
    for faculty in faculties:
        faculty_df = df[df["Faculty"] == faculty]
        if len(faculty_df) > 0:
            kpi_data[faculty] = faculty_df["Satisfaction_Score"].median()
        else:
            kpi_data[faculty] = 0

    return html.Div(
        [
            # title and short description
            html.Div(
                [
                    html.H2(
                        "Student satisfaction with teaching received",
                        style={
                            "fontSize": "18px",
                            "fontWeight": "bold",
                            "color": "#111",
                            "margin": "0 0 8px 0"
                        }
                    ),
                    html.P(
                        "Median satisfaction scores (0-10) rated by students to their professors, broken down by professor gender, student gender, and faculty. " \
                        "Cards below show the overall median per faculty. Bars compare scores across professor and student gender groups. " \
                        "Hover over a bar for details, or expand the section below to see the full score distribution.",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "normal",
                            "color": "#666",
                            "margin": "0"
                        }
                    )
                ],
                style={
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "padding": "16px",
                    "marginBottom": "20px"
                }
            ),

            # summary kpi cards (one per faculty)
            html.Div(
                [
                    html.Label(
                        "Faculty glossary",
                        style={
                            "fontSize": "14px",
                            "color": "#888",
                            "marginBottom": "8px",
                            "display": "block",
                        }
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        f"{kpi_data[faculty]:.1f}",
                                        style={
                                            "fontSize": "28px",
                                            "fontWeight": "500",
                                            "color": "#185FA5",
                                            "margin": "0 0 4px 0"
                                        }
                                    ),
                                    html.Div(
                                        faculty,
                                        style={
                                            "fontSize": "12px",
                                            "color": "#888",
                                            "margin": "0"
                                        }
                                    )
                                ],
                                style={
                                    "border": "1px solid #e0e0e0",
                                    "borderRadius": "8px",
                                    "padding": "12px 16px",
                                    "flex": "1",
                                    "textAlign": "center",
                                    **({"marginRight": "12px"} if faculty != faculties[-1] else {})
                                }
                            )
                            for faculty in faculties
                        ],
                        style={
                            "display": "flex",
                            "gap": "0",
                        }
                    ),
                ],
                style={"marginBottom": "20px"}
            ),

            # faculty filter buttons
            html.Div(
                [
                    html.Label(
                        "Faculties shown:",
                        style={
                            "fontSize": "14px",
                            "color": "#888",
                            "marginBottom": "8px",
                            "display": "block"
                        }
                    ),
                    html.Div(
                        [
                            html.Button(
                                faculty,
                                id=f"case1-faculty-btn-{faculty}",
                                style={
                                    "background": "#378ADD",
                                    "border": "1px solid #378ADD",
                                    "borderRadius": "20px",
                                    "padding": "6px 16px",
                                    "margin": "4px",
                                    "fontSize": "13px",
                                    "color": "white",
                                    "cursor": "pointer"
                                }
                            )
                            for faculty in faculties
                        ],
                        style={
                            "display": "flex",
                            "flexWrap": "wrap"
                        }
                    ),
                    dcc.Store(
                        id="case1-selected-faculties",
                        data=faculties
                    )
                ],
                style={
                    "marginBottom": "20px"
                }
            ),

            html.Div(
                [
                    html.Button(
                        "i",
                        id="case1-info-icon",
                        title="Students rated their satisfaction with teaching on a scale from 0 to 10, where 0 means completely dissatisfied and 10 means completely satisfied. Each bar shows the median score, the middle value when all scores are ranked from lowest to highest.",
                        style={
                            "background": "#d0d0d0",
                            "border": "none",
                            "borderRadius": "50%",
                            "width": "18px",
                            "height": "18px",
                            "fontSize": "10px",
                            "color": "white",
                            "cursor": "pointer",
                            "display": "inline-flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "marginTop": "8px",
                            "marginLeft": "8px"
                        }
                    ),
                    dcc.Graph(id="case1-bar-chart")
                ],
                style={
                    "marginBottom": "20px"
                }
            ),

            # expandable section (for advanecd users) with the full distribution plot
            html.Div(
                [
                    html.Span(
                        "Want to explore beyond the summary? The section below shows the full spread of professor scores within each selected faculty and student gender group.",
                        style={
                            "fontSize": "14px",
                            "color": "#888",
                            "fontStyle": "italic",
                            "marginBottom": "6px",
                            "display": "block"
                        }
                    ),
                    html.Button(
                        "▸ View full distribution (for advanced users)",
                        id="case1-expand-btn",
                        style={
                            "background": "none",
                            "border": "none",
                            "color": "#378ADD",
                            "cursor": "pointer",
                            "fontSize": "16px",
                            "padding": "0",
                            "marginTop": "8px"
                        }
                    ),
                    html.Div(
                        [
                            dcc.Graph(id="case1-dot-plot")
                        ],
                        id="case1-detail-div",
                        style={"display": "none"}
                    )
                ]
            ),

            html.Div(
                "Scores from UPF satisfaction surveys, filtered by RAS reliability threshold. "
                "Only courses with sufficient respondents relative to enrolled students are included.",
                style={
                    "background": "#F8F8F8",
                    "borderRadius": "6px",
                    "padding": "10px 14px",
                    "fontSize": "12px",
                    "color": "#888",
                    "marginTop": "12px"
                }
            )
        ],
        style={
            "padding": "20px",
            "maxWidth": "1200px",
            "margin": "0 auto"
        }
    )
