from services.lms_client import get_health, get_labs, get_scores


def handle_start() -> str:
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check system health, browse labs, and see scores.\n"
        "Use /help to see available commands."
    )


def handle_help() -> str:
    return (
        "Available commands:\n\n"
        "/start — welcome message\n"
        "/help — show this help\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab> — show per-task pass rates for a lab"
    )


def handle_health() -> str:
    result = get_health()
    if result.get("ok"):
        return "✅ Backend is up and running."
    error = result.get("error") or f"HTTP {result.get('status')}"
    return f"❌ Backend is down: {error}"


def handle_labs() -> str:
    try:
        labs = get_labs()
        if not labs:
            return "No labs found."
        lines = [f"• {lab['title']}" for lab in labs]
        return "Available labs:\n\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ Failed to fetch labs: {e}"


def handle_scores(lab: str) -> str:
    if not lab:
        return "Usage: /scores <lab>\nExample: /scores lab-04"
    try:
        scores = get_scores(lab)
        if not scores:
            return f"No scores found for '{lab}'."
        lines = [f"• {s.get('task_title', s)}: {s.get('pass_rate', '?')}%" for s in scores]
        return f"Scores for {lab}:\n\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ Failed to fetch scores: {e}"
