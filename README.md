# Campus AI Chatbot

A working prototype of an AI-powered support chatbot for the Kempton Park Campus communication platform.

## Live Chatbot

Open the chatbot here:

https://campus-ai-chatbot-fpjv.onrender.com/

The chatbot runs on Render’s cloud server. It remains accessible when the developer’s computer, PowerShell and VS Code are switched off.

## How to Use It

1. Open the chatbot link.
2. Enter a unique demo user ID.
3. Type a message.
4. Select **Send**.

Each tester should use a different demo ID because conversation history is currently associated with the entered ID.

Examples:

```text
TEST-AMAN
TEST-DEAN
TEST-RIAN
```

Testers do not need to:

- Install Python.
- Download the project.
- Run the application locally.
- Create an OpenAI account.
- Provide an API key.

The OpenAI API key is stored securely on Render and used by the FastAPI backend.

## API Documentation

The FastAPI testing page is available at:

https://campus-ai-chatbot-fpjv.onrender.com/docs

## Health Check

The server health check is available at:

https://campus-ai-chatbot-fpjv.onrender.com/health

A working server returns:

```json
{
  "status": "healthy"
}
```

## Current Features

The chatbot can:

- Retrieve active campus notices.
- Retrieve active safety risks.
- Summarize recent campus emails.
- Search the campus staff directory.
- Check the status of support tickets.
- Prevent one user from accessing another user’s ticket.
- Collect information for a new support ticket.
- Request confirmation before creating a ticket.
- Log unanswered campus inquiries after confirmation.
- Maintain conversation context while the server is running.
- Display responses through a browser-based chat interface.

## How It Works

```text
User’s browser
      |
      v
Render cloud server
      |
      v
FastAPI /chat endpoint
      |
      v
OpenAI Responses API
      |
      v
Controlled chatbot tools
      |
      v
Mock campus JSON data
```

The AI handles the conversation and chooses an appropriate tool.

The Python backend performs the actual data operations. The AI does not have unrestricted access to the application files.

## Project Structure

```text
campus-ai-chatbot/
|
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- ai_provider.py
|   |-- chat_tools.py
|   |-- data_store.py
|   |
|   `-- static/
|       |-- index.html
|       |-- styles.css
|       `-- chat.js
|
|-- data/
|   |-- notices.json
|   |-- tickets.json
|   |-- staff.json
|   |-- risks.json
|   |-- email_summaries.json
|   `-- inquiries.json
|
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## Main Files

### `app/main.py`

Creates the FastAPI application and provides:

- The browser interface.
- The `/chat` endpoint.
- The `/health` endpoint.
- The API documentation.

### `app/ai_provider.py`

Handles:

- OpenAI API communication.
- System instructions.
- Conversation context.
- AI tool calls.
- Ticket and inquiry confirmation rules.

### `app/chat_tools.py`

Defines the functions available to the AI, including:

- Retrieving campus notices.
- Retrieving ticket information.
- Creating support tickets.
- Searching the staff directory.
- Retrieving safety risks.
- Retrieving email summaries.
- Creating unanswered inquiries.

### `app/data_store.py`

Reads and writes the current JSON mock data.

The data-access logic is kept separate so the JSON files can later be replaced with SharePoint Lists.

### `app/static/`

Contains the browser interface:

- `index.html` defines the page.
- `styles.css` controls the appearance.
- `chat.js` communicates with the `/chat` endpoint.

## Support Ticket Workflow

When a user reports a problem, the chatbot:

1. Collects the issue.
2. Requests the location.
3. Requests when the problem occurred.
4. Determines the category.
5. Collects additional details.
6. Summarizes the proposed ticket.
7. Requests confirmation.
8. Creates the ticket after confirmation.
9. Returns the ticket ID and status.

## Unanswered Inquiry Workflow

When a campus-specific question cannot be answered, the chatbot:

1. Explains that the information is unavailable.
2. Offers to log an inquiry.
3. Determines the category.
4. Summarizes the inquiry.
5. Requests confirmation.
6. Creates the inquiry after confirmation.
7. Returns the inquiry ID and status.

## Current Data

The prototype currently uses local JSON files:

| File | Purpose |
|---|---|
| `notices.json` | Campus notices |
| `tickets.json` | Support tickets |
| `staff.json` | Staff directory |
| `risks.json` | Campus safety risks |
| `email_summaries.json` | Campus email summaries |
| `inquiries.json` | Unanswered inquiries |

## Planned Integration

The final application will replace the JSON files with SharePoint Lists.

```text
Power Apps interface
        |
        v
Hosted FastAPI chatbot
        |
        +----> OpenAI API
        |
        v
Microsoft Graph
        |
        v
SharePoint Lists
        |
        +----> Power Automate workflows
        |
        `----> Power BI reporting
```

The chatbot’s existing data functions will be updated to read and write SharePoint data instead of JSON.

Power Automate will respond to SharePoint changes, such as:

- A new support ticket being created.
- A new inquiry requiring follow-up.
- A ticket requiring assignment or escalation.
- A new urgent campus alert.

## Current Limitations

- The entered user ID is not verified authentication.
- Conversation history is lost when the Render server restarts.
- Testers using the same ID may share conversation context.
- The JSON files are temporary development storage.
- Tickets and inquiries saved on Render can be lost after a restart or redeployment.
- The first request may take longer if the free Render service has been inactive.
- OpenAI API usage is charged to the maintainer’s account.

These limitations will be addressed when the chatbot is connected to authenticated users and SharePoint Lists.
