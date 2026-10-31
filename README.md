# Interview API

The backend is a Flask JSON API for creating interview sessions, adding questions,
recording answers, and completing or abandoning sessions. It does not call an AI
provider; questions are supplied by the client.

## Run locally

From the project root, install the dependencies and create the database tables:

```powershell
python -m pip install -r backend\requirements.txt
python -m flask --app backend.app init-db
python -m flask --app backend.app run
```

The server listens on port `5000`. By default, SQLite stores data in the Flask
instance directory. Set `DATABASE_URL` in `backend\.env` to use another
SQLAlchemy-supported database. `CORS_ORIGINS` accepts a comma-separated list;
the default allows the Vite development server.

## Deploy on Render

The backend uses package-relative imports, so Gunicorn must load it as
`backend.app`, not as the top-level module `app`.

If the Render service's **Root Directory** is `backend`, use:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --pythonpath .. backend.app:app`

If **Root Directory** is blank and the commands run from the repository root,
use `pip install -r backend/requirements.txt` as the build command and
`gunicorn backend.app:app` as the start command.

## Endpoints

- `GET /api/health` — liveness check
- `GET /api/ready` — database connectivity check
- `GET /api/interviews?status=in_progress` — list sessions (status is optional)
- `POST /api/interviews` — create a session
- `GET /api/interviews/<id>` — read a session and its questions
- `PATCH /api/interviews/<id>` — complete or abandon a session
- `DELETE /api/interviews/<id>` — delete a session and its questions
- `POST /api/interviews/<id>/questions` — add a question
- `PATCH /api/interviews/<id>/questions/<question_id>` — submit or update an answer

Create-session example:

```json
{
  "role": "Backend Engineer",
  "experience_level": "mid-level",
  "interview_type": "technical",
  "questions": ["How do you design an idempotent API?"]
}
```

Question creation accepts `{"text": "..."}`; answer submission accepts
`{"answer": "..."}`. A session can be completed only after it has at least one
question and every question has an answer. API errors use a JSON `error` field.
