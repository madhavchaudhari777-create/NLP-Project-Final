<<<<<<< HEAD
# Adaptive AI Interview Platform

## Project Title
**Adaptive AI Interview Platform** — NLP-Powered Technical Mock Interview System

## Assigned Problem Statement
Build an NLP-based technical interview platform that dynamically adapts questions based on candidate responses, evaluates answers using Generative AI/LLMs with local fallback, and provides multi-dimensional feedback with persistent student dashboards and teacher review portals.

## Objectives
- Implement text extraction, preprocessing, cleaning, and vectorization of unstructured interview data (CO1)
- Evaluate student answers using sentiment analysis, information extraction, and LLM-based scoring (CO2)
- Apply topic modeling (LDA) to discover themes across interview responses (CO3)
- Integrate OpenAI GPT models with prompt engineering for answer evaluation, with local NLP fallback (CO4)
- Provide student dashboards, teacher review portals, and interview performance reports

## Technologies
- **Backend:** Flask 3.1.2, Python 3.13, SQLite
- **NLP:** NLTK (VADER sentiment, stemming, lemmatization), scikit-learn (LDA, TF-IDF), sentence-transformers
- **LLM:** OpenAI GPT-4o-mini with structured Pydantic output
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (SPA)
- **Data:** Apache Parquet dataset (ASAG 2024 student answers)

## Methodology
1. **Data Preprocessing:** Load raw ASAG 2024 dataset → remove missing/empty records → deduplicate → save cleaned parquet → TF-IDF vectorization
2. **Question Bank:** Role-specific technical questions tagged by difficulty (Beginner/Intermediate/Advanced) and skills
3. **Adaptive Interview:** Dialogue Manager adjusts difficulty based on answer scores (>=8 increases, <5 decreases)
4. **Answer Evaluation:** OpenAI LLM with detailed prompt template → structured JSON output (correctness, relevance, completeness, clarity, score, feedback) → local rule-based + semantic similarity fallback if API unavailable
5. **NLP Processing:** Text cleaning, tokenization, keyword extraction, skill detection, VADER sentiment analysis, LDA topic modeling

## Architecture
```
Browser (SPA)
    │
    ├─► Flask Backend (REST API)
    │     ├─► QuestionService (question bank + skill matching)
    │     ├─► InterviewService (orchestration + adaptive flow)
    │     ├─► LLMEvaluator (OpenAI GPT-4o-mini evaluation)
    │     ├─► LocalEvaluator (rule-based + semantic fallback)
    │     ├─► NLPProcessor (sentiment, skills, topics, TF-IDF)
    │     ├─► DialogueManager (difficulty adaptation)
    │     └─► SQLite (users, interviews, answers)
    │
    └─► Index.html (single-page application)
```

## Installation & Execution

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd NLP-Project-Final-main

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Add your OpenAI API key to .env (optional - local fallback works without it)

# Run the application
python run.py
```

### Access
Open `http://127.0.0.1:5000` in your browser.

### Features
- **Candidate Setup:** Name, role, skills, difficulty, session length
- **Live Interview:** Adaptive questions with real-time evaluation
- **Evaluation Display:** Score, competency breakdown, sentiment, TF-IDF similarity, strengths/improvements
- **Student Dashboard:** Interview history, competency averages
- **Teacher Portal:** Class analytics, student roster, topic modeling (LDA)
- **Report Modal:** Detailed interview performance reports

## Course Outcomes Mapping

| CO | Outcome | Implementation |
|----|---------|----------------|
| CO1 | Text extraction, preprocessing, cleaning & vectorization | `preprocess_dataset.py`, `/api/dataset/stats`, TF-IDF vectorizer (`dataset/vectorized/`) |
| CO2 | Sentiment analysis & information extraction | `NLPProcessor.analyze_sentiment()` (VADER), `extract_skills()`, `extract_keywords()`, displayed in evaluation UI |
| CO3 | Topic modeling | `NLPProcessor.extract_topics_lda()` (LDA), `/api/teacher/topics` endpoint |
| CO4 | GenAI/LLM integration & prompt engineering | `LLMEvaluator` with OpenAI GPT-4o-mini, structured prompt template, local fallback |

