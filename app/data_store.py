import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"


def load_json(filename: str) -> list[dict]:
    file_path = DATA_DIRECTORY / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(filename: str, records: list[dict]) -> None:
    file_path = DATA_DIRECTORY / filename

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def get_active_notices() -> list[dict]:
    notices = load_json("notices.json")

    return [
        notice
        for notice in notices
        if notice.get("active") is True
    ]


def get_ticket(ticket_id: str, user_id: str) -> dict | None:
    tickets = load_json("tickets.json")
    requested_ticket = ticket_id.strip().upper()
    requesting_user = user_id.strip()

    for ticket in tickets:
        if (
            ticket.get("ticket_id", "").upper() == requested_ticket
            and ticket.get("user_id") == requesting_user
        ):
            return ticket

    return None


def create_ticket(
    user_id: str,
    issue: str,
    location: str,
    reported_time: str,
    category: str,
    details: str,
) -> dict:
    tickets = load_json("tickets.json")

    existing_numbers = [
        int(ticket["ticket_id"][1:])
        for ticket in tickets
        if ticket.get("ticket_id", "").startswith("T")
        and ticket["ticket_id"][1:].isdigit()
    ]

    next_number = max(existing_numbers, default=0) + 1
    ticket_id = f"T{next_number:03d}"

    new_ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "category": category,
        "issue": issue,
        "location": location,
        "reported_time": reported_time,
        "details": details,
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    tickets.append(new_ticket)
    save_json("tickets.json", tickets)

    return new_ticket


def search_staff(query: str) -> list[dict]:
    staff_members = load_json("staff.json")
    search_term = query.strip().lower()
    results = []

    for staff_member in staff_members:
        if staff_member.get("active") is not True:
            continue

        searchable_text = " ".join(
            [
                staff_member.get("name", ""),
                staff_member.get("department", ""),
                staff_member.get("role", ""),
            ]
        ).lower()

        if search_term in searchable_text:
            results.append(staff_member)

    return results


def get_active_risks() -> list[dict]:
    risks = load_json("risks.json")

    return [
        risk
        for risk in risks
        if risk.get("active") is True
    ]


def get_active_email_summaries() -> list[dict]:
    email_summaries = load_json("email_summaries.json")

    return [
        email
        for email in email_summaries
        if email.get("active") is True
    ]


def create_inquiry(
    user_id: str,
    question: str,
    category: str,
) -> dict:
    inquiries = load_json("inquiries.json")

    existing_numbers = [
        int(inquiry["inquiry_id"][1:])
        for inquiry in inquiries
        if inquiry.get("inquiry_id", "").startswith("I")
        and inquiry["inquiry_id"][1:].isdigit()
    ]

    next_number = max(existing_numbers, default=0) + 1
    inquiry_id = f"I{next_number:03d}"

    new_inquiry = {
        "inquiry_id": inquiry_id,
        "user_id": user_id,
        "question": question,
        "category": category,
        "status": "Pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    inquiries.append(new_inquiry)
    save_json("inquiries.json", inquiries)

    return new_inquiry


# ---------------------------------------------------------------------------
# Academic calendar
# ---------------------------------------------------------------------------
# The Belgium Campus calendar page embeds its data inline as a JavaScript
# object:  eventsByMonth["YYYY-MM"] = [ {title, start, end?, category}, ... ];
# We fetch the page, regex the events out, normalise them, expand multi-day
# ranges into per-day entries, and persist two JSON files in the data folder:
#   - calendar_events.json   (raw event list)
#   - calendar_by_date.json  (date -> list of events active that day)
# The chatbot reads those files to answer calendar questions. refresh_calendar
# re-fetches the page and overwrites them.

CALENDAR_URL = "https://www.belgiumcampus.ac.za/calendar/"
CALENDAR_EVENTS_FILE = "calendar_events.json"
CALENDAR_BY_DATE_FILE = "calendar_by_date.json"
CALENDAR_META_FILE = "calendar_meta.json"

CALENDAR_CATEGORY_LABELS = {
    "holiday": "Public/Student holidays",
    "campus": "Campus closed",
    "student": "Student holidays",
    "exam": "(Re)Exams & Perusals",
    "course": "Maths bridging course",
    "admin": "Admin / schedules",
    "research": "Dissertation (final)",
    "event": "Events",
    "staff": "Staff-only tasks",
}

_EVENT_RE = re.compile(
    r"\{\s*title:\s*\"((?:[^\"\\]|\\.)*)\"\s*,\s*"
    r"start:\s*\"(\d{4}-\d{2}-\d{2})\"\s*,\s*"
    r"(?:end:\s*\"(\d{4}-\d{2}-\d{2})\"\s*,\s*)?"
    r"category:\s*\"([a-zA-Z]+)\"\s*\}"
)
_MONTH_BLOCK_RE = re.compile(
    r'eventsByMonth\["(\d{4}-\d{2})"\]\s*=\s*\[(.*?)\];',
    re.DOTALL,
)

# In-memory cache so repeated tool calls do not re-read the JSON files.
_calendar_events_cache: list[dict] | None = None
_calendar_by_date_cache: dict[str, list[dict]] | None = None
# Per-process flag: the once-per-year auto-refresh check runs at most once
# per process lifetime so a stale source page or a failed fetch does not
# trigger an external request on every single query.
_calendar_year_check_done: bool = False


def _fetch_calendar_html(url: str = CALENDAR_URL, timeout: float = 30.0) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; CampusChatbotCalendarFetcher/1.0; "
            "+https://www.belgiumcampus.ac.za/calendar/)"
        ),
        "Accept": "text/html,*/*",
    }
    response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.text


