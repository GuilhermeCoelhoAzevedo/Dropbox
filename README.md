# 🏨 Room Scheduler App

## 🧭 Overview

**Room Scheduler** is a Flask web application that allows users to:
1. Sign in securely with **Google OAuth 2.0**.  
2. Create and manage **rooms** and **bookings**.  
3. Store all data in **Google Cloud Datastore**.  
4. Support real-time validation and dynamic booking filters.

---

## 🛠 Requirements

- **Python 3.13+**
- **Google Cloud Project** with Datastore API enabled  
- A valid **OAuth 2.0 Client ID** from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- A **service account key file** (`service-account.json`)

To install all required packages:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Before running the application, create a `.flaskenv` file in the root directory (not committed to Git).
You can use `.flaskenv.example` as a template:

```bash
# --- Flask Settings ---
FLASK_APP=application.py
FLASK_ENV=development

# --- Security ---
SECRET_KEY=replace-with-your-secret-key

# --- Google Cloud ---
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json

# --- Google OAuth 2.0 ---
GOOGLE_CLIENT_ID=replace-with-your-google-client-id
GOOGLE_CLIENT_SECRET=replace-with-your-google-client-secret
```
---

## 🚀 Running the App

After setting up your environment:

```bash
# Activate your virtual environment
source .venv/bin/activate     # macOS/Linux
# or
.venv\Scripts\activate        # Windows

# Run the app
python -m flask run
```

Once the app starts, visit:  
👉 http://127.0.0.1:5000

You’ll be prompted to log in with your Google account before accessing the system.

---

## 📂 Project Structure
```bash
RoomScheduler/
├── application/              # Main Flask application package
│   ├── static/               # CSS, JS, and assets
│   ├── templates/            # Jinja2 templates (HTML)
│   ├── __init__.py
│   ├── forms.py              # WTForms definitions
│   └── routes.py             # All Flask routes and logic
│
├── .flaskenv                 # Local environment file (ignored in .git)
├── .flaskenv.example         # Template for environment setup
├── .gitignore                # Files ignored by git
├── .app.py                   # Flask starter file
├── app.yaml                  # App general configurations
├── config.py                 # Configuration loaded from environment
├── index.yaml                # Indexes
├── README.md
├── requirements.txt          # Python dependencies
└── service-account.json      # Google service account credentials (ignored in .git)
```

---

## 🧰 Key Technologies

- **Flask** – Web framework
- **Authlib** – OAuth 2.0 authentication
- **Google Cloud Datastore** – NoSQL database
- **WTForms** – Form validation
- **Jinja2** – Template rendering

---

## 🧑‍💻 Development Notes

- .flaskenv and service-account.json should never be committed.
- Use .flaskenv.example to share configuration structure safely.
- Always activate your virtual environment before running Flask.