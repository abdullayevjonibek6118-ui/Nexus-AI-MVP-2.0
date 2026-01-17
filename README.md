
# Nexus AI (MVP)

Nexus AI is a B2B SaaS HR Tech platform for intelligent candidate screening using AI.

## Project Structure

- **frontend/**: Static files (HTML, CSS, JS) for the web interface.
- **backend/**: FastAPI application for the REST API.

## Prerequisites

- Python 3.9+
- Node.js (optional, only if you want to use a specific static server, otherwise Python can serve it)
- Gemini API Key (Get one from Google AI Studio)

## Setup & Run

### 1. Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Create virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure Environment:
   - Copy `.env.example` to `.env`
   - **IMPORTANT**: Edit `.env` and set your `GEMINI_API_KEY`.
   ```sh
   cp .env.example .env
   ```
5. Initialize Database:
   ```sh
   python app/db/init_db.py
   ```
6. Run Server:
   ```sh
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```sh
   cd ../frontend
   ```
2. You can serve the static files using any web server. For example, using Python:
   ```sh
   python -m http.server 3000
   ```
3. Open your browser to `http://localhost:3000`.

## User Journey Walkthrough

1. **Register**: Go to `http://localhost:3000/register.html` and create an account.
2. **Login**: Log in with your new credentials.
3. **Values**: You will be redirected to the **Dashboard**.
4. **Create Vacancy**: Click "Create Vacancy", fill in the details (e.g., "Python Developer"), and publish.
5. **View Vacancy**: Click on the new vacancy in the dashboard.
6. **Upload Candidate**: Click "Add Candidate". Upload a text file (or a dummy `.txt` for MVP) representing a resume.
7. **Analysis**: The system will automatically upload and trigger Gemini to analyze the resume against the vacancy.
8. **Results**: View the score, skills match, and recommendation on the **Candidate Analysis** page.

## Tech Stack

- **Frontend**: HTML5, CSS3 (Custom), Vanilla JavaScript
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **AI**: OpenRouter (Model: `google/gemini-2.0-flash-001` or compatible)
- **Integrations**: HH.ru OAuth

## New Features
- **Sidebar Navigation**: Animated styling.
- **HH.ru Login**: OAuth integration for recruiters.
- **Improved UI**: Header alignment and logo placement.