def _parse_calendar_events(html: str) -> list[dict]:
    """Parse the embedded eventsByMonth JS object into a flat event list."""
    events: list[dict] = []
    seen: set[tuple] = set()

    for _month_key, body in _MONTH_BLOCK_RE.findall(html):
        for match in _EVENT_RE.finditer(body):
            title, start, end, category = match.groups()
            title = title.replace('\\"', '"').replace("\\/", "/")
            key = (title, start, end, category)
            if key in seen:
                continue
            seen.add(key)
            events.append(
                {
                    "title": title,
                    "start": start,
                    "end": end or start,
                    "category": category,
                    "category_label": CALENDAR_CATEGORY_LABELS.get(category, category),
                }
            )

    events.sort(key=lambda event: (event["start"], event["category"], event["title"]))
    return events


def _expand_calendar_by_date(events: list[dict]) -> dict[str, list[dict]]:
    """Build a date -> list of events mapping, expanding multi-day ranges."""
    by_date: dict[str, list[dict]] = {}
    for event in events:
        start = datetime.strptime(event["start"], "%Y-%m-%d").date()
        end = datetime.strptime(event["end"], "%Y-%m-%d").date()
        current = start
        while current <= end:
            by_date.setdefault(current.isoformat(), []).append(
                {
                    "title": event["title"],
                    "category": event["category"],
                    "category_label": event["category_label"],
                    "start": event["start"],
                    "end": event["end"],
                    "multi_day": event["start"] != event["end"],
                }
            )
            current += timedelta(days=1)
    return by_date


def _load_calendar_meta() -> dict:
    """Read the calendar metadata file, or return {} if it is absent/invalid."""
    path = DATA_DIRECTORY / CALENDAR_META_FILE
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_calendar_meta(meta: dict) -> None:
    """Write the calendar metadata file."""
    path = DATA_DIRECTORY / CALENDAR_META_FILE
    with path.open("w", encoding="utf-8") as file:
        json.dump(meta, file, indent=2)


def _maybe_refresh_for_new_year() -> None:
    """Refresh the stored calendar once per calendar year, automatically.

    Called from the query path. If the stored calendar was last fetched for a
    year that is not the current year, re-fetch it from the website. Runs at
    most once per process lifetime so a stale source page or a failed fetch
    cannot cause an external request on every query.
    """
    global _calendar_year_check_done
    if _calendar_year_check_done:
        return
    _calendar_year_check_done = True

    current_year = datetime.now(timezone.utc).year
    meta = _load_calendar_meta()

    if meta.get("year") == current_year:
        return

    # Stored calendar is from a different (older) year -> refresh it.
    try:
        refresh_calendar()
    except Exception:
        # Leave the check flagged as done for this process so we do not retry
        # on every query; the next process restart will retry. The stored
        # data (if any) is still served below.
        return


