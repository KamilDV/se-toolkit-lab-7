import httpx
from config import LMS_API_BASE_URL, LMS_API_KEY


def _headers() -> dict:
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def get_items() -> list:
    r = httpx.get(f"{LMS_API_BASE_URL}/items/", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_health() -> dict:
    try:
        items = get_items()
        return {"ok": True, "count": len(items)}
    except httpx.ConnectError as e:
        return {"ok": False, "error": f"connection refused ({LMS_API_BASE_URL}). Check that the services are running."}
    except httpx.HTTPStatusError as e:
        return {"ok": False, "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_labs() -> list:
    items = get_items()
    return [i for i in items if i.get("type") == "lab"]


def get_pass_rates(lab: str) -> list:
    r = httpx.get(
        f"{LMS_API_BASE_URL}/analytics/pass-rates",
        params={"lab": lab},
        headers=_headers(),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
