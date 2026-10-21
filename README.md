# CyberRakshak AI

CyberRakshak AI is a web-based cyber-fraud awareness and suspicious-message analysis prototype. It provides a dashboard, message analysis, a fraud-case library, analysis history, and analytics.

## Technology Stack

- **Frontend:** React, Vite, JavaScript, Recharts, Lucide React
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **API documentation:** FastAPI / Swagger UI

## Repository Structure

```text
CyberRakshakAI/
├── backend/                 # FastAPI application, API routes, services, models
│   ├── app/
│   ├── alembic/             # Database migration files
│   ├── requirements.txt
│   └── seed_frauds.py
├── Frontend/                # React + Vite frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── Data/                    # Fraud seed data used by the project
├── Docs/Diagrams/           # Project architecture and workflow diagrams
├── .env.example             # Safe environment-variable template
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or compatible version
- Node.js and npm compatible with the Vite version in `Frontend/package.json`
- PostgreSQL
- Git (for source control)

## 1. Configure the database

1. Start PostgreSQL.
2. Create a database named `cyberrakshak` (or choose another name).
3. Copy `.env.example` to `.env` in the project root.
4. Update the values in `.env` for your local PostgreSQL username, password, host, port, and database name.

Example PowerShell command from the project root:

```powershell
Copy-Item .env.example .env
```

**Never commit `.env` or share real database credentials.** Only `.env.example` belongs in GitHub.

## 2. Set up and run the backend

Open PowerShell in the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

The API documentation should be available at `http://127.0.0.1:8000/docs` while the backend is running locally.

## 3. Prepare database tables and seed data

Ensure the `.env` database settings are correct first. If tables have not yet been created, the project models can be used to create them with:

```powershell
python -c "import sys; sys.path.insert(0, 'backend'); from app import models; from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

Then, if the fraud records have not already been seeded, run:

```powershell
python backend\seed_frauds.py
```

Do not repeatedly seed data if records already exist. For an existing development database, follow the migration state and inspect the seed script before running it.

## 4. Set up and run the frontend

Open a **second** PowerShell window:

```powershell
cd Frontend
npm install
npm run dev
```

Open the local address printed by Vite (usually `http://localhost:5173`). Keep the backend running in the first terminal.

## Main application modules

- **Dashboard:** overview and statistics
- **Analyze Message:** submit text for preliminary fraud-pattern analysis
- **Fraud Cases:** browse available fraud-related information
- **History:** view saved analysis history, where available
- **Analytics:** view available fraud/risk distribution and activity information

## API endpoints

The backend includes routes for dashboard statistics, analytics, fraud records, message analysis/matching, and history. Run the backend and open `/docs` to inspect the exact available routes and request/response schemas.

## Diagrams

The `Docs/Diagrams/` folder contains the project architecture, data flow, ER diagram, and message-analysis workflow visuals for the project report.

## Important limitations and safety

- This project is a cyber-fraud awareness and preliminary message-screening prototype. Its result is not a guarantee that a message is fraudulent or safe.
- Verify financial requests through official channels. Never share OTPs, UPI PINs, passwords, or remote-access permissions.
- Do not test with real private messages or commit personal information, credentials, database dumps, virtual environments, or `node_modules`.
- Before public deployment, configure production secrets, HTTPS, database access controls, backups, and appropriate logging.

## Academic project

Prepared as a final-year project for B.Voc Software Development. Update author, institution, supervisor, and academic-year details as required before publishing project documentation.
