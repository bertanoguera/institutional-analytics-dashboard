"""
Per-case schemas used by both the classifier (to build prompts) and the
explain branch (to ground LLM answers in data definitions).

Each entry in CASE_SCHEMAS is a dict with:
  columns          – list of {name, type, description} dicts
  filterable       – list of {dimension, values, description} dicts
  non_filterable   – list of {dimension, reason} dicts  (shown to classifier)
  chart_note       – plain-language note about what the chart visualises
  analytical_notes – list of strings with case-specific analytical context
"""

CASE_SCHEMAS = {

    # Case 1
    "case1": {
        "title": "Student satisfaction with teaching received",
        "columns": [
            {
                "name": "Student_ID",
                "type": "string",
                "description": "Anonymised identifier for each student.",
            },
            {
                "name": "Professor_ID",
                "type": "string",
                "description": "Anonymised identifier for each professor.",
            },
            {
                "name": "Student_Gender",
                "type": "categorical",
                "description": "Gender of the student who rated the professor. Values: Female, Male.",
            },
            {
                "name": "Professor_Gender",
                "type": "categorical",
                "description": "Gender of the professor being rated. Values: Female, Male.",
            },
            {
                "name": "Faculty",
                "type": "categorical",
                "description": (
                    "Academic faculty the course belongs to. "
                    "Values: Economics, Engineering, Law, Humanities, Translation."
                ),
            },
            {
                "name": "Satisfaction_Score",
                "type": "numeric",
                "description": (
                    "Student satisfaction with teaching, rated on a 0–10 scale "
                    "(0 = completely dissatisfied, 10 = completely satisfied). "
                    "Source: UPF institutional satisfaction surveys."
                ),
            },
        ],
        "filterable": [
            {
                "dimension": "faculty",
                "values": ["Economics", "Engineering", "Law", "Humanities", "Translation"],
                "description": "Filter to show only the selected faculties in the bar chart.",
            },
            {
                "dimension": "student_gender",
                "values": ["Female", "Male"],
                "description": "Filter to show only the selected student gender group.",
            },
            {
                "dimension": "professor_gender",
                "values": ["Female", "Male"],
                "description": "Filter to show only the selected professor gender group.",
            },
        ],
        "non_filterable": [],
        "chart_note": (
            "Each bar shows the median Satisfaction_Score for a combination of "
            "professor gender and student gender, within each selected faculty. "
            "The median is the middle value when all individual scores are ranked "
            "from lowest to highest; it is more robust to extreme ratings than the mean."
        ),
        "analytical_notes": [
            (
                "Only courses that meet the RAS (Reliability Assessment System) threshold are included. "
                "This means only courses with a sufficient number of survey respondents relative to "
                "the total enrolled students pass the reliability filter."
            ),
            (
                "The chart does not imply a causal relationship between professor/student gender and "
                "satisfaction scores. Many other factors — subject difficulty, cohort characteristics, "
                "teaching style — may explain observed differences."
            ),
        ],
        "responsible_interpretation": [
            (
                "Data quality: the chart presents median satisfaction scores aggregated per professor. "
                "This gives a general overview but does not represent the satisfaction score for each "
                "professor individually — granular information is lost through aggregation."
            ),
            (
                "Visualisation type: the dot/swarm plot provides detail at the individual professor "
                "level, while the box plot gives an overview of the aggregated distribution. "
                "Both layers together give a fuller picture than either alone."
            ),
            (
                "Academic unit: each faculty operates in a different disciplinary and organisational "
                "context. Contextual characteristics of academic centres should be considered when "
                "comparing satisfaction scores across faculties."
            ),
            (
                "Gender interaction: the chart shows the interaction between professor gender and "
                "student gender. There could be a gender bias in how students evaluate professors "
                "depending on the gender combination — this should be kept in mind when interpreting "
                "differences."
            ),
        ],
    },

    # Case 2
    "case2": {
        "title": "Student performance by active teaching methodology and workload satisfaction",
        "columns": [
            {
                "name": "Course_ID",
                "type": "string",
                "description": "Anonymised identifier for each course.",
            },
            {
                "name": "Teaching_Methodology",
                "type": "categorical",
                "description": (
                    "Active teaching methodology used in the course. "
                    "LECT = Lecture, PJBL = Project-Based Learning, "
                    "PRBL = Problem-Based Learning, FLIP = Flipped Classroom, "
                    "CASE = Case Study."
                ),
            },
            {
                "name": "Weighted_Performance",
                "type": "numeric",
                "description": (
                    "Normalised weighted student performance score (0–1). "
                    "Calculated from the Spanish grading system (fail, pass, notable, excellent): "
                    "each band is assigned its midpoint value, a weighted average is computed "
                    "across all students, and the result is normalised relative to the "
                    "institutional range. It does not represent a percentage. "
                    "Approximate band ranges: Fail ≈ 0.25–0.38, Pass ≈ 0.38–0.46, "
                    "Notable ≈ 0.46–0.54, Excellent ≈ 0.54–0.60."
                ),
            },
            {
                "name": "Workload_Satisfaction",
                "type": "numeric",
                "description": (
                    "Student satisfaction with the workload of the course, rated 0–10. "
                    "Used to classify courses into top and bottom groups."
                ),
            },
            {
                "name": "Class",
                "type": "categorical",
                "description": (
                    "Workload satisfaction class of the course. "
                    "TOP = top 20% of courses by workload satisfaction score (highest-rated). "
                    "BOTTOM = bottom 20% of courses by workload satisfaction score (lowest-rated)."
                ),
            },
        ],
        "filterable": [
            {
                "dimension": "teaching_methodology",
                "values": ["LECT", "PJBL", "PRBL", "FLIP", "CASE"],
                "description": "Filter to show only the selected teaching methodologies.",
            },
        ],
        "non_filterable": [
            {
                "dimension": "class",
                "reason": (
                    "The Class variable (TOP/BOTTOM) is not filterable. "
                    "The entire point of this chart is to compare top-rated and bottom-rated courses "
                    "side by side for each methodology. Removing one class would make the comparison "
                    "meaningless. Both groups must always remain visible."
                ),
            },
        ],
        "chart_note": (
            "Each pair of bars shows the Weighted_Performance for TOP (high workload satisfaction) "
            "and BOTTOM (low workload satisfaction) courses, grouped by teaching methodology. "
            "The gap between the two bars for each methodology indicates how strongly workload "
            "satisfaction is associated with performance in that context."
        ),
        "analytical_notes": [
            (
                "These results show an association between workload satisfaction and student "
                "performance, not a causal relationship. Differences may reflect course-level "
                "factors such as subject difficulty, cohort characteristics, or learning design, "
                "not the teaching methodology alone."
            ),
            (
                "The performance gap between TOP and BOTTOM courses is widest for Lectures (LECT) "
                "and Case Studies (CASE), and narrowest for Flipped Classroom (FLIP)."
            ),
        ],
        "responsible_interpretation": [
            (
                "Data quality: student performance is a weighted average, which may lose granular "
                "information about the distribution of grades within a course."
            ),
            (
                "Visualisation type: the combination of box plots with a lollipop chart helps "
                "understand the relationship between performance, workload satisfaction, and "
                "teaching methodology across two layers of analysis."
            ),
            (
                "Learning design: learning design decisions are an important factor. The chart "
                "shows that it is not only the methodology that impacts performance — the practical "
                "implementation and workload perception also play a role."
            ),
            (
                "Student workload: the chart compares extreme cases (top 20% vs bottom 20% by "
                "workload satisfaction). Analysing extremes helps better understand the influence "
                "of perceived workload on student performance within each methodology."
            ),
            (
                "Student performance: multiple factors influence student performance simultaneously, "
                "including workload perception and teaching methodology. The chart should be read "
                "as showing associations, not causes."
            ),
        ],
    },

    # Case 3
    "case3": {
        "title": "Social comparison of courses with high LMS interaction level",
        "columns": [
            {
                "name": "Course",
                "type": "categorical",
                "description": (
                    "Identifier for the course or the institutional reference. "
                    "A, B, C = three real courses with unusually high LMS interaction. "
                    "AVG = institutional average across all courses (always shown as reference)."
                ),
            },
            {
                "name": "Indicator",
                "type": "categorical",
                "description": (
                    "The specific variable being measured. Each indicator belongs to one of "
                    "four variable groups (Student Outcomes, LMS Usage, Task Types, Social & Modality). "
                    "See analytical_notes for the full indicator list per group."
                ),
            },
            {
                "name": "Score",
                "type": "numeric",
                "description": (
                    "Normalised value of the indicator on a 0–1 scale. "
                    "Scores are normalised relative to the institutional range for that indicator, "
                    "so that indicators with very different original units can be compared on the "
                    "same axis. A score of 1.0 means the course is at the institutional maximum; "
                    "0.0 means it is at the institutional minimum."
                ),
            },
        ],
        "filterable": [
            {
                "dimension": "course",
                "values": ["A", "B", "C"],
                "description": (
                    "Select which courses to display (up to two at a time). "
                    "The institutional average (AVG) is always shown as a reference and cannot be removed."
                ),
            },
            {
                "dimension": "variable_group",
                "values": ["Student Outcomes", "LMS Usage", "Task Types", "Social & Modality"],
                "description": (
                    "Switch between the four variable groups shown in the chart tabs. "
                    "Each group contains a different set of indicators."
                ),
            },
            {
                "dimension": "indicator",
                "values": [
                    "Grades", "Workload", "Subject", "Methodology",
                    "Course_Interaction_Frequency", "Daily_Access_Frequency",
                    "Course_Interaction_Span", "Unique_AR_Indexn",
                    "AR_Interaction_Span", "AR_Interaction_Frequency",
                    "AR_First_Access_Interval",
                    "Instruction", "Preparation", "Consolidation", "Discovery",
                    "Social Classroom", "Social Group", "Social Individual",
                    "Modality Presential", "Modality Remote",
                ],
                "description": (
                    "Show ONLY the listed indicators within the active variable group. "
                    "Student Outcomes: Grades, Workload, Subject, Methodology. "
                    "Task Types: Instruction, Preparation, Consolidation, Discovery. "
                    "LMS Usage: Course_Interaction_Frequency, Daily_Access_Frequency, "
                    "Course_Interaction_Span, Unique_AR_Indexn, AR_Interaction_Span, "
                    "AR_Interaction_Frequency, AR_First_Access_Interval. "
                    "Social & Modality: Social Classroom, Social Group, Social Individual, "
                    "Modality Presential, Modality Remote."
                ),
            },
            {
                "dimension": "hide_indicator",
                "values": [
                    "Grades", "Workload", "Subject", "Methodology",
                    "Course_Interaction_Frequency", "Daily_Access_Frequency",
                    "Course_Interaction_Span", "Unique_AR_Indexn",
                    "AR_Interaction_Span", "AR_Interaction_Frequency",
                    "AR_First_Access_Interval",
                    "Instruction", "Preparation", "Consolidation", "Discovery",
                    "Social Classroom", "Social Group", "Social Individual",
                    "Modality Presential", "Modality Remote",
                ],
                "description": (
                    "Hide the listed indicators — all others in the same group remain visible. "
                    "Use this dimension (not 'indicator') when the user says 'hide X', "
                    "'remove X', or 'exclude X'. Same groups as the indicator dimension."
                ),
            },
        ],
        "non_filterable": [],
        "chart_note": (
            "Horizontal bar chart comparing up to two selected courses against the institutional "
            "average (AVG) on all indicators within the active variable group. "
            "Bars represent normalised scores (0–1); the vertical tick mark on each bar shows "
            "the institutional average for that indicator. Hover over a variable name to read "
            "its definition and original measurement scale."
        ),
        "responsible_interpretation": [
            (
                "Data quality: variables were standardised to ensure comparability across courses. "
                "Original magnitudes should be kept in mind when interpreting the chart — a score "
                "of 0.8 in one indicator does not mean the same thing in absolute terms as 0.8 in "
                "another indicator."
            ),
            (
                "Visualisation type: the chart includes several variables at once, requiring "
                "cautious analysis. Comparing courses among themselves and against the institutional "
                "average (AVG) is important for drawing meaningful conclusions."
            ),
            (
                "Learning design: each course reflects specific learning design decisions "
                "(LMS usage patterns, task types, modalities). These decisions should be considered "
                "when interpreting differences between courses."
            ),
            (
                "Student workload: workload perception is one of the variables in the chart. "
                "Its relationship with other indicators — such as grades and LMS usage — "
                "is important to explore."
            ),
            (
                "Student performance: grades are one indicator in the chart. Observing whether "
                "performance is high or low relative to the average, and how it relates to workload "
                "and engagement indicators, is central to the analysis."
            ),
        ],
        "analytical_notes": [
            (
                "Variable groups and their indicators:\n"
                "  Student Outcomes: Grades, Workload satisfaction, Subject satisfaction, Methodology satisfaction.\n"
                "  LMS Usage: Course interaction frequency, Daily access frequency, Course interaction span, "
                "Unique A/R index, A/R interaction span, A/R interaction frequency, A/R first access interval.\n"
                "  Task Types: Instruction hours, Preparation hours, Consolidation hours, Discovery hours.\n"
                "  Social & Modality: Social classroom, Social group, Social individual, "
                "Modality presential, Modality remote."
            ),
            (
                "Normalisation: each score is normalised relative to the institutional range for that "
                "specific indicator. This means a score of 0.6 in one indicator is NOT directly "
                "comparable to a score of 0.6 in a different indicator — each is relative to its "
                "own institutional benchmark. Cross-indicator comparisons should only be made against "
                "the institutional average (AVG), not against one another."
            ),
            (
                "The institutional average (AVG) is always visible and serves as the reference line. "
                "It cannot be filtered out. Indicators within each group are independent of one "
                "another: a high score on one variable does not predict scores on others."
            ),
            (
                "Key observations: Course A performs above average on grades and workload satisfaction "
                "but below average on methodology satisfaction. Course B stands out for high subject "
                "and methodology satisfaction. Course C consistently underperforms across all four "
                "Student Outcomes indicators, with workload satisfaction especially far below average."
            ),
        ],
    },

    # Case 4
    "case4": {
        "title": "Diversity of LMS tasks by teaching methodology and workload satisfaction",
        "columns": [
            {
                "name": "Teaching_Methodology",
                "type": "categorical",
                "description": (
                    "Active teaching methodology used in the course. "
                    "LECT = Lecture, PJBL = Project-Based Learning, "
                    "PRBL = Problem-Based Learning, FLIP = Flipped Classroom, "
                    "CASE = Case Study."
                ),
            },
            {
                "name": "Class",
                "type": "categorical",
                "description": (
                    "Workload satisfaction class of the course. "
                    "TOP = top 20% of courses by workload satisfaction score (highest-rated). "
                    "BOTTOM = bottom 20% of courses by workload satisfaction score (lowest-rated)."
                ),
            },
            {
                "name": "Shannon_Index",
                "type": "numeric",
                "description": (
                    "Shannon Diversity Index measuring the variety of LMS task types used in the course. "
                    "Scale: 0 (only one task type used) to 2.5 (maximum variety across all task types). "
                    "Higher values indicate a wider mix of activity types — quizzes, forums, assignments, "
                    "resources, and so on. Lower values indicate that fewer task types dominate."
                ),
            },
        ],
        "filterable": [
            {
                "dimension": "teaching_methodology",
                "values": ["LECT", "PJBL", "PRBL", "FLIP", "CASE"],
                "description": "Filter to show only the selected teaching methodologies.",
            },
        ],
        "non_filterable": [
            {
                "dimension": "class",
                "reason": (
                    "The Class variable (TOP/BOTTOM) is not filterable. "
                    "The entire point of this chart is to compare top-rated and bottom-rated courses "
                    "side by side for each methodology. Removing one class would destroy the comparison "
                    "that the chart is designed to show. Both groups must always remain visible."
                ),
            },
        ],
        "chart_note": (
            "Each pair of bars shows the Shannon_Index for TOP (high workload satisfaction) and "
            "BOTTOM (low workload satisfaction) courses, grouped by teaching methodology. "
            "A larger gap between the two bars for a given methodology indicates a stronger "
            "association between task diversity and workload satisfaction in that context."
        ),
        "analytical_notes": [
            (
                "Flipped Classroom anomaly: For FLIP courses, the BOTTOM class (low workload "
                "satisfaction) has a HIGHER Shannon_Index than the TOP class — the reverse of "
                "all other methodologies. This suggests that in flipped classroom contexts, "
                "greater variety of online tasks may be associated with increased perceived "
                "workload rather than improved workload satisfaction. This is an association, "
                "not a causal relationship."
            ),
            (
                "For all other methodologies (LECT, PJBL, PRBL, CASE), TOP courses show higher "
                "task diversity than BOTTOM courses. Project-Based Learning (PJBL) shows the "
                "largest gap between TOP and BOTTOM."
            ),
            (
                "These results show an association between task diversity and workload satisfaction, "
                "not a causal relationship. Course-level factors such as subject type, student cohort, "
                "and learning design may account for the observed patterns."
            ),
        ],
        "responsible_interpretation": [
            (
                "Data quality: the Shannon index is computed using both resources and activities "
                "together. It is not possible to distinguish whether differences come from resources, "
                "activities, or both — this is a limitation to keep in mind."
            ),
            (
                "Visualisation type: bar chart magnitudes matter here. The y-axis starts at 1.5 "
                "to make differences visible — understanding the absolute scale of the Shannon index "
                "(0 to ~2.5) is important to avoid overreading small differences."
            ),
            (
                "Learning design: teaching methodology is the primary grouping variable. The chart "
                "shows how different learning design choices relate to LMS task diversity within "
                "the two workload satisfaction groups."
            ),
            (
                "Student workload: the two groups (TOP and BOTTOM) are defined by workload "
                "satisfaction ranking. This factor is central to the chart's structure and should "
                "be considered in every comparison."
            ),
        ],
    },
}


