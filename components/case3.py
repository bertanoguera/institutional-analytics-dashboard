from dash import html, dcc


def case3_layout(df):

    # button styles, toggled by callbacks depending on selection state
    _sel = {
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

    _unsel = {
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

    _tab_active = {
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

    _tab_inactive = {
        "color": "#888",
        "borderBottom": "2px solid transparent",
        "background": "none",
        "borderTop": "none",
        "borderLeft": "none",
        "borderRight": "none",
        "padding": "8px 14px",
        "cursor": "pointer",
    }

    def _course_btn(course, methods, btn_id, style):
        return html.Button(
            [
                html.Div(
                    "Course " + course,
                    style={"fontWeight": "bold", "fontSize": "14px"},
                ),
                html.Div(
                    methods,
                    style={"fontSize": "11px", "marginTop": "2px", "opacity": 0.75},
                ),
            ],
            id=btn_id,
            style=style,
        )

    def _tab_btn(label, btn_id, style):
        return html.Button(label, id=btn_id, style=style)

    return html.Div(
        [
            html.Div(
                [
                    html.H2(
                        "Social comparison of courses with high Learning Management System (LMS) interaction level",
                        style={
                            "fontSize": "18px",
                            "fontWeight": "bold",
                            "margin": "0 0 8px 0",
                        },
                    ),
                    html.P(
                        (
                            "Three courses with unusually high LMS interaction are compared against the "
                            "institutional average across four dimensions: student outcomes, LMS usage patterns, "
                            "planned task types, and social design. All values are normalized to a 0-1 scale so "
                            "indicators with different units can be compared directly. Indicators within each "
                            "group are independent of one another. "
                            "Hover over any variable name on the chart axis to read its definition."
                        ),
                        style={
                            "fontSize": "13px",
                            "color": "#666",
                            "lineHeight": "1.6",
                            "margin": "0",
                        },
                    ),
                ],
                style={
                    "border": "1px solid #e0e0e0",
                    "borderRadius": "8px",
                    "padding": "16px",
                    "marginBottom": "20px",
                },
            ),

            # course selector  (max 2 courses can be active at once)
            html.Div(
                [
                    html.Label(
                        "Select up to two courses to compare against the institutional average:",
                        style={
                            "fontSize": "14px",
                            "color": "#888",
                            "marginBottom": "8px",
                            "display": "block",
                        },
                    ),
                    html.Div(
                        [
                            _course_btn("A", "LECT, CASE",       "case3-btn-A", _sel),
                            _course_btn("B", "LECT, PJBL, FLIP", "case3-btn-B", _sel),
                            _course_btn("C", "LECT, PRBL",       "case3-btn-C", _unsel),
                        ],
                        style={"display": "flex", "flexWrap": "wrap"},
                    ),
                    dcc.Store(id="case3-selected-courses", data=["A", "B"]),
                ],
                style={"marginBottom": "20px"},
            ),

            # variable group tabs
            html.Div(
                [
                    html.Div(
                        [
                            _tab_btn("Student outcomes", "case3-tab-outcomes", _tab_active),
                            _tab_btn("LMS usage",        "case3-tab-lms",      _tab_inactive),
                            _tab_btn("Task types",       "case3-tab-tasks",    _tab_inactive),
                            _tab_btn("Social & modality","case3-tab-social",   _tab_inactive),
                        ],
                        style={"display": "flex", "borderBottom": "1px solid #e0e0e0"},
                    ),
                    html.Div(
                        id="case3-variable-list",
                        style={
                            "fontSize": "11px",
                            "color": "#888",
                            "fontStyle": "italic",
                            "marginTop": "6px",
                        },
                    ),
                    dcc.Store(id="case3-active-tab", data="outcomes"),
                ],
                style={"marginBottom": "20px"},
            ),

            html.Div(
                [dcc.Graph(id="case3-bar-chart")],
                style={"marginBottom": "20px"},
            ),

            html.Div(
                id="case3-insight-text",
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

            html.Div(
                (
                    "The indicators within each group are independent of one another, meaning that a high score "
                    "on one variable does not predict scores on others. Variables from different groups use "
                    "different original scales and should not be compared directly to one another, only against "
                    "the institutional average within the same group."
                ),
                style={
                    "background": "#F8F8F8",
                    "borderRadius": "6px",
                    "padding": "10px 14px",
                    "fontSize": "12px",
                    "color": "#888",
                    "marginTop": "12px",
                },
            ),
        ]
    )
