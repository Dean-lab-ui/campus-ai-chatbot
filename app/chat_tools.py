from app.data_store import (
    create_inquiry,
    create_ticket,
    get_active_email_summaries,
    get_active_notices,
    get_active_risks,
    get_calendar_categories,
    get_calendar_events_in_range,
    get_calendar_events_on_date,
    get_calendar_overview,
    get_ticket,
    refresh_calendar,
    search_calendar_events,
    search_staff,
)


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_active_notices",
        "description": (
            "Get the currently active campus notices. "
            "Use this when a user asks about announcements, notices, "
            "campus updates, closures, or maintenance."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_ticket_status",
        "description": (
            "Get a support ticket belonging to the current user. "
            "Use this when the user asks about a ticket or its status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "The support ticket ID, such as T001.",
                }
            },
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_support_ticket",
        "description": (
            "Create a new support ticket for the current user. "
            "Only use this after collecting all required information "
            "and receiving the user's explicit confirmation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "issue": {
                    "type": "string",
                    "description": "A short description of the problem.",
                },
                "location": {
                    "type": "string",
                    "description": "Where the problem occurred.",
                },
                "reported_time": {
                    "type": "string",
                    "description": "When the problem occurred.",
                },
                "category": {
                    "type": "string",
                    "description": (
                        "The appropriate category, such as IT, "
                        "Facilities, Security, Library, or Administration."
                    ),
                },
                "details": {
                    "type": "string",
                    "description": "Additional useful details about the problem.",
                },
            },
            "required": [
                "issue",
                "location",
                "reported_time",
                "category",
                "details",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_staff",
        "description": (
            "Search the active campus staff directory by a person's name, "
            "department, role, or type of assistance required."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "What the user needs help with, such as registration, "
                        "IT support, or library assistance."
                    ),
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_active_risks",
        "description": (
            "Get the currently active campus safety risks and alerts. "
            "Use this when a user asks about hazards, safety concerns, "
            "risk alerts, or dangerous campus conditions."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_active_email_summaries",
        "description": (
            "Get summaries of recent active campus emails. "
            "Use this when a user asks about recent campus emails, "
            "email announcements, or important email updates."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "create_inquiry",
        "description": (
            "Log a campus-related question that could not be answered. "
            "Only use this after explaining that the answer is unavailable "
            "and receiving the user's explicit confirmation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The unanswered campus-related question.",
                },
                "category": {
                    "type": "string",
                    "description": (
                        "The inquiry category, such as Academic, IT, "
                        "Facilities, Library, Security, or Administration."
                    ),
                },
            },
            "required": ["question", "category"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "refresh_calendar",
        "description": (
            "Fetch the latest Belgium Campus academic calendar from the "
            "public website and store it in the data folder for the chatbot "
            "to use. Use this when the user asks to refresh, update, or "
            "re-download the calendar, or when calendar data appears missing "
            "or out of date. This makes an external web request."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_calendar_events_on_date",
        "description": (
            "Get every event active on a single calendar date. "
            "Use this when the user asks what is happening on a specific day."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "ISO date YYYY-MM-DD.",
                }
            },
            "required": ["date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_calendar_events_in_range",
        "description": (
            "Get every event active within an inclusive date range. "
            "Use this when the user asks about a week, month, or any span "
            "of dates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "start": {
                    "type": "string",
                    "description": "ISO date YYYY-MM-DD.",
                },
                "end": {
                    "type": "string",
                    "description": "ISO date YYYY-MM-DD.",
                },
            },
            "required": ["start", "end"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_calendar_events",
        "description": (
            "Search the academic calendar by keyword in the event title "
            "(case-insensitive). Use this for 'when is X' questions, such "
            "as 'when is the next Open Day' or 'when do exams start'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Word or phrase to search for in event titles.",
                }
            },
            "required": ["keyword"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_calendar_categories",
        "description": (
            "List the available academic-calendar event categories with their "
            "counts. Use this when the user asks what kinds of calendar "
            "events exist."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_calendar_overview",
        "description": (
            "Get a high-level overview of the stored academic calendar: date "
            "range and per-month event counts. Use this when the user asks "
            "for a summary of the calendar or what period it covers."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def execute_tool(
    tool_name: str,
    arguments: dict,
    user_id: str,
):
    if tool_name == "get_active_notices":
        return get_active_notices()

    if tool_name == "get_ticket_status":
        ticket = get_ticket(
            ticket_id=arguments["ticket_id"],
            user_id=user_id,
        )

        if ticket is None:
            return {
                "found": False,
                "message": "No accessible ticket was found with that ID.",
            }

        return {
            "found": True,
            "ticket": ticket,
        }

    if tool_name == "create_support_ticket":
        return create_ticket(
            user_id=user_id,
            issue=arguments["issue"],
            location=arguments["location"],
            reported_time=arguments["reported_time"],
            category=arguments["category"],
            details=arguments["details"],
        )

    if tool_name == "search_staff":
        matches = search_staff(arguments["query"])

        if not matches:
            return {
                "found": False,
                "message": "No active staff contact matched that search.",
            }

        return {
            "found": True,
            "staff": matches,
        }

    if tool_name == "get_active_risks":
        return get_active_risks()

    if tool_name == "get_active_email_summaries":
        return get_active_email_summaries()

    if tool_name == "create_inquiry":
        return create_inquiry(
            user_id=user_id,
            question=arguments["question"],
            category=arguments["category"],
        )

    if tool_name == "refresh_calendar":
        return refresh_calendar()

    if tool_name == "get_calendar_events_on_date":
        return get_calendar_events_on_date(date=arguments["date"])

    if tool_name == "get_calendar_events_in_range":
        return get_calendar_events_in_range(
            start=arguments["start"],
            end=arguments["end"],
        )

    if tool_name == "search_calendar_events":
        return search_calendar_events(keyword=arguments["keyword"])

    if tool_name == "get_calendar_categories":
        return get_calendar_categories()

    if tool_name == "get_calendar_overview":
        return get_calendar_overview()

    raise ValueError(f"Unknown tool: {tool_name}")