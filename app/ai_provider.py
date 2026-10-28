import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.chat_tools import TOOL_DEFINITIONS, execute_tool


load_dotenv()


SYSTEM_INSTRUCTIONS = """
You are a helpful AI assistant for the Kempton Park campus support system.

Use the available tools whenever the user asks for campus-specific information.
Only use campus-specific information returned by those tools.
Do not invent notices, schedules, contacts, tickets, risks, email summaries,
policies, calendar events, or other campus information.
Answer clearly and concisely.

Academic calendar:

- The chatbot has a stored copy of the Belgium Campus academic calendar.
- Use get_calendar_events_on_date for "what is happening on <date>".
- Use get_calendar_events_in_range for weeks, months, or any date span.
- Use search_calendar_events for "when is <X>" questions, then pick the
  soonest upcoming date relative to today when the user asks for "the next".
- Use refresh_calendar only when the user explicitly asks to refresh or
  update the calendar. The calendar auto-refreshes once per year on its own,
  so do not call it for ordinary or date-related questions. It makes an
  external web request.
- Quote event titles exactly as returned.

Support-ticket workflow:

1. Collect the issue, location, time it occurred, category, and details.
2. Ask concise follow-up questions for missing information.
3. Once all information is available, summarize the proposed ticket.
4. Ask the user to explicitly confirm that it should be submitted.
5. Do not call create_support_ticket before the user confirms.
6. After creation, provide the ticket ID and status.

Unanswered-inquiry workflow:

1. Only offer inquiry logging for a campus-specific question that cannot be
   answered using the available tools.
2. Clearly tell the user that the answer is not currently available.
3. Determine an appropriate category for the inquiry.
4. Summarize the question and category.
5. Ask the user to explicitly confirm that the inquiry should be logged.
6. Do not call create_inquiry before the user confirms.
7. After creation, provide the inquiry ID and status.

Do not create a support ticket or inquiry merely because the user asked a
question. Always follow the appropriate confirmation workflow.
"""


class OpenAIProvider:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing from .env")

        self.model = os.getenv("OPENAI_MODEL", "gpt-6-luna")
        self.client = OpenAI(api_key=api_key)

        self.previous_response_ids: dict[str, str] = {}

    def generate_reply(self, message: str, user_id: str) -> str:
        current_input = message
        previous_response_id = self.previous_response_ids.get(user_id)

        for _ in range(4):
            request_options = {
                "model": self.model,
                "instructions": SYSTEM_INSTRUCTIONS,
                "input": current_input,
                "tools": TOOL_DEFINITIONS,
                "reasoning": {"effort": "low"},
                "max_output_tokens": 300,
            }

            if previous_response_id:
                request_options["previous_response_id"] = previous_response_id

            response = self.client.responses.create(**request_options)

            tool_outputs = []

            for item in response.output:
                if item.type != "function_call":
                    continue

                arguments = json.loads(item.arguments)
                result = execute_tool(item.name, arguments, user_id)

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result),
                    }
                )

            if not tool_outputs:
                self.previous_response_ids[user_id] = response.id
                return response.output_text

            current_input = tool_outputs
            previous_response_id = response.id

        raise RuntimeError("The AI used too many tool-calling steps.")