import httpx
import config
from services.lms_client import get_health, get_labs, get_pass_rates
from services.llm_client import route


def handle_start() -> str:
    return (
        "👋 Welcome to LMS Bot!\n\n"
        "I connect you to the LMS backend — check health, browse labs, and view scores.\n\n"
        "You can use slash commands or just ask me anything in plain language:\n"
        "• \"which lab has the lowest pass rate?\"\n"
        "• \"show me top 5 students in lab 4\"\n"
        "• \"how many students are enrolled?\"\n\n"
        "Use /help to see all slash commands."
    )


def handle_help() -> str:
    return (
        "Available commands:\n\n"
        "/start — welcome message\n"
        "/help — show this help\n"
        "/health — check backend status and item count\n"
        "/labs — list available labs\n"
        "/scores <lab> — per-task pass rates (e.g. /scores lab-04)\n\n"
        "Or just type a question in plain language and I'll figure it out!"
    )


def handle_health() -> str:
    result = get_health()
    if result.get("ok"):
        count = result.get("count", 0)
        return f"✅ Backend is healthy. {count} items available."
    error = result.get("error", "unknown error")
    return f"❌ Backend error: {error}"


def handle_labs() -> str:
    try:
        labs = get_labs()
        if not labs:
            return "No labs found in the backend."
        lines = [f"• {lab['title']}" for lab in labs]
        return "Available labs:\n\n" + "\n".join(lines)
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({config.LMS_API_BASE_URL}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_scores(lab: str) -> str:
    if not lab:
        return "Usage: /scores <lab>\nExample: /scores lab-04"
    try:
        scores = get_pass_rates(lab)
        if not scores:
            return f"No scores found for '{lab}'. Try /labs to see available lab names."
        lines = [
            f"• {s.get('task', '?')}: {s.get('avg_score', 0):.1f}% ({s.get('attempts', 0)} attempts)"
            for s in scores
        ]
        return f"Pass rates for {lab}:\n\n" + "\n".join(lines)
    except httpx.ConnectError:
        return f"❌ Backend error: connection refused ({config.LMS_API_BASE_URL}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}"
    except Exception as e:
        return f"❌ Backend error: {e}"


def handle_message(text: str) -> str:
    try:
        return route(text)
    except Exception as e:
        return f"❌ LLM error: {e}"
