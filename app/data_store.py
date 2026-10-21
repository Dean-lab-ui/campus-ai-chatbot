import json
from datetime import datetime, timezone
from pathlib import Path


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