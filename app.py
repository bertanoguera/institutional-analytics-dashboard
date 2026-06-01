import dash
from dash import html, dcc, Input, Output, State, callback_context
import pandas as pd
from components.case1 import case1_layout
from components.case2 import case2_layout
from components.case3 import case3_layout
from components.case4 import case4_layout
from callbacks.case1_callbacks import register_case1_callbacks
from callbacks.case2_callbacks import register_case2_callbacks
from callbacks.case3_callbacks import register_case3_callbacks
from callbacks.case4_callbacks import register_case4_callbacks
from agent_callbacks import register_agent_callbacks

# load datasets once at startup
df1 = pd.read_csv("data/case1_student_satisfaction.csv")
df2 = pd.read_csv("data/case2_teaching_methodology_performance.csv")
df3 = pd.read_csv("data/case3_social_comparison_courses.csv")
df4 = pd.read_csv("data/case4_shannon_diversity_by_methodology.csv")

dfs = {"case1": df1, "case2": df2, "case3": df3, "case4": df4}

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# tab button styles
TAB_BASE_STYLE = {
    "background": "none",
    "border": "none",
    "borderBottom": "2px solid transparent",
    "color": "#888",
    "cursor": "pointer",
    "fontSize": "14px",
    "padding": "12px 18px",
    "marginRight": "4px",
}

TAB_ACTIVE_STYLE = {
    **TAB_BASE_STYLE,
    "color": "#378ADD",
    "borderBottom": "2px solid #378ADD",
}

TAB_INACTIVE_STYLE = {
    **TAB_BASE_STYLE,
    "color": "#888",
    "borderBottom": "2px solid transparent",
}

# chat panel placeholder text
_PLACEHOLDER = (
    "Ask about the data, or filter it"
)

