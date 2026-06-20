# 🚀 VivaSaarthi Backend

Welcome to the **VivaSaarthi Backend**! This is the core API and real-time engine that powers the AI-driven Mock Interview platform. It is built using a modern Python stack with Flask, PostgreSQL, and WebSockets, deeply integrated with DeepSeek and Gemini for intelligent, real-time feedback and behavioral analysis.

---

## 🛠️ Tech Stack

- **Framework**: Flask
- **Database**: PostgreSQL (Hosted on Supabase) & SQLAlchemy (ORM)
- **Real-Time Communication**: Flask-SocketIO (with `gevent` & WebSockets)
- **Authentication**: JWT (JSON Web Tokens stored securely in cookies)
- **AI Integrations**: 
  - DeepSeek API (For conversational interview generation & grading)
  - Google Gemini Vision (For video/webcam behavioral analysis)

---

## 🏃‍♂️ Getting Started

### 1. Prerequisites
Make sure you have **Python 3.9+** installed on your machine.

### 2. Environment Setup
Clone the repository and activate your virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries, including WebSockets and database drivers:

```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory. You will need your database connection details and API keys. Use the following template:

```env
# Supabase PostgreSQL Connection Details
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Flask Secrets
SECRET_KEY=your_super_secret_flask_key_here
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# Third-party APIs
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key
```
*(Note: If your database password contains special characters like `@`, the backend is configured to automatically URL-encode them for SQLAlchemy.)*

### 5. Initialize the Database
If this is your first time setting up the project, you need to create the database tables. Run the provided script:

```bash
python init_db.py
```
*This will create the Users, Plans, Subscriptions, Templates, and InterviewSession tables in your Supabase database.*

### 6. Run the Server
Start the Flask application with WebSocket support:

```bash
python run.py
```
The server will start at `http://localhost:5000`.

---

## 🧪 Testing the APIs

A comprehensive Postman Collection is included in the root directory: 
`VivaSaarthi_Postman_Collection.json`

### How to use Postman:
1. Import `VivaSaarthi_Postman_Collection.json` into Postman.
2. The collection uses a `{{base_url}}` variable preset to `http://localhost:5000`.
3. **Authentication**: 
   - First, run the `POST /auth/signup` or `POST /auth/login` request.
   - Upon successful login, the server sets a **JWT HttpOnly Cookie**. 
   - Postman will automatically save this cookie and attach it to all subsequent requests. You do not need to manually pass Bearer tokens!
4. You can now test protected routes like `GET /dashboard/overview` or `POST /interview/start`.

---

## 🎙️ How the Interview Flow Works

The core of VivaSaarthi is the real-time AI interview. Here is the flow from the client's perspective:

1. **Start the Session (REST API)**
   - Call `POST /interview/start` passing a `template_id`.
   - The backend creates an `InterviewSession` record in the database and returns a `session_id`.

2. **Upload CV (Optional REST API)**
   - Call `POST /interview/upload-cv` with a `.pdf` or `.docx` file in the form-data.
   - The backend extracts the text using PyPDF2/python-docx and returns the `cv_text`.

3. **Connect to WebSockets**
   - The frontend establishes a WebSocket connection to `ws://localhost:5000`.
   - The frontend emits a `start_interview` event containing the `session_id` and the extracted `cv_text` (if uploaded).
   - The backend injects the CV context into the template's system prompt (RAG) to personalize the interview.
   - The backend generates the first interview question and emits a `question` event back to the client.

3. **Answering & Video Analysis (WebSockets)**
   - The user answers via voice/text. The frontend emits an `answer` event.
   - The frontend continuously captures webcam frames and emits `receive_frame` events to the backend.

4. **Finishing the Interview**
   - When the question limit is reached (or the user emits a quit command), the backend wraps up.
   - **Gemini Vision** analyzes the batch of webcam frames for behavioral insights.
   - **DeepSeek** generates a structured JSON report containing textual feedback and numeric scores (Technical, Communication, Confidence, etc.).
   - The backend parses the JSON, saves all numeric scores and textual summaries directly to the `InterviewSession` database record, and emits the final `report` to the frontend!

---

## 📂 Directory Structure

```text
VivaSaarthi---Backend/
│
├── app/
│   ├── models/          # SQLAlchemy Database Models (User, Subscription, Session, etc.)
│   ├── routes/          # REST API Endpoints (Auth, Dashboard, Subscriptions, etc.)
│   ├── services/        # AI & Core Logic (DeepSeek, Gemini, CV parsing)
│   ├── sockets/         # WebSocket Event Handlers (Real-time interview)
│   ├── config.py        # Environment Configuration
│   └── __init__.py      # App Factory & Extension Initialization
│
├── init_db.py           # Script to create Database Tables
├── requirements.txt     # Python Dependencies
├── run.py               # Main Entry Point
└── VivaSaarthi_Postman_Collection.json # Postman API Collection
```

Enjoy building the future of AI interviews! 🚀
