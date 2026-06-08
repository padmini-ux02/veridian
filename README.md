# Veridian 🛡️

> **AI-powered Fraud Detection and Prevention System** — detect and prevent fraud in SMS messages, emails, and URLs using Machine Learning, NLP, and Explainable AI.

### 📱💻 Universal Multi-Device Support
Veridian is fully optimized for both **mobile phones** and **laptops / desktops**:
- **Mobile Phones**: Enjoy a fully responsive touch-friendly layout, view real-time risk logs on the go, and use the device's **back camera** to scan physical texts, screens, or printed documents.
- **Laptops / Desktops**: Experience the high-fidelity bento-box dashboard, drag-and-drop screenshots of phishing texts for instant OCR scanning, and view interactive global analytics.

---

## ✨ Features

| Module | Capabilities |
|---|---|
| **SMS Scanner** | Spam, scam, financial fraud detection with TF-IDF + Ensemble ML |
| **Email Scanner** | Phishing, urgency, social engineering detection |
| **URL Scanner** | Phishing domain analysis, brand impersonation, entropy scoring |
| **Explainable AI** | Human-readable explanations with risk factor breakdown |
| **Premium UI** | Stunning glassmorphic design system with terminal-style interfaces |
| **AI Chat Assistant** | Intent-based fraud prevention guide |
| **User Dashboard** | Bento-box style dashboard with real-time risk analytics |
| **Admin Panel** | User management, report review, global analytics |
| **Zero-Setup DB** | Automatically uses SQLite for local dev, PostgreSQL for production |
| **Auth System** | JWT + bcrypt, RBAC (Admin / User), rate limiting |

---

## 🏗️ Tech Stack

**Frontend:** React 18 + TypeScript, Recharts, Lucide Icons, React Router  
**Backend:** Python 3.11, FastAPI, SQLAlchemy, Pydantic v2  
**Database:** PostgreSQL (production) / SQLite (local dev)  
**AI/ML:** Scikit-Learn (TF-IDF, RF, LR), NLTK, Regex ensemble  
**Auth:** JWT (python-jose), bcrypt passlib  
**DevOps:** Docker + Docker Compose, Uvicorn, Render, Vercel

---

## ☁️ Cloud Hosting & Infrastructure

The production environment is deployed 24/7 in the cloud using the following platforms:

