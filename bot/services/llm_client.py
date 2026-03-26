import sys
import json
from openai import OpenAI
import config
import services.lms_client as lms

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks in the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets: 0-25, 25-50, 50-75, 75-100) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission counts per day (timeline) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return (default 5)"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger an ETL sync to refresh data from the autochecker API",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SYSTEM_PROMPT = """You are an LMS assistant bot. You help users get information about labs, student scores, and performance analytics.

You have access to tools that fetch real data from the LMS backend. Always use the appropriate tool to answer questions — never make up data.

When answering:
- Be concise and friendly
- Format lists clearly
- Include relevant numbers (percentages, counts)
- If a question is ambiguous (e.g. "lab 4"), ask for clarification or assume the most likely lab identifier (e.g. "lab-04")
- If the question is a greeting or unclear, respond helpfully and describe what you can do
"""

_TOOL_MAP = {
    "get_items": lambda args: lms.get_items(),
    "get_learners": lambda args: lms.get_learners(),
    "get_scores": lambda args: lms.get_scores(args["lab"]),
    "get_pass_rates": lambda args: lms.get_pass_rates(args["lab"]),
    "get_timeline": lambda args: lms.get_timeline(args["lab"]),
    "get_groups": lambda args: lms.get_groups(args["lab"]),
    "get_top_learners": lambda args: lms.get_top_learners(args["lab"], args.get("limit", 5)),
    "get_completion_rate": lambda args: lms.get_completion_rate(args["lab"]),
    "trigger_sync": lambda args: lms.trigger_sync(),
}


def route(message: str) -> str:
    client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_API_BASE_URL)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    for _ in range(10):  # max iterations to avoid infinite loops
        response = client.chat.completions.create(
            model=config.LLM_API_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            messages.append(choice.message)

            for tc in tool_calls:
                args = json.loads(tc.function.arguments)
                print(f"[tool] LLM called: {tc.function.name}({tc.function.arguments})", file=sys.stderr)
                try:
                    result = _TOOL_MAP[tc.function.name](args)
                    result_str = json.dumps(result, ensure_ascii=False)
                    preview = result_str[:80] + "..." if len(result_str) > 80 else result_str
                    print(f"[tool] Result: {preview}", file=sys.stderr)
                except Exception as e:
                    result_str = json.dumps({"error": str(e)})
                    print(f"[tool] Error: {e}", file=sys.stderr)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_str,
                })

            print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        else:
            return choice.message.content or "No response from LLM."

    return "I couldn't complete this request after several steps. Please try a more specific question."
