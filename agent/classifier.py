import json
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
from agent.schemas import CASE_SCHEMAS, get_filterable_dimensions
from agent.tracing import trace_llm

load_dotenv()

MODEL = "gemini-flash-lite-latest"

_model: genai.GenerativeModel | None = None

def _get_model() -> genai.GenerativeModel:
    global _model
    if _model is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _model = genai.GenerativeModel(MODEL)
    return _model


# prompt builder
def _build_prompt(query: str, case_id: str) -> str:
    schema = CASE_SCHEMAS[case_id]
    lines = [
        "You are a query intent classifier for an institutional analytics data dashboard.",
        "",
        f"The user is currently viewing: {case_id.upper()} — {schema['title']}",
        "",
    ]

    filterable = schema["filterable"]
    if filterable:
        lines.append(
            "FILTERABLE DIMENSIONS "
            "(the ONLY dimensions you may include in filter params):"
        )
        for dim in filterable:
            vals = ", ".join(f'"{v}"' for v in dim["values"])
            lines.append(f'  {dim["dimension"]}: [{vals}]')
        lines.append("")

    non_filterable = schema["non_filterable"]
    if non_filterable:
        lines.append(
            "NON-FILTERABLE DIMENSIONS "
            "(queries about these MUST return explain intent):"
        )
        for dim in non_filterable:
            lines.append(f'  {dim["dimension"]}: {dim["reason"]}')
        lines.append("")

    lines += [
        "TASK:",
        "Classify the user query into one of two intents.",
        "Return ONLY a valid JSON object — no explanation, no markdown, no preamble.",
        "",
        'Intent 1 — filter: the user wants to narrow the chart to a subset of the data.',
        '  Return: {"intent": "filter", "params": {<dimension>: <value_or_list>}}',
        "  Rules:",
        "    - Only include dimensions listed under FILTERABLE DIMENSIONS.",
        "    - Only use values listed for each dimension.",
        "    - Single value: string.  Multiple values for the same dimension: list of strings.",
        "    - HIDE / EXCLUDE queries (e.g. 'hide X', 'remove X', 'exclude X', 'don't show X'):",
        "        Case 1 (faculty/gender): return ALL valid values for that dimension EXCEPT the hidden one.",
        "        Case 2 / Case 4 (methodology): return ALL valid methodology values EXCEPT the hidden one.",
        "        Case 3 (indicator): use the 'hide_indicator' dimension with the value(s) to hide.",
        "",
        'Intent 2 — explain: the user wants an explanation, definition, comparison, or description.',
        "  Also use explain for: ambiguous queries, off-topic queries,",
        "  and any query that mentions a non-filterable dimension.",
        '  Return: {"intent": "explain"}',
        "",
        "EXAMPLES:",
    ]

    lines += _examples_for_case(case_id)

    lines += [
        "",
        f'User query: "{query}"',
        "",
        "Return ONLY the JSON object.",
    ]

    return "\n".join(lines)


