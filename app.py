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

# load datasets once at startup
df1 = pd.read_csv("data/case1_student_satisfaction.csv")
df2 = pd.read_csv("data/case2_teaching_methodology_performance.csv")
df3 = pd.read_csv("data/case3_social_comparison_courses.csv")
df4 = pd.read_csv("data/case4_shannon_diversity_by_methodology.csv")

# suppress_callback_exceptions needed because components are rendered
# dynamically depending on which tab is active
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# base style shared by both states, active just overrides color and border
TAB_BASE_STYLE = {
    "background": "none",
    "border": "none",
    "borderBottom": "2px solid transparent",
    "color": "#888",
    "cursor": "pointer",
    "fontSize": "14px",
    "padding": "12px 18px",
    "marginRight": "4px"
}

TAB_ACTIVE_STYLE = {
    **TAB_BASE_STYLE,
    "color": "#378ADD",
    "borderBottom": "2px solid #378ADD"
}

TAB_INACTIVE_STYLE = {
    **TAB_BASE_STYLE,
    "color": "#888",
    "borderBottom": "2px solid transparent"
}

app.layout = html.Div(
    [
        # top navigation bar
        html.Div(
            [
                html.Button("Case 1", id="nav-case1", n_clicks=0, style=TAB_ACTIVE_STYLE),
                html.Button("Case 2", id="nav-case2", n_clicks=0, style=TAB_INACTIVE_STYLE),
                html.Button("Case 3", id="nav-case3", n_clicks=0, style=TAB_INACTIVE_STYLE),
                html.Button("Case 4", id="nav-case4", n_clicks=0, style=TAB_INACTIVE_STYLE)
            ],
            style={"display": "flex", "borderBottom": "1px solid #e0e0e0", "paddingBottom": "4px", "marginBottom": "20px"}
        ),
        dcc.Store(id="active-case", data="case1"),
        html.Div(id="page-content", children=case1_layout(df1))
    ],
    style={"fontFamily": "Arial, sans-serif", "padding": "20px", "maxWidth": "1200px", "margin": ""}
)

# register all case callbacks before running
register_case1_callbacks(app, df1)
register_case2_callbacks(app, df2)
register_case3_callbacks(app, df3)
register_case4_callbacks(app, df4)


@app.callback(
    [
        Output("page-content", "children"),
        Output("active-case", "data"),
        Output("nav-case1", "style"),
        Output("nav-case2", "style"),
        Output("nav-case3", "style"),
        Output("nav-case4", "style")
    ],
    [
        Input("nav-case1", "n_clicks"),
        Input("nav-case2", "n_clicks"),
        Input("nav-case3", "n_clicks"),
        Input("nav-case4", "n_clicks")
    ],
    [State("active-case", "data")]
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
            "nav-case4": "case4"
        }.get(triggered_id, active_case)

    # render the layout for the selected case
    if selected_case == "case1":
        content = case1_layout(df1)
    elif selected_case == "case2":
        content = case2_layout(df2)
    elif selected_case == "case3":
        content = case3_layout(df3)
    elif selected_case == "case4":
        content = case4_layout(df4)
    else:
        content = html.Div(
            "Coming soon",
            style={"padding": "40px", "color": "#888", "fontSize": "16px"}
        )

    styles = [
        TAB_ACTIVE_STYLE if selected_case == "case1" else TAB_INACTIVE_STYLE,
        TAB_ACTIVE_STYLE if selected_case == "case2" else TAB_INACTIVE_STYLE,
        TAB_ACTIVE_STYLE if selected_case == "case3" else TAB_INACTIVE_STYLE,
        TAB_ACTIVE_STYLE if selected_case == "case4" else TAB_INACTIVE_STYLE
    ]

    return [content, selected_case, *styles]


if __name__ == "__main__":
    app.run(debug=True)
