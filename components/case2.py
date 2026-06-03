import dash
from dash import html, dcc


def case2_layout(df):
    methodology_pills = [
        {"abbr": "LECT", "name": "Lectures"},
        {"abbr": "PJBL", "name": "Project-based learning"},
        {"abbr": "FLIP", "name": "Flipped classroom"},
        {"abbr": "PRBL", "name": "Problem-based learning"},
        {"abbr": "CASE", "name": "Case studies"}
    ]

    return html.Div(
        [
            html.Div(
                [
                    html.H2(
                        "Student performance by active teaching methodology and workload satisfaction",
                        style={
                            "fontSize": "18px",
                            "fontWeight": "bold",
                            "color": "#111",
                            "margin": "0 0 8px 0"
                        }
                    ),
                    html.P(
                        "Weighted student performance (0-1 scale) compared between courses rated highest (Top courses) "
                        "and lowest (Bottom courses) for workload satisfaction, broken down by teaching methodology. "
                        "Bars show whether students in well-rated courses consistently outperform those "
                        "in poorly-rated ones, and how much that gap varies across methodologies. "
                        "Hover over a bar for details, or expand the section below to see the performance gap.",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "normal",
                            "color": "#444",
                            "margin": "0"
                        }
                    ),
                    html.Hr(style={"border": "none", "borderTop": "1px solid #e0e0e0", "margin": "12px 0"}),
                    html.P(
                        "What does the performance score measure?",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "bold",
                            "color": "#444",
                            "margin": "0 0 4px 0",
                        }
                    ),
                    html.P(
                        "Performance is measured through a normalized weighted grade, calculated at course level using the Spanish grading system (fail, pass, notable, excellent). Each band is assigned its midpoint value, and a weighted average is computed across all students. The result is normalized relative to the institutional range, it does not represent a percentage.",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "normal",
                            "color": "#444",
                            "lineHeight": "1.6",
                            "margin": "0 0 12px 0"
                        }
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div("Fail", style={"fontSize": "11px", "fontWeight": "500"}),
                                    html.Div("≈ 0.25–0.38", style={"fontSize": "10px", "marginTop": "2px"})
                                ],
                                style={"flex": "1", "padding": "8px 6px", "textAlign": "center", "color": "white", "fontWeight": "500", "background": "#E8443A"}
                            ),
                            html.Div(
                                [
                                    html.Div("Pass", style={"fontSize": "11px", "fontWeight": "500"}),
                                    html.Div("≈ 0.38–0.46", style={"fontSize": "10px", "marginTop": "2px"})
                                ],
                                style={"flex": "1", "padding": "8px 6px", "textAlign": "center", "color": "white", "fontWeight": "500", "background": "#E8943A"}
                            ),
                            html.Div(
                                [
                                    html.Div("Notable", style={"fontSize": "11px", "fontWeight": "500"}),
                                    html.Div("≈ 0.46–0.54", style={"fontSize": "10px", "marginTop": "2px"})
                                ],
                                style={"flex": "1", "padding": "8px 6px", "textAlign": "center", "color": "white", "fontWeight": "500", "background": "#378ADD"}
                            ),
                            html.Div(
                                [
                                    html.Div("Excellent", style={"fontSize": "11px", "fontWeight": "500"}),
                                    html.Div("≈ 0.54–0.60", style={"fontSize": "10px", "marginTop": "2px"})
                                ],
                                style={"flex": "1", "padding": "8px 6px", "textAlign": "center", "color": "white", "fontWeight": "500", "background": "#1D9E75"}
                            )
                        ],
                        style={"display": "flex", "gap": "0", "marginBottom": "10px"}
                    ),
                    html.Div(
                        [
                            html.Div("lower performance", style={"fontSize": "12px", "color": "#555"}),
                            html.Div("higher performance", style={"fontSize": "12px", "color": "#555"})
                        ],
                        style={"display": "flex", "justifyContent": "space-between"}
                    )
                ],
                style={
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "padding": "16px",
                    "marginBottom": "20px"
                }
            ),

            # methodology glossary
            html.Div(
                [
                    html.Label(
                        "Methodology glossary",
                        style={
                            "fontSize": "14px",
                            "color": "#555",
                            "marginBottom": "8px",
                            "display": "block"
                        }
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        item["abbr"],
                                        style={
                                            "fontSize": "24px",
                                            "fontWeight": "500",
                                            "color": "#185FA5",
                                            "margin": "0 0 4px 0"
                                        }
                                    ),
                                    html.Div(
                                        item["name"],
                                        style={
                                            "fontSize": "12px",
                                            "color": "#555",
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
                                    "marginRight": "12px"
                                }
                            )
                            for i, item in enumerate(methodology_pills)
                            if i < len(methodology_pills) - 1
                        ] + [
                            html.Div(
                                [
                                    html.Div(
                                        methodology_pills[-1]["abbr"],
                                        style={
                                            "fontSize": "24px",
                                            "fontWeight": "500",
                                            "color": "#185FA5",
                                            "margin": "0 0 4px 0"
                                        }
                                    ),
                                    html.Div(
                                        methodology_pills[-1]["name"],
                                        style={
                                            "fontSize": "12px",
                                            "color": "#555",
                                            "margin": "0"
                                        }
                                    )
                                ],
                                style={
                                    "border": "1px solid #e0e0e0",
                                    "borderRadius": "8px",
                                    "padding": "12px 16px",
                                    "flex": "1",
                                    "textAlign": "center"
                                }
                            )
                        ],
                        style={
                            "display": "flex",
                            "gap": "0",
                            "marginBottom": "20px"
                        }
                    )
                ],
                style={"marginBottom": "20px"}
            ),

            # key insight
            html.Div(
                "Top courses consistently reach excellent performance while bottom courses fall into fail or pass. The gap is widest in lectures and case studies, and narrowest in flipped classroom.",
                style={
                    "background": "#E6F1FB",
                    "borderLeft": "3px solid #378ADD",
                    "borderRadius": "0 6px 6px 0",
                    "padding": "10px 14px",
                    "marginBottom": "20px",
                    "fontSize": "13px",
                    "color": "#0C447C",
                    "lineHeight": "1.6"
                }
            ),

            html.Div(
                [
                    dcc.Graph(id="case2-bar-chart")
                ],
                style={"marginBottom": "20px"}
            ),

            # expandable gap chart for advanced users
            html.Div(
                [
                    html.Span(
                        "How large is the difference in performance between top and bottom-rated courses for each methodology?",
                        style={
                            "fontSize": "14px",
                            "color": "#555",
                            "fontStyle": "italic",
                            "marginBottom": "6px",
                            "display": "block"
                        }
                    ),
                    html.Button(
                        "▸ View performance gap (for advanced users)",
                        id="case2-expand-btn",
                        n_clicks=0,
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
                        [dcc.Graph(id="case2-gap-chart")],
                        id="case2-detail-div",
                        style={"display": "none"}
                    )
                ]
            ),

            html.Div(
                "These results show an association between workload satisfaction and student performance, not a causal relationship. Differences may reflect course-level factors such as course characteristics, learning design, student's workload and performance, not the teaching methodology alone.",
                style={
                    "background": "#F8F8F8",
                    "borderRadius": "6px",
                    "padding": "10px 14px",
                    "fontSize": "12px",
                    "color": "#555",
                    "marginTop": "12px"
                }
            )
        ]
    )
