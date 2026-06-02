import os
import google.generativeai as genai
from dotenv import load_dotenv
from agent.schemas import get_context_block
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


def _build_prompt(
    query: str,
    case_id: str,
    data_summary: str = "",
    recent_history: list | None = None,
) -> str:
    context = get_context_block(case_id)

    # format recent conversation turns as context (excluding thinking dots)
    history_block = ""
    if recent_history:
        lines = ["RECENT CONVERSATION (for context, do not repeat it verbatim):"]
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            text = msg.get("text", "").strip()
            if text:
                lines.append(f"  {role}: {text}")
        history_block = "\n".join(lines) + "\n\n"

    # precomputed data values to ground factual answers
    data_block = ""
    if data_summary:
        data_block = f"{data_summary}\n\n"

    return (
        "You are an assistant helping a non-technical user understand an institutional analytics data dashboard in a learning analytics context.\n"
        "Answer the user's question using ONLY the context provided below.\n"
        "Write in plain language, no jargon, no bullet points, no markdown formatting.\n"
        "Be concise: 2–4 sentences is ideal unless the question genuinely needs more.\n"
        "When citing specific numbers, use the DATA VALUES section, do not invent figures.\n"
        "If the question cannot be answered from the context, say so briefly.\n"
        "\n"
        "DASHBOARD CONTEXT:\n"
        f"{context}\n"
        f"{data_block}"
        f"{history_block}"
        "USER QUESTION:\n"
        f"{query}\n"
        "\n"
        "Answer:"
    )


def explain(
    query: str,
    case_id: str,
    data_summary: str = "",
    recent_history: list | None = None,
) -> str:
    """
    Answer a user question grounded in the case schema, data values, and
    recent conversation history.  Returns a plain-language string, or a
    fallback message on any error.
    """
    try:
        prompt = _build_prompt(query, case_id, data_summary, recent_history)

        # wrap the Gemini call so the full prompt and response are visible in LangSmith
        with trace_llm("gemini_explain", {"prompt": prompt, "case_id": case_id}) as out:
            response = _get_model().generate_content(prompt)
            answer = response.text.strip()
            out["response"] = answer
            return answer

    except Exception as e:
        return f"Sorry, I could not generate a response right now. ({type(e).__name__})"
