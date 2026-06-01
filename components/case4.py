from dash import html, dcc


def case4_layout(df):

    methodology_pills = [
        {"abbr": "LECT", "name": "Lectures"},
        {"abbr": "PJBL", "name": "Project-based learning"},
        {"abbr": "FLIP", "name": "Flipped classroom"},
        {"abbr": "PRBL", "name": "Problem-based learning"},
        {"abbr": "CASE", "name": "Case studies"},
    ]

    def _pill(item, last=False):
        return html.Div(
            [
                html.Div(
                    item["abbr"],
                    style={
                        "fontSize": "24px",
                        "fontWeight": "500",
                        "color": "#185FA5",
                        "margin": "0 0 4px 0",
                    },
                ),
                html.Div(
                    item["name"],
                    style={"fontSize": "12px", "color": "#888", "margin": "0"},
                ),
            ],
            style={
                "border": "1px solid #e0e0e0",
                "borderRadius": "8px",
                "padding": "12px 16px",
                "flex": "1",
                "textAlign": "center",
                **({"marginRight": "12px"} if not last else {}),
            },
        )

    return html.Div(
        [
            # title and description block
            html.Div(
                [
                    html.H2(
                        "Diversity of Learning Management System (LMS) tasks by teaching methodology and workload satisfaction",
                        style={
                            "fontSize": "18px",
                            "fontWeight": "bold",
                            "margin": "0 0 8px 0",
                        },
                    ),
                    html.P(
                        "Shannon Diversity Index, a measure of LMS task variety (0-2.5 scale), "
                        "compared between courses rated highest (Top courses)and lowest (Bottom courses) for workload satisfaction, "
                        "broken down by teaching methodology. "
                        "Bars show whether more varied task design is associated with better workload "
                        "satisfaction, and highlight where that pattern breaks down. "
                        "Hover over a bar for exact values.",
                        style={"fontSize": "14px", "color": "#666", "margin": "0"},
                    ),
                ],
                style={
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "padding": "16px",
                    "marginBottom": "20px",
                },
            ),

            # Shannon Diversity Index explainer block
            html.Div(
                [
                    html.Label(
                        "What is the Shannon Diversity Index?",
                        style={
                            "fontSize": "14px",
                            "fontWeight": "bold",
                            "color": "#333",
                            "marginBottom": "8px",
                            "display": "block",
                        },
                    ),
                    html.P(
                        (
                            "A variety score for LMS task types. Higher values indicate a wider mix of "
                            "activity types, such as, quizzes, forums, assignments, resources, and so on. "
                            "Lower values indicate that fewer types dominate the course. "
                            "The scale runs from 0 (a single activity type only) to 2.5 "
                            "(maximum variety across all types)."
                        ),
                        style={
                            "fontSize": "13px",
                            "color": "#666",
                            "lineHeight": "1.6",
                            "margin": "0 0 12px 0",
                        },
                    ),
                    # gradient scale bar
                    html.Div(
                        style={
                            "background": "linear-gradient(to right, #d6eaf8, #1D9E75)",
                            "height": "8px",
                            "borderRadius": "4px",
                            "marginBottom": "4px",
                        }
                    ),
                    html.Div(
                        [
                            html.Span(
                                "0 — single type",
                                style={"fontSize": "10px", "color": "#888"},
                            ),
                            html.Span(
                                "1.25",
                                style={"fontSize": "10px", "color": "#888"},
                            ),
                            html.Span(
                                "2.5 — max variety",
                                style={"fontSize": "10px", "color": "#888"},
                            ),
                        ],
                        style={"display": "flex", "justifyContent": "space-between"},
                    ),
                ],
                style={
                    "background": "#F8F8F8",
                    "borderRadius": "8px",
                    "padding": "14px 16px",
                    "marginBottom": "20px",
                },
            ),

            # methodology glossary as in case 2
            html.Div(
                [
                    html.Label(
                        "Methodology glossary",
                        style={
                            "fontSize": "14px",
                            "color": "#888",
                            "marginBottom": "8px",
                            "display": "block",
                        },
                    ),
                    html.Div(
                        [
                            _pill(item, last=(i == len(methodology_pills) - 1))
                            for i, item in enumerate(methodology_pills)
                        ],
                        style={"display": "flex", "gap": "0", "marginBottom": "0"},
                    ),
                ],
                style={"marginBottom": "20px"},
            ),

            # key insight annotation
            html.Div(
                (
                    "Across most methodologies, courses with higher workload satisfaction show greater "
                    "task diversity. Project-based learning shows the largest gap between Top and Bottom courses. Flipped Classroom is "
                    "the exception."
                ),
                style={
                    "background": "#E6F1FB",
                    "borderLeft": "3px solid #378ADD",
                    "borderRadius": "0 6px 6px 0",
                    "padding": "10px 14px",
                    "marginBottom": "20px",
                    "fontSize": "13px",
                    "color": "#0C447C",
                    "lineHeight": "1.6",
                },
            ),

            # main chart
            html.Div(
                [dcc.Graph(id="case4-chart")],
                style={"marginBottom": "16px"},
            ),

            # FLIP anomaly callout 
            html.Div(
                [
                    html.Span(
                        "⚠  ",
                        style={"color": "#C0392B", "fontWeight": "bold", "fontSize": "14px"},
                    ),
                    html.Span(
                        "Flipped Classroom anomaly: ",
                        style={"fontWeight": "bold", "color": "#C0392B"},
                    ),
                    (
                        "Flipped Classroom bottom-rated courses display greater task diversity than "
                        "top-rated courses, the reverse of all other methodologies. This may reflect "
                        "that in flipped classroom contexts, greater variety of online tasks is "
                        "associated with increased perceived workload rather than improved workload "
                        "satisfaction."
                    ),
                ],
                style={
                    "background": "#FDEDEC",
                    "borderLeft": "3px solid #E8443A",
                    "borderRadius": "0 6px 6px 0",
                    "padding": "10px 14px",
                    "marginBottom": "20px",
                    "fontSize": "13px",
                    "color": "#333",
                    "lineHeight": "1.6",
                },
            ),

            # interpretation note
            html.Div(
                (
                    "These results show an association between task diversity and workload satisfaction, "
                    "not a causal relationship. The direction of the relationship may vary by methodology, "
                    "as the Flipped Classroom case illustrates. Course-level factors such as course characteristics, "
                    "learning design, and student's workload may account for the observed patterns."
                ),
                style={
                    "background": "#F8F8F8",
                    "borderRadius": "6px",
                    "padding": "10px 14px",
                    "fontSize": "12px",
                    "color": "#888",
                    "marginTop": "4px",
                },
            ),
        ]
    )