## Dataset Details
- **Source:** ASAG 2024 (Automatic Short Answer Grading)
- **File:** `dataset/asag2024/train.parquet`
- **Preprocessing:** Removed missing/empty questions/answers, removed exact duplicates, saved to `dataset/processed/asag2024_cleaned.parquet`
- **Vectorization:** TF-IDF matrix saved to `dataset/vectorized/answers_tfidf.npz` with `tfidf_vectorizer.pkl`

## Project Structure
```
NLP-Project-Final-main/
├── app/
│   ├── __init__.py          # Flask app factory
├── auth.py                  # Authentication
├── db.py                    # SQLite database layer
├── routes.py                # REST API endpoints
├── ai/
│   ├── dialogue_manager.py  # Adaptive difficulty logic
├── llm_evaluator.py         # OpenAI GPT evaluation
├── local_evaluator.py       # Rule-based + semantic fallback
├── nlp_processor.py         # Sentiment, skills, LDA topics
├── semantic_evaluator.py    # Dense vector similarity
├── services/
│   ├── question_service.py  # Role/skill question bank
│   ├── interview_service.py # Interview orchestration
│   └── report_service.py    # Performance reports
├── templates/
│   └── index.html           # Single-page frontend
├── dataset/
│   ├── asag2024/            # Raw dataset
│   ├── processed/           # Cleaned parquet files
│   └── vectorized/          # TF-IDF vectors
├── preprocess_dataset.py    # Data preprocessing script
├── evaluate_similarity.py   # TF-IDF vs grade correlation
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (local, not committed)
└── .env.example             # Environment template
```

