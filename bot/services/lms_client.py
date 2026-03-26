import httpx
import config


def _headers() -> dict:
    return {"Authorization": f"Bearer {config.LMS_API_KEY}"}


def _get(path: str, params: dict | None = None) -> list | dict:
    r = httpx.get(f"{config.LMS_API_BASE_URL}{path}", headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def get_items() -> list:
    return _get("/items/")


def get_health() -> dict:
    try:
        items = get_items()
        return {"ok": True, "count": len(items)}
    except httpx.ConnectError:
        return {"ok": False, "error": f"connection refused ({config.LMS_API_BASE_URL}). Check that the services are running."}
    except httpx.HTTPStatusError as e:
        return {"ok": False, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_labs() -> list:
    return [i for i in get_items() if i.get("type") == "lab"]


def get_learners() -> list:
    return _get("/learners/")


def get_scores(lab: str) -> list:
    return _get("/analytics/scores", {"lab": lab})


def get_pass_rates(lab: str) -> list:
    return _get("/analytics/pass-rates", {"lab": lab})


def get_timeline(lab: str) -> list:
    return _get("/analytics/timeline", {"lab": lab})


def get_groups(lab: str) -> list:
    return _get("/analytics/groups", {"lab": lab})


def get_top_learners(lab: str, limit: int = 5) -> list:
    return _get("/analytics/top-learners", {"lab": lab, "limit": limit})


def get_completion_rate(lab: str) -> dict:
    return _get("/analytics/completion-rate", {"lab": lab})


def trigger_sync() -> dict:
    r = httpx.post(f"{config.LMS_API_BASE_URL}/pipeline/sync", headers=_headers(), json={}, timeout=30)
    r.raise_for_status()
    return r.json()
