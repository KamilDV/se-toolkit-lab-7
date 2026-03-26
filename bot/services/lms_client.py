import httpx
from config import LMS_API_BASE_URL, LMS_API_KEY


def _headers() -> dict:
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def get_health() -> dict:
    try:
        r = httpx.get(f"{LMS_API_BASE_URL}/health", headers=_headers(), timeout=5)
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_labs() -> list:
    r = httpx.get(f"{LMS_API_BASE_URL}/items/", headers=_headers(), timeout=10)
    r.raise_for_status()
    items = r.json()
    return [i for i in items if i.get("type") == "lab"]


def get_scores(lab: str) -> list:
    r = httpx.get(
        f"{LMS_API_BASE_URL}/analytics/task-pass-rates",
        params={"lab_title": lab},
        headers=_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