- **[GitHub](https://github.com/padmini-ux02/veridian)** — Holds the master source code repository and triggers automatic build pipelines upon commits.
- **[Vercel](https://vercel.com/)** — Hosts the React TypeScript frontend UI, serving the fast responsive interface and loading the client-side Tesseract.js OCR camera scanner.
- **[Render](https://render.com/)** — Hosts the FastAPI Python web service backend and PostgreSQL database, running the machine learning ensemble models.

| Service | URL |
|---|---|
| **Live Demo (Web/Mobile)** | https://veridian-virid.vercel.app/ |
| Backend API | https://veridian-backend-lvke.onrender.com |
| API Docs (Swagger) | https://veridian-backend-lvke.onrender.com/docs |

---

## 🚀 Quick Start

### Option A — Docker (Local, Recommended)

```bash
git clone https://github.com/padmini-ux02/veridian.git
cd veridian
cp .env.example .env   # Edit values as needed
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend (Local) | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Option B — Local Development (Manual)

**1. Backend Setup**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start server (SQLite configured automatically for local dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend Setup (in a new terminal)**

```powershell
cd frontend
npm install
npm run dev
```

> **Note:** `npm run dev` exposes the app to your local network. Check the terminal for your Network IP (e.g. `http://192.168.1.X:5173`) to view the app on mobile!

### Default Admin Credentials

```
Email:    admin@veridian.io
Password: Admin@123456
```

> ⚠️ Change the admin password immediately in production!

---

## ☁️ Cloud Deployment Guide

### Step 1 — Backend on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect GitHub → select `padmini-ux02/veridian`
3. Configure the service:
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```
     pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
     ```
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add a **PostgreSQL** database (New → PostgreSQL → name: `veridian-db`)
5. Set environment variables in Render dashboard:

| Variable | Value |
|---|---|
| `DATABASE_URL` | *(auto-filled from linked Render DB)* |
| `SECRET_KEY` | *(generate a strong 32+ char random string)* |
| `ALLOWED_ORIGINS` | `https://veridian-virid.vercel.app` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `DEBUG` | `false` |

6. Click **Deploy** — wait ~3–5 minutes for first build (ML deps are large)

> **Note:** Render free tier **spins down after 15 minutes of inactivity** — the first request after idle takes ~30 seconds to wake up.

---

### Step 2 — Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → Import `padmini-ux02/veridian`
2. Configure the project:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add environment variable:

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://veridian-backend-lvke.onrender.com/api/v1` |

4. Click **Deploy** ✅

---

### Step 3 — Connect & Verify

After both are deployed:
1. Visit your Vercel URL: `https://veridian-virid.vercel.app`
2. Register a new account → should work (hitting Render backend)
3. Run an SMS scan → should return AI risk analysis
4. Login as admin → check admin panel
5. Verify backend health: `https://veridian-backend-lvke.onrender.com/health`

---

## 📁 Project Structure

```
fraud detection system/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI Detection Modules
│   │   │   ├── sms_detector.py
│   │   │   ├── email_detector.py
│   │   │   ├── url_detector.py
│   │   │   ├── explainer.py
│   │   │   └── chat_assistant.py
│   │   ├── models/          # SQLAlchemy ORM Models
│   │   ├── schemas/         # Pydantic Validation Schemas
│   │   ├── routers/         # FastAPI Route Handlers
│   │   ├── services/        # Business Logic Layer
│   │   ├── middleware/       # Rate Limiting, Logging
│   │   ├── utils/           # Security, Validators
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # DB Engine & Sessions
│   │   └── main.py          # FastAPI Application
│   ├── alembic/             # Database Migrations
│   ├── render.yaml          # Render Blueprint (cloud deploy)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # Route Page Components
│   │   ├── components/      # Reusable UI Components
│   │   ├── context/         # Auth & Theme Context
│   │   ├── services/        # Axios API Client
│   │   ├── types/           # TypeScript Interfaces
│   │   └── index.css        # Design System
│   └── vercel.json          # Vercel deployment config
│
├── .env.example
├── docker-compose.yml
└── setup.ps1                # Windows Setup Script
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login & get JWT |
| GET | `/api/v1/auth/me` | Get profile |
| PUT | `/api/v1/auth/me` | Update profile |
| POST | `/api/v1/auth/change-password` | Change password |

### Fraud Detection
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/scan/analyze` | Run AI fraud scan |
| GET | `/api/v1/scan/history` | Get scan history |
| GET | `/api/v1/scan/stats` | User statistics |
| GET | `/api/v1/scan/{id}` | Get scan detail |

### Chat & Reports
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat/` | AI assistant message |
| POST | `/api/v1/reports/` | Submit fraud report |
| GET | `/api/v1/reports/my-reports` | My reports |

### Admin (Admin role only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/admin/dashboard` | Global stats |
| GET | `/api/v1/admin/users` | All users |
| PUT | `/api/v1/admin/users/{id}/toggle-status` | Activate/deactivate |
| GET | `/api/v1/admin/reports` | All reports |
| PUT | `/api/v1/admin/reports/{id}` | Update report status |

---

## 🧠 AI Model Architecture

Each detector uses an **ensemble approach**:

1. **Rule-based layer** — fast regex pattern matching for known fraud signatures  
2. **TF-IDF + ML layer** — trained on labeled spam/fraud datasets  
3. **Feature engineering** — extracts urgency indicators, financial keywords, URL patterns  
4. **Score fusion** — weighted combination of rule + ML scores  
5. **Explainer** — generates human-readable reasons for each decision

**Risk Categories:**
- 🟢 **Low** (0–30) — Safe content
- 🟡 **Medium** (30–50) — Treat with caution
- 🔴 **High** (50–75) — Likely fraud
- 🚨 **Critical** (75–100) — Definite fraud

---

## 🛡️ Security Features

- **JWT Authentication** with configurable expiry
- **bcrypt password hashing** (12 rounds)
- **Rate limiting** — 60 req/min per IP (SlowAPI)
- **Input sanitization** — HTML stripping, length limits
- **RBAC** — Admin and User roles
- **Structured logging** — correlation IDs per request
- **CORS** — configurable allowed origins
- **Security headers** — X-Frame-Options, XSS Protection, CSP (via Vercel)

---

## 🧪 Running Tests

```bash
cd backend
pip install pytest httpx
pytest app/tests/ -v
```

---

## ⚙️ Environment Variables

See `.env.example` for all available configuration options. Key variables:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/veridian_db
ALLOWED_ORIGINS=https://veridian-virid.vercel.app,http://localhost:5173
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📜 License

MIT License — Free for personal and commercial use.
