import pandas as pd

# maps the display-name values used in the classifier schema to the internal
# keys that the case3-active-tab dcc.Store expects
_VARIABLE_GROUP_TO_TAB = {
    "Student Outcomes": "outcomes",
    "LMS Usage":        "lms",
    "Task Types":       "tasks",
    "Social & Modality": "social",
}

# maps each indicator name to the tab it belongs to (for auto-tab detection)
_INDICATOR_TO_TAB = {
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


def apply_filters(params: dict, case_id: str, df: pd.DataFrame) -> dict:
    """
    Apply validated filter params to the dataframe for the given case.

    Returns a dict with:
        "df"            – filtered DataFrame (cases 1, 2, 4) or the original
                          DataFrame unchanged (case 3, where the chart is
                          driven by stores rather than a filtered df).
        "store_updates" – dict of logical key -> value for cases where filters
                          must be applied by updating dcc.Store components
                          rather than by filtering the dataframe directly.
                          Keys for case 3: "courses" (list[str]), "tab" (str).
                          Empty for all other cases.
    """
    if case_id == "case1":
        return _filter_case1(params, df)
    if case_id == "case2":
        return _filter_case2(params, df)
    if case_id == "case3":
        return _filter_case3(params, df)
    if case_id == "case4":
        return _filter_case4(params, df)
    # unknown case — pass through unchanged
    return {"df": df, "store_updates": {}}


# per-case helpers
def _filter_case1(params: dict, df: pd.DataFrame) -> dict:
    result = df.copy()

    if "faculty" in params:
        faculty = params["faculty"]
        if isinstance(faculty, str):
            faculty = [faculty]
        result = result[result["Faculty"].isin(faculty)]

    if "student_gender" in params:
        result = result[result["Student_Gender"] == params["student_gender"]]

    if "professor_gender" in params:
        result = result[result["Professor_Gender"] == params["professor_gender"]]

    return {"df": result, "store_updates": {}}


def _filter_case2(params: dict, df: pd.DataFrame) -> dict:
    result = df.copy()

    if "teaching_methodology" in params:
        methods = params["teaching_methodology"]
        if isinstance(methods, str):
            methods = [methods]
        result = result[result["Teaching_Methodology"].isin(methods)]

    return {"df": result, "store_updates": {}}


def _filter_case3(params: dict, df: pd.DataFrame) -> dict:
    store_updates = {}

    if "course" in params:
        courses = params["course"]
        if isinstance(courses, str):
            courses = [courses]
        # cap at 2 because the UI for this case only supports showing at most two courses at once
        store_updates["courses"] = courses[:2]

    if "variable_group" in params:
        tab_key = _VARIABLE_GROUP_TO_TAB.get(params["variable_group"])
        if tab_key:
            store_updates["tab"] = tab_key

    if "indicator" in params:
        indicators = params["indicator"]
        if isinstance(indicators, str):
            indicators = [indicators]
        store_updates["indicators"] = {"mode": "show", "items": indicators}
        # auto-switch to the correct tab when only indicators are specified
        if "tab" not in store_updates:
            for ind in indicators:
                tab = _INDICATOR_TO_TAB.get(ind)
                if tab:
                    store_updates["tab"] = tab
                    break

    if "hide_indicator" in params:
        indicators = params["hide_indicator"]
        if isinstance(indicators, str):
            indicators = [indicators]
        store_updates["indicators"] = {"mode": "hide", "items": indicators}
        # auto switch to the tab the hidden indicator belongs to
        if "tab" not in store_updates:
            for ind in indicators:
                tab = _INDICATOR_TO_TAB.get(ind)
                if tab:
                    store_updates["tab"] = tab
                    break

    # the case3 dataframe is not filtered: _build_figure in the existing
    # callback reads Course == "A"/"B"/"C"/"AVG" directly from the full df
    return {"df": df, "store_updates": store_updates}


def _filter_case4(params: dict, df: pd.DataFrame) -> dict:
    result = df.copy()

    if "teaching_methodology" in params:
        methods = params["teaching_methodology"]
        if isinstance(methods, str):
            methods = [methods]
        result = result[result["Teaching_Methodology"].isin(methods)]

    return {"df": result, "store_updates": {}}