## Deliverables
- ✅ Working source code with organized folders
- ✅ README.md with overview, objectives, technologies, methodology, architecture, installation instructions
- ✅ Live application (deploy separately)
- ✅ Output screenshots (capture during demonstration)
- ✅ Dataset details documented above
- ⬜ Project Poster (one page)
- ⬜ AWS NLP Lab Certificate (separate 20-mark component)
=======
# Adaptive AI Technical Interview Platform
> **An Intelligent, Adaptive Mock Technical Interview Platform powered by Natural Language Processing (NLP), Dense Semantic Embeddings, and Large Language Models (LLMs).**

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![NLP](https://img.shields.io/badge/NLP-Transformers%20%7C%20Scikit--Learn-green.svg)](https://huggingface.co/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-108%20Passing-brightgreen.svg)]()

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Capabilities & Features](#-key-capabilities--features)
3. [Deep Dive: Natural Language Processing (NLP) Architecture](#-deep-dive-natural-language-processing-nlp-architecture)
4. [System Architecture & Multi-Tier Evaluation](#-system-architecture--multi-tier-evaluation)
5. [User Roles & Dashboard Portals](#-user-roles--dashboard-portals)
6. [Technology Stack](#-technology-stack)
7. [Project Directory Structure](#-project-directory-structure)
8. [Installation & Getting Started](#-installation--getting-started)
9. [Database & Persistence Schema](#-database--persistence-schema)
10. [Automated Testing Suite](#-automated-testing-suite)
11. [Project Changelog & Recent Updates](#-project-changelog--recent-updates)

---

## 🚀 Project Overview

The **Adaptive AI Technical Interview Platform** is a web-based educational system engineered to simulate realistic technical coding and engineering interviews. Unlike conventional static quiz tools, this platform utilizes:
- **Adaptive Dialogue Management:** Dynamically modifies question difficulty (Beginner $\leftrightarrow$ Intermediate $\leftrightarrow$ Advanced) based on the candidate's real-time answer performance.
- **Hybrid Multi-Dimensional NLP Evaluation:** Grades technical explanations across four distinct competencies: **Correctness**, **Relevance**, **Completeness**, and **Clarity**.
- **Dense Vector Semantic Embeddings (Enhancement 1):** Utilizes transformer models (`sentence-transformers/all-MiniLM-L6-v2`) and statistical N-gram TF-IDF vectorizers to accurately measure conceptual alignment, overcoming the limitations of traditional keyword matching.
- **Academic Reviewer / Teacher Portal:** Enables educators to audit class-wide performance, inspect question-by-question student transcripts, and monitor skill progression.

---

## ✨ Key Capabilities & Features

- **⚡ Adaptive Question Progression:** The dialogue manager assesses each answer and dynamically selects subsequent questions at higher or lower difficulty tiers based on candidate aptitude.
- **🎯 Multi-Dimensional Evaluation:** Every answer receives granular scores (0–10) across:
  - **Correctness:** Technical accuracy and theoretical validity.
  - **Relevance:** Precision in directly answering the prompt.
  - **Completeness:** Depth of explanation, edge cases, and trade-off considerations.
  - **Clarity:** Structural coherence, conciseness, and readability.
- **🧠 Dense Semantic Embedding Engine:** Evaluates candidate answers against gold-standard reference answers using 384-dimensional cosine vector similarity.
- **👤 Persistent User Authentication & Role-Based Access Control:**
  - **Students:** Access personal mock interview history, average score trends, and competency meters.
  - **Teachers / Reviewers:** Access class-wide analytics, filterable student roster, and granular interview audit logs.
- **🎨 Minimalist Design System:** Built with an obsidian/zinc monochrome aesthetic inspired by modern minimalist tools (Vercel, Linear, Notion), featuring interactive skill chips, difficulty selector cards, and backdrop-blurred report modals.

---

## 🔬 Deep Dive: Natural Language Processing (NLP) Architecture

### 1. The Core NLP Challenge: Synonymy & Paraphrasing
In technical interviews, candidates frequently express the correct concept using varied terminology:
- *Candidate:* "It isolates Python dependencies in an encapsulated virtual environment."
- *Reference:* "Sandboxes project packages to prevent system-wide version conflicts."

Traditional **lexical keyword matching** or basic **TF-IDF** awards minimal points because tokens do not lexically overlap.

### 2. Dense Semantic Embeddings (`all-MiniLM-L6-v2`)
To solve this, the platform incorporates **Dense Semantic Embeddings** via Sentence-Transformers:
1. Input sentences are tokenized into subwords.
2. The transformer maps sequences into a continuous 384-dimensional latent vector space:
   $$\vec{u}, \vec{v} \in \mathbb{R}^{384}$$
3. Mean pooling with attention masking creates fixed-size sentence vectors.
4. **Cosine Similarity** measures the angle between candidate vector $\vec{u}$ and reference vector $\vec{v}$:

$$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \frac{\sum_{i=1}^{n} u_i v_i}{\sqrt{\sum_{i=1}^{n} u_i^2} \sqrt{\sum_{i=1}^{n} v_i^2}}$$

### 3. Dual-Layer Offline-Resilient Vectorizer
To ensure uninterrupted operation even when running offline or in resource-constrained environments:
- **Primary Engine:** HuggingFace `AutoModel` & `AutoTokenizer` (`all-MiniLM-L6-v2`) with PyTorch tensor normalization.
- **Fallback Engine:** Sub-word character N-grams (3–4 character boundaries) combined with word unigram TF-IDF vectorization. This captures morphological variants (e.g., *generalize* $\leftrightarrow$ *generalization*, *indexes* $\leftrightarrow$ *indexing*) with zero external network overhead.

### 4. Dialogue Management State Machine
The dialogue manager (`app/ai/dialogue_manager.py`) tracks candidate state through a Markov-style adaptive policy:
- **Promotion Threshold:** Consecutive scores $\ge 7.5/10$ trigger difficulty escalation (e.g., `Beginner` $\rightarrow$ `Intermediate` $\rightarrow$ `Advanced`).
- **Demotion Policy:** Consecutive scores $< 4.5/10$ transition to foundational questions to diagnose prerequisite gaps.
- **Dynamic Pool Re-weighting:** Avoids repeat questions and balances domain coverage across candidate skills.

---

## 🏗️ System Architecture & Multi-Tier Evaluation

When a student submits an answer, the evaluation pipeline processes it through three fallback tiers:

```
[Candidate Answer] ──> [NLP Text Analysis (Tokens, Keywords, Skills)]
                                │
                                ▼
                   ┌───────────────────────────┐
                   │ Tier 1: Cloud LLM Engine  │ ──> (OpenAI GPT-4o / GPT-3.5)
                   └─────────────┬─────────────┘
                                 │ (If offline / API unavailable)
                                 ▼
                   ┌───────────────────────────┐
                   │ Tier 2: Semantic Vectors  │ ──> (all-MiniLM-L6-v2 / Hybrid TF-IDF)
                   └─────────────┬─────────────┘
                                 │ (Combined with topic rules)
                                 ▼
                   ┌───────────────────────────┐
                   │ Tier 3: Local Evaluator   │ ──> (Multi-dimensional fallback scoring)
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                     [Dialogue Manager Update]
                                 │
                                 ▼
                   [SQLite Database Persistence]
```

---

## 👥 User Roles & Dashboard Portals

| Feature / Permission | Guest | Student | Teacher / Admin |
|---|:---:|:---:|:---:|
| Take Practice Interview | ✅ | ✅ | ✅ |
| Adaptive Difficulty | ✅ | ✅ | ✅ |
| Instant Multi-Dimensional Feedback | ✅ | ✅ | ✅ |
| Personal Interview History Dashboard | ❌ | ✅ | ✅ |
| Persistent Progress Timeline & Average Score | ❌ | ✅ | ✅ |
| Class-Wide Aggregated Analytics | ❌ | ❌ | ✅ |
| Student Roster Search & Filter | ❌ | ❌ | ✅ |
| Audit Individual Student Transcripts | ❌ | ❌ | ✅ |

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, Flask 3.x (Modular Application Blueprint architecture)
- **Database:** SQLite 3 (`instance/interviews.db`) with parameterized queries and foreign key constraints
- **Natural Language Processing & Machine Learning:**
  - `transformers` & `torch`: Deep learning sentence embeddings (`all-MiniLM-L6-v2`)
  - `scikit-learn`: TF-IDF vectorization and cosine similarity
  - `nltk`: Word tokenization, stop-words filtering, and text preprocessing
  - `openai`: Multi-dimensional evaluation with structured Pydantic schemas
- **Authentication & Security:** `werkzeug.security` (PBKDF2 SHA-256 password hashing), session management
- **Frontend:** Vanilla JavaScript (ES6+), CSS3 custom properties (Design System), HTML5 semantic markup

---

## 📁 Project Directory Structure

```
NLP-Project/
├── app/
│   ├── __init__.py                 # Flask factory & database initialization
│   ├── auth.py                     # Auth helpers (@login_required, @teacher_required)
│   ├── db.py                       # SQLite database layer, migrations & CRUD queries
│   ├── routes.py                   # REST API endpoints & page routes
│   │
│   ├── ai/
│   │   ├── dialogue_manager.py     # Adaptive interview state & difficulty controller
│   │   ├── llm_evaluator.py        # OpenAI GPT evaluator with structured schema
│   │   ├── local_evaluator.py      # Rule-based & semantic fallback evaluator
│   │   ├── nlp_processor.py        # Tokenizer, skill extractor, keyword analyzer
│   │   └── semantic_evaluator.py   # Enhancement 1: Dense embeddings & cosine similarity
│   │
│   ├── services/
│   │   ├── interview_service.py    # Pipeline coordinator (NLP + AI + Dialogue)
│   │   ├── question_service.py     # Question repository & role/skill filtering
│   │   └── report_service.py       # Performance report generation & recommendations
│   │
│   └── templates/
│       └── index.html              # Minimalist Single Page Application (Auth, Dashboards, Arena)
│
├── instance/
│   └── interviews.db               # SQLite persistent database file
│
├── tests/
│   ├── test_auth_and_dashboards.py # 13 Auth, isolation, and audit tests
│   ├── test_dialogue_manager.py    # Adaptive difficulty transition tests
│   ├── test_interview_service.py   # End-to-end interview flow tests
│   ├── test_llm_evaluator.py       # OpenAI LLM integration & fallback tests
│   ├── test_local_evaluator.py     # Local scoring & reference matching tests
│   ├── test_nlp_processor.py       # NLP tokenization & extraction tests
│   ├── test_question_service.py    # Question pool filtering tests
│   ├── test_report_service.py      # Performance scorecard tests
│   ├── test_routes.py              # Endpoint integration tests (with isolated temp DB)
│   └── test_semantic_evaluator.py  # Enhancement 1 semantic embedding tests
│
├── .env                            # Environment variables & API keys
├── requirements.txt                # Project dependencies
├── TECHNICAL_ENHANCEMENTS.md       # Architectural roadmap & enhancement guides
└── README.md                       # Project documentation & reference manual
```

---

## 💻 Installation & Getting Started

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/madhavchaudhari777-create/NLP-Project.git
cd NLP-Project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
Or create/verify your `.env` file in the project root:
```env
FLASK_SECRET_KEY=your-secure-secret-key-here
OPENAI_API_KEY=your-openai-api-key-optional
DATABASE_PATH=instance/interviews.db
```
*(Note: An OpenAI API key is optional. If absent or credits expire, the system automatically falls back to the local semantic and rule-based NLP evaluator).*

### 4. Run the Application
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🗄️ Database & Persistence Schema

Data is stored locally in an embedded SQLite database (`instance/interviews.db`):

```sql
-- Users (Students and Teachers)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mock Interview Sessions
CREATE TABLE interviews (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_applied TEXT NOT NULL,
    target_skills TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('in_progress', 'completed')),
    score REAL DEFAULT 0.0,
    max_score REAL DEFAULT 0.0,
    percentage REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Question-by-Question Evaluations
CREATE TABLE interview_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id TEXT NOT NULL REFERENCES interviews(id),
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    correctness INTEGER NOT NULL,
    relevance INTEGER NOT NULL,
    completeness INTEGER NOT NULL,
    clarity INTEGER NOT NULL,
    feedback TEXT,
    strengths TEXT,
    improvements TEXT,
    evaluation_method TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧪 Automated Testing Suite

The repository includes a comprehensive automated test suite spanning unit tests, integration tests, and security/isolation tests.

To run the complete test suite:
```bash
python -m unittest discover tests
```

### Test Coverage Highlights (108 Tests Total):
- **`test_semantic_evaluator.py`:** Tests dense vector similarity, identical vs. dissimilar text differentiation, and score scaling.
- **`test_auth_and_dashboards.py`:** Tests user registration, session management, teacher audit privileges, and student data isolation.
- **`test_dialogue_manager.py`:** Tests adaptive difficulty level shifts and state tracking.
- **`test_local_evaluator.py`:** Tests rule-based keyword matching and reference coverage.
- **`test_routes.py`:** Tests all Flask API endpoints using isolated temporary test databases.

---

## 📝 Project Changelog & Recent Updates

### 🔄 Update Log
- **Enhancement 1 Implemented (`app/ai/semantic_evaluator.py`):** Added dense vector semantic embeddings using `all-MiniLM-L6-v2` transformer architecture and multi-ngram TF-IDF fallback for conceptual alignment scoring.
- **Minimalist UI Redesign:** Replaced legacy styles with an obsidian/zinc monochrome minimalist design system (responsive dual-panel auth, interactive skill tag chips, difficulty selector cards, and clean typography).
- **Authentication & Role-Based Portals:** Integrated session authentication, student dashboard with personal history, and teacher review portal with class-wide metrics.
- **Database Persistence Layer (`app/db.py`):** Implemented SQLite database storing users, interview sessions, and dimensional answer scorecards.
- **Test Suite Expansion:** Expanded test coverage to **108 passing tests** covering semantic evaluation, auth isolation, and interview persistence.

*(This README will continue to be updated after each subsequent enhancement).*
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
