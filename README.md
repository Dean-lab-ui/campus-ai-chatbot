# Campus AI Chatbot

A campus-support chatbot prototype built using Python, FastAPI, the OpenAI API, tool calling, and JSON data files.

## Live Demo

Open the deployed chatbot:

https://campus-ai-chatbot-fpjv.onrender.com/

The first load may take a short while because the free Render service sleeps when inactive.

FastAPI testing interface:

https://campus-ai-chatbot-fpjv.onrender.com/docs

## Current Features

The chatbot can:

- Display active campus notices
- Search the campus staff directory
- Check a user's support-ticket status
- Create support tickets after confirmation
- Display active campus safety risks
- Summarize recent campus emails
- Log unanswered questions as inquiries
- Remember previous messages during the current session
- Answer questions about the Belgium Campus academic calendar
- Refresh the academic calendar from the public website on demand

## How It Works

```text
Browser interface
       |
       v
FastAPI backend
       |
       +--> OpenAI API
       |
       +--> JSON data files

## Running Locally to View How Data Is Stored

Team members can run their own local copy if they want to inspect the code and watch the chatbot store tickets and inquiries.

### 1. Clone the Repository

```powershell
git clone https://github.com/harriperSoda/campus-ai-chatbot.git
cd campus-ai-chatbot
```

Because the repository is private, you must first be added as a GitHub collaborator.

### 2. Create and Activate the Python Environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the Requirements

```powershell
python -m pip install -r requirements.txt
```

### 4. Add the Project API Key

The project owner will provide the `.env` settings privately, so team members do not need to purchase their own API credits.

Create a file called `.env` in the main `campus-ai-chatbot` folder:

```env
OPENAI_API_KEY=the_private_test_key  DM ME FOR IT
OPENAI_MODEL=gpt-6-luna
```

Do not upload or commit the `.env` file to GitHub.

### 5. Start the Chatbot

```powershell
python -m uvicorn app.main:app --reload
```

Open the chatbot at:

http://127.0.0.1:8000/

The FastAPI testing page is available at:

http://127.0.0.1:8000/docs

### Viewing the Stored Data

The prototype currently stores information in JSON files inside the `data` folder:

| File | Stored information |
|---|---|
| `data/tickets.json` | Created support and security tickets |
| `data/inquiries.json` | Unanswered questions logged as inquiries |
| `data/notices.json` | Campus notices |
| `data/staff.json` | Staff-directory information |
| `data/risks.json` | Existing campus safety risks |
| `data/email_summaries.json` | Campus email summaries |
| `data/calendar_events.json` | Belgium Campus academic-calendar events (fetched from the public website) |
| `data/calendar_by_date.json` | Calendar events expanded per date, used to answer date questions |

### Testing Ticket Storage

1. Open `data/tickets.json` in VS Code.
2. Use the locally running chatbot to report a problem.
3. Give the chatbot the requested details.
4. Confirm that the ticket should be submitted.
5. Return to `data/tickets.json`.
6. The newly created ticket should now appear in the file.

### Testing Inquiry Storage

1. Ask a campus-specific question the chatbot cannot answer.
2. Confirm when the chatbot asks to log it.
3. Open `data/inquiries.json`.
4. The new inquiry should appear in the file.

### How Local Storage Works

Each team member has a separate local copy of the data.

- Local tickets only appear in that person’s `data/tickets.json`.
- Local records do not automatically appear on Render.
- Local records do not automatically upload to GitHub.
- One team member’s local records do not change another member’s files.
- The local server stops when its PowerShell window is closed.
- The separate Render deployment remains available when local computers are switched off.