def refresh_calendar() -> dict:
    """Fetch the live calendar page, parse it, and store it in the data folder.

    Returns a summary dict describing what was stored. This is exposed to the
    chatbot as a tool so the calendar can be refreshed on demand.
    """
    html = _fetch_calendar_html()
    events = _parse_calendar_events(html)

    if not events:
        return {
            "success": False,
            "message": "No events were found; the calendar page layout may have changed.",
        }

    by_date = _expand_calendar_by_date(events)

    save_json(CALENDAR_EVENTS_FILE, events)
    (DATA_DIRECTORY / CALENDAR_BY_DATE_FILE).write_text(
        json.dumps(by_date, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Update the in-memory cache so later queries use the fresh data.
    global _calendar_events_cache, _calendar_by_date_cache
    _calendar_events_cache = events
    _calendar_by_date_cache = by_date

    # Record the year this calendar was fetched for, so the query path can
    # auto-refresh once per calendar year without the user asking.
    _save_calendar_meta(
        {
            "year": datetime.now(timezone.utc).year,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
            "total_events": len(events),
        }
    )

    by_category: dict[str, int] = {}
    by_month: dict[str, int] = {}
    for event in events:
        by_category[event["category"]] = by_category.get(event["category"], 0) + 1
        by_month[event["start"][:7]] = by_month.get(event["start"][:7], 0) + 1

    return {
        "success": True,
        "message": "Calendar refreshed and stored in the data folder.",
        "total_events": len(events),
        "total_dates": len(by_date),
        "first_date": events[0]["start"],
        "last_date": events[-1]["end"],
        "by_category": by_category,
        "by_month": by_month,
    }


def _ensure_calendar_loaded() -> tuple[list[dict], dict[str, list[dict]]]:
    """Load the calendar from disk.

    Automatically refreshes it once per calendar year (see
    _maybe_refresh_for_new_year) and once if the data files are missing.
    Falls back to whatever is stored on disk if a refresh is not possible.
    """
    global _calendar_events_cache, _calendar_by_date_cache

    if _calendar_events_cache is not None and _calendar_by_date_cache is not None:
        return _calendar_events_cache, _calendar_by_date_cache

    # Auto-refresh once per calendar year, and once when files are missing.
    _maybe_refresh_for_new_year()

    # refresh_calendar may have populated the cache already.
    if _calendar_events_cache is not None and _calendar_by_date_cache is not None:
        return _calendar_events_cache, _calendar_by_date_cache

    events_path = DATA_DIRECTORY / CALENDAR_EVENTS_FILE
    by_date_path = DATA_DIRECTORY / CALENDAR_BY_DATE_FILE

    if not events_path.exists() or not by_date_path.exists():
        try:
            refresh_calendar()
        except Exception:
            pass  # serve whatever is available below

    if events_path.exists() and by_date_path.exists():
        _calendar_events_cache = load_json(CALENDAR_EVENTS_FILE)
        with by_date_path.open("r", encoding="utf-8") as file:
            _calendar_by_date_cache = json.load(file)
    else:
        # No data available and the fetch failed; serve empty data so that
        # queries return a clear "no events" answer instead of crashing.
        _calendar_events_cache = []
        _calendar_by_date_cache = {}

    return _calendar_events_cache, _calendar_by_date_cache


def get_calendar_events_on_date(date: str) -> dict:
    """Return every event active on a single ISO date (YYYY-MM-DD)."""
    _events, by_date = _ensure_calendar_loaded()
    items = by_date.get(date)
    if not items:
        return {"date": date, "found": False, "message": f"No events on {date}."}
    return {"date": date, "found": True, "count": len(items), "events": items}


def get_calendar_events_in_range(start: str, end: str) -> dict:
    """Return every event active within an inclusive date range (YYYY-MM-DD)."""
    _events, by_date = _ensure_calendar_loaded()
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError as error:
        return {"found": False, "message": f"Invalid date: {error}"}

    if end_date < start_date:
        return {"found": False, "message": "end date is before start date."}

    collected: list[dict] = []
    current = start_date
    while current <= end_date:
        for event in by_date.get(current.isoformat(), []):
            collected.append({"date": current.isoformat(), **event})
        current += timedelta(days=1)

    if not collected:
        return {
            "found": False,
            "message": f"No events between {start} and {end}.",
        }
    return {
        "found": True,
        "range": [start, end],
        "count": len(collected),
        "events": collected,
    }


def search_calendar_events(keyword: str) -> dict:
    """Return events whose title contains the keyword (case-insensitive)."""
    events, _by_date = _ensure_calendar_loaded()
    term = keyword.strip().lower()
    matches = [event for event in events if term in event["title"].lower()]
    if not matches:
        return {"found": False, "message": f"No events match '{keyword}'."}
    return {"found": True, "keyword": keyword, "count": len(matches), "events": matches}


def get_calendar_categories() -> dict:
    """List the available calendar categories with their event counts."""
    events, _by_date = _ensure_calendar_loaded()
    counts: dict[str, int] = {}
    for event in events:
        counts[event["category"]] = counts.get(event["category"], 0) + 1
    categories = [
        {
            "category": slug,
            "label": label,
            "count": counts.get(slug, 0),
        }
        for slug, label in CALENDAR_CATEGORY_LABELS.items()
    ]
    return {"categories": categories}


def get_calendar_overview() -> dict:
    """High-level overview of the stored calendar: date range and per-month counts."""
    events, _by_date = _ensure_calendar_loaded()
    months: dict[str, int] = {}
    for event in events:
        months[event["start"][:7]] = months.get(event["start"][:7], 0) + 1
    return {
        "total_events": len(events),
        "first_date": events[0]["start"] if events else None,
        "last_date": events[-1]["end"] if events else None,
        "by_month": months,
    }