def _examples_for_case(case_id: str) -> list[str]:
    if case_id == "case1":
        return [
            '  Query: "show only Engineering and Law"',
            '  {"intent": "filter", "params": {"faculty": ["Engineering", "Law"]}}',
            "",
            '  Query: "filter to female students"',
            '  {"intent": "filter", "params": {"student_gender": "Female"}}',
            "",
            '  Query: "female professors, Economics and Humanities only"',
            '  {"intent": "filter", "params": {"professor_gender": "Female", "faculty": ["Economics", "Humanities"]}}',
            "",
            '  Query: "hide Economics"',
            '  {"intent": "filter", "params": {"faculty": ["Engineering", "Law", "Humanities", "Translation"]}}',
            "  (return all faculties EXCEPT the hidden one)",
            "",
            '  Query: "remove Law and Translation"',
            '  {"intent": "filter", "params": {"faculty": ["Economics", "Engineering", "Humanities"]}}',
            "",
            '  Query: "why are satisfaction scores higher in Translation?"',
            '  {"intent": "explain"}',
            "",
            '  Query: "what does median mean here?"',
            '  {"intent": "explain"}',
        ]

    if case_id in ("case2", "case4"):
        met = "teaching_methodology"
        extra_explain = (
            '  Query: "what does weighted performance mean?"'
            if case_id == "case2"
            else '  Query: "what is the Shannon Diversity Index?"'
        )
        return [
            '  Query: "show only project-based learning and flipped classroom"',
            f'  {{"intent": "filter", "params": {{"{met}": ["PJBL", "FLIP"]}}}}',
            "",
            '  Query: "lectures only"',
            f'  {{"intent": "filter", "params": {{"{met}": "LECT"}}}}',
            "",
            '  Query: "hide lectures"',
            f'  {{"intent": "filter", "params": {{"{met}": ["PJBL", "PRBL", "FLIP", "CASE"]}}}}',
            "  (return ALL valid methodologies EXCEPT the hidden one)",
            "",
            '  Query: "remove case studies and problem-based learning"',
            f'  {{"intent": "filter", "params": {{"{met}": ["LECT", "PJBL", "FLIP"]}}}}',
            "",
            '  Query: "show only the top courses"',
            '  {"intent": "explain"}',
            "  (class is non-filterable — both TOP and BOTTOM must always be visible)",
            "",
            '  Query: "remove bottom courses from the chart"',
            '  {"intent": "explain"}',
            "  (class is non-filterable — both TOP and BOTTOM must always be visible)",
            "",
            extra_explain,
            '  {"intent": "explain"}',
        ]

    if case_id == "case3":
        return [
            '  Query: "show course A and C"',
            '  {"intent": "filter", "params": {"course": ["A", "C"]}}',
            "",
            '  Query: "switch to LMS usage tab"',
            '  {"intent": "filter", "params": {"variable_group": "LMS Usage"}}',
            "",
            '  Query: "course B, task types"',
            '  {"intent": "filter", "params": {"course": "B", "variable_group": "Task Types"}}',
            "",
            '  Query: "show only preparation and discovery"',
            '  {"intent": "filter", "params": {"indicator": ["Preparation", "Discovery"]}}',
            "",
            '  Query: "task types, only instruction and consolidation"',
            '  {"intent": "filter", "params": {"variable_group": "Task Types", "indicator": ["Instruction", "Consolidation"]}}',
            "",
            '  Query: "only grades and workload"',
            '  {"intent": "filter", "params": {"indicator": ["Grades", "Workload"]}}',
            "",
            '  Query: "hide preparation"',
            '  {"intent": "filter", "params": {"hide_indicator": "Preparation"}}',
            "  (use hide_indicator — do NOT compute the complement for indicators)",
            "",
            '  Query: "remove consolidation and discovery"',
            '  {"intent": "filter", "params": {"hide_indicator": ["Consolidation", "Discovery"]}}',
            "",
            '  Query: "what does the normalization mean?"',
            '  {"intent": "explain"}',
            "",
            '  Query: "why is course C below average on grades?"',
            '  {"intent": "explain"}',
        ]

    return []


# params validation
def _validate_params(params: dict, case_id: str) -> dict:
    """Strip dimensions/values that are not in the filterable schema."""
    valid_dims = get_filterable_dimensions(case_id)
    cleaned = {}
    for dim, val in params.items():
        if dim not in valid_dims:
            continue
        valid_vals = valid_dims[dim]
        if isinstance(val, list):
            kept = [v for v in val if v in valid_vals]
            if kept:
                cleaned[dim] = kept if len(kept) > 1 else kept[0]
        elif val in valid_vals:
            cleaned[dim] = val
    return cleaned


# public API
def classify(query: str, case_id: str) -> dict:
    """
    Classify a user query for the active case.

    Returns one of:
        {"intent": "filter", "params": {dimension: value_or_list, ...}}
        {"intent": "explain"}

    Falls back to {"intent": "explain"} on any error.
    """
    prompt = _build_prompt(query, case_id)

    try:
        # wrap the Gemini call in a LangSmith trace so we can see the full
        # prompt, raw response, and parsed result in the evaluation logs
        with trace_llm("gemini_classify", {"prompt": prompt, "case_id": case_id}) as out:
            response = _get_model().generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0,
                ),
            )
            raw = response.text.strip()

            # strip markdown fences if the model adds them despite instructions
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            result = json.loads(raw)
            intent = result.get("intent")

            # log what the model returned and what we parsed from it
            out["raw_response"] = raw
            out["parsed_intent"] = intent

            if intent not in ("filter", "explain"):
                return {"intent": "explain"}

            if intent == "filter":
                params = _validate_params(result.get("params", {}), case_id)
                out["validated_params"] = params
                if not params:
                    return {"intent": "explain"}
                return {"intent": "filter", "params": params}

            return {"intent": "explain"}

    except Exception:
        return {"intent": "explain"}