def get_schema(case_id: str) -> dict:
    """Return the schema dict for a given case ID (e.g. 'case1')."""
    return CASE_SCHEMAS[case_id]


def get_filterable_dimensions(case_id: str) -> dict[str, list[str]]:
    """Return {dimension: [valid_values]} for filter-intent validation."""
    schema = CASE_SCHEMAS[case_id]
    return {dim["dimension"]: dim["values"] for dim in schema["filterable"]}


def get_context_block(case_id: str) -> str:
    """
    Build a plain-text context block for the explain branch.
    Includes the case title, all column definitions, filterable dimensions,
    non-filterable dimensions with their rationale, the chart note, and
    all analytical notes.
    """
    schema = CASE_SCHEMAS[case_id]
    lines = []

    lines.append(f"CASE: {case_id.upper()} — {schema['title']}")
    lines.append("")

    lines.append("COLUMNS:")
    for col in schema["columns"]:
        lines.append(f"  {col['name']} ({col['type']}): {col['description']}")
    lines.append("")

    if schema["filterable"]:
        lines.append("FILTERABLE DIMENSIONS:")
        for dim in schema["filterable"]:
            lines.append(f"  {dim['dimension']}: {', '.join(dim['values'])}")
            lines.append(f"    -> {dim['description']}")
        lines.append("")

    if schema["non_filterable"]:
        lines.append("NON-FILTERABLE DIMENSIONS:")
        for dim in schema["non_filterable"]:
            lines.append(f"  {dim['dimension']}: {dim['reason']}")
        lines.append("")

    lines.append("CHART:")
    lines.append(f"  {schema['chart_note']}")
    lines.append("")

    if schema["analytical_notes"]:
        lines.append("ANALYTICAL NOTES:")
        for i, note in enumerate(schema["analytical_notes"], 1):
            lines.append(f"  [{i}] {note}")
        lines.append("")

    if schema.get("responsible_interpretation"):
        lines.append("RESPONSIBLE INTERPRETATION FACTORS:")
        for i, note in enumerate(schema["responsible_interpretation"], 1):
            lines.append(f"  [{i}] {note}")
        lines.append("")

    return "\n".join(lines)