# layout
app.layout = html.Div(
    [
        # left panel for navigation and case content
        html.Div(
            [
                html.Div(
                    [
                        html.Button("Case 1", id="nav-case1", n_clicks=0, style=TAB_ACTIVE_STYLE),
                        html.Button("Case 2", id="nav-case2", n_clicks=0, style=TAB_INACTIVE_STYLE),
                        html.Button("Case 3", id="nav-case3", n_clicks=0, style=TAB_INACTIVE_STYLE),
                        html.Button("Case 4", id="nav-case4", n_clicks=0, style=TAB_INACTIVE_STYLE),
                    ],
                    style={
                        "display": "flex",
                        "borderBottom": "1px solid #e0e0e0",
                        "paddingBottom": "4px",
                        "marginBottom": "20px",
                    },
                ),
                dcc.Store(id="active-case", data="case1"),
                # per-case filter stores: always in DOM so agent callbacks
                # can safely write to them regardless of which tab is active
                dcc.Store(id="agent-case1-filter", data=None),
                dcc.Store(id="agent-case2-filter", data=None),
                dcc.Store(id="agent-case3-filter", data=None),
                dcc.Store(id="agent-case4-filter", data=None),
                dcc.Store(id="agent-chat-history", data=[]),
                dcc.Store(id="agent-filter-active", data=False),
                dcc.Store(id="agent-pending-query", data=None),
                html.Div(id="page-content", children=case1_layout(df1)),
            ],
            style={
                "flex": "1",
                "minWidth": "0",
                "overflowY": "auto",
                "height": "100vh",
                "padding": "20px",
                "boxSizing": "border-box",
            },
        ),

        # right panel for the AI chat
        html.Div(
            [
                # header
                html.Div(
                    [
                        html.Div(
                            "AI Assistant",
                            style={
                                "fontSize": "14px",
                                "fontWeight": "600",
                                "color": "#185FA5",
                                "letterSpacing": "0.02em",
                            },
                        ),
                        html.Button(
                            "Reset filters",
                            id="agent-reset-btn",
                            n_clicks=0,
                            disabled=True,
                            style={
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
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "paddingBottom": "12px",
                        "marginBottom": "14px",
                        "borderBottom": "1px solid #e0e0e0",
                    },
                ),

                # response area takes all remaining vertical space
                html.Div(
                    dcc.Loading(
                        html.Div(
                            id="agent-response-output",
                            children=html.Div(
                                _PLACEHOLDER,
                                style={
                                    "fontSize": "13px",
                                    "color": "#aaa",
                                    "lineHeight": "1.7",
                                    "fontStyle": "italic",
                                },
                            ),
                        ),
                        type="dot",
                        color="#378ADD",
                    ),
                    id="agent-response-panel",
                    style={
                        "flex": "1",
                        "overflowY": "auto",
                        "paddingBottom": "8px",
                        "position": "relative",
                    },
                ),

                # input row
                html.Div(
                    [
                        dcc.Textarea(
                            id="agent-query-input",
                            placeholder="Ask or filter...",
                            style={
                                "flex": "1",
                                "border": "1px solid #d0d0d0",
                                "borderRadius": "12px",
                                "padding": "12px 18px",
                                "fontSize": "14px",
                                "outline": "none",
                                "marginRight": "10px",
                                "fontFamily": "Arial, sans-serif",
                                "color": "#333",
                                "background": "white",
                                "resize": "none",
                                "height": "72px",
                                "lineHeight": "1.5",
                                "overflowY": "auto",
                                "boxSizing": "border-box",
                            },
                        ),
                        html.Button(
                            "Send",
                            id="agent-submit-btn",
                            n_clicks=0,
                            style={
                                "background": "#378ADD",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "20px",
                                "padding": "0 20px",
                                "fontSize": "13px",
                                "fontWeight": "500",
                                "cursor": "pointer",
                                "whiteSpace": "nowrap",
                                "fontFamily": "Arial, sans-serif",
                                "flexShrink": "0",
                                "height": "72px",
                                "boxSizing": "border-box",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "flex-end",
                        "borderTop": "1px solid #e0e0e0",
                        "paddingTop": "14px",
                        "marginTop": "8px",
                    },
                ),
            ],
            style={
                "width": "360px",
                "minWidth": "360px",
                "height": "100vh",
                "display": "flex",
                "flexDirection": "column",
                "padding": "20px",
                "background": "#FAFAFA",
                "borderLeft": "1px solid #e0e0e0",
                "boxSizing": "border-box",
            },
        ),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "display": "flex",
        "height": "100vh",
        "overflow": "hidden",
        "margin": "0",
        "padding": "0",
    },
)

# navigation callback

@app.callback(
    [
        Output("page-content", "children"),
        Output("active-case", "data"),
        Output("nav-case1", "style"),
        Output("nav-case2", "style"),
        Output("nav-case3", "style"),
        Output("nav-case4", "style"),
        Output("agent-chat-history", "data"),
        Output("agent-filter-active", "data"),
    ],
    [
        Input("nav-case1", "n_clicks"),
        Input("nav-case2", "n_clicks"),
        Input("nav-case3", "n_clicks"),
        Input("nav-case4", "n_clicks"),
    ],
    [State("active-case", "data")],
)
def update_navigation(case1_clicks, case2_clicks, case3_clicks, case4_clicks, active_case):
    if active_case is None:
        active_case = "case1"

    ctx = callback_context
    if not ctx.triggered:
        selected_case = active_case
    else:
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        selected_case = {
            "nav-case1": "case1",
            "nav-case2": "case2",
            "nav-case3": "case3",
            "nav-case4": "case4",
        }.get(triggered_id, active_case)

    content_map = {
        "case1": lambda: case1_layout(df1),
        "case2": lambda: case2_layout(df2),
        "case3": lambda: case3_layout(df3),
        "case4": lambda: case4_layout(df4),
    }
    content = content_map.get(
        selected_case,
        lambda: html.Div("Coming soon", style={"padding": "40px", "color": "#888", "fontSize": "16px"}),
    )()

    styles = [
        TAB_ACTIVE_STYLE if selected_case == f"case{i}" else TAB_INACTIVE_STYLE
        for i in range(1, 5)
    ]

    return [content, selected_case, *styles, [], False]


# register callbacks 
register_case1_callbacks(app, df1)
register_case2_callbacks(app, df2)
register_case3_callbacks(app, df3)
register_case4_callbacks(app, df4)
register_agent_callbacks(app, dfs)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
