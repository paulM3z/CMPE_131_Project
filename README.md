# CampusHub

CampusHub is a FastAPI website for managing campus clubs and events.

## Fastest Setup

### 1. Open the project folder (replace YourUsername with your actual Windows username)

cd C:\Users\YourUsername\Downloads\CMPE_131_Project

### 2. Create a virtual environment

python -m venv venv

### 3. Activate it (choose your option)

Option A - Windows PowerShell:
.\venv\Scripts\Activate.ps1

Option B - Windows Command Prompt:
.\venv\Scripts\activate.bat

Option C - macOS/Linux:
source venv/bin/activate

Option D - Git Bash on Windows:
source venv/Scripts/activate

If you get a PowerShell execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### 4. Install the packages

pip install -r requirements.txt

### 5. Add sample data

python seed.py

### 6. Start the website (choose your option)

Option A - Using Python module (recommended):
python -m uvicorn app.main:app --reload

Option B - Using uvicorn directly:
uvicorn app.main:app --reload

### 7. Successful startup should look like this:

(venv) PS C:\Users\YourUsername\Downloads\CMPE_131_Project> python -m uvicorn app.main:app --reload
INFO:     Will watch for changes in these directories: ['C:\\Users\\YourUsername\\Downloads\\CMPE_131_Project']
INFO:     Uvicorn running on http://###.#.#.#:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using WatchFiles
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

### 8. Open it in your browser (Note: You can click the link above from the terminal!)

http://###.#.#.#:8000

or

http://localhost:8000

API documentation:
http://localhost:8000/api/docs

## Test Login Accounts

| Username |  Password   |
|----------|-------------|
|  admin   | admin1234   |
|  alice   | password123 |
|   bob    | password123 |

## Local Notes

- You do not need a .env file for local setup.
- The app uses SQLite by default and creates campus_events.db automatically.
- Profile photo uploads are saved under app/static/uploads/profile_photos.
- Press CTRL+C in the terminal to stop the server when you're done.
- The server only runs on your local machine (localhost/127.0.0.1) - your real IP address is never exposed.

## Run Tests

pytest tests -v

## Reset Local Data

To get a clean local database:

Remove-Item .\campus_events.db
python seed.py

## Troubleshooting

### Fatal error in launcher:
Use python -m uvicorn app.main:app --reload instead of uvicorn alone

### Activation permission error:
Run PowerShell as Administrator and execute:
Set-ExecutionPolicy RemoteSigned

### Port already in use:
Change the port: python -m uvicorn app.main:app --reload --port 8001

### Shell integration error in VS Code:
Open PowerShell directly from Windows Start Menu (not from VS Code) or use Command Prompt instead

## Project Stack

- FastAPI
- SQLAlchemy
- Jinja2
- SQLite
- Alembic
- pytest

## Main Files

- app/main.py - app startup and routes
- app/templates/ - HTML templates
- app/static/ - CSS, JavaScript, uploads
- seed.py - sample data loader
- tests/ - test suite