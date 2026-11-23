import json
import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.security import check_password_hash, generate_password_hash

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance", "interviews.db")
)

DATABASE_URL = os.getenv("DATABASE_URL")


def is_postgresql(db_path=None):
    """Check if we're using PostgreSQL."""
    path = db_path or DATABASE_PATH
    return path.startswith("postgresql://") or path.startswith("postgres://")


def get_db_path(db_path=None):
    """Resolve database path from argument, Flask current_app config, or default."""
    if db_path:
        return db_path
    try:
        from flask import current_app
        if current_app and "DATABASE_PATH" in current_app.config:
            return current_app.config["DATABASE_PATH"]
    except Exception:
        pass
    return DATABASE_PATH


def get_db_connection(db_path=None):
    """Create and return a database connection with dictionary-like row access."""
    path = get_db_path(db_path)

    if is_postgresql(path):
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2-binary required for PostgreSQL. Install: pip install psycopg2-binary")

        # Parse PostgreSQL URL
        parsed = urlparse(path)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # remove leading /
            user=parsed.username,
            password=parsed.password,
        )
        conn.autocommit = False
        return conn
    else:
        # SQLite
        path = get_db_path(db_path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn


def init_db(db_path=None):
    """Initialize database tables if they do not already exist."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            if is_postgresql(conn):
                # PostgreSQL syntax
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS interviews (
                            id TEXT PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            role_applied TEXT NOT NULL,
                            target_skills TEXT NOT NULL,
                            difficulty TEXT NOT NULL,
                            total_questions INTEGER NOT NULL,
                            score REAL DEFAULT 0.0,
                            max_score REAL DEFAULT 0.0,
                            percentage REAL DEFAULT 0.0,
                            status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed')),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS interview_answers (
                            id SERIAL PRIMARY KEY,
                            interview_id TEXT NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
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
                            evaluation_method TEXT NOT NULL,
                            feedback TEXT,
                            strengths_json TEXT,
                            improvements_json TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE INDEX IF NOT EXISTS idx_interviews_user ON interviews(user_id);
                        CREATE INDEX IF NOT EXISTS idx_answers_interview ON interview_answers(interview_id);
                    """)
            else:
                # SQLite syntax
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS interviews (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        role_applied TEXT NOT NULL,
                        target_skills TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        total_questions INTEGER NOT NULL,
                        score REAL DEFAULT 0.0,
                        max_score REAL DEFAULT 0.0,
                        percentage REAL DEFAULT 0.0,
                        status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'completed')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS interview_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interview_id TEXT NOT NULL,
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
                        evaluation_method TEXT NOT NULL,
                        feedback TEXT,
                        strengths_json TEXT,
                        improvements_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_interviews_user ON interviews(user_id);
                    CREATE INDEX IF NOT EXISTS idx_answers_interview ON interview_answers(interview_id);
                """)
    finally:
        conn.close()


# ---------------- User CRUD ----------------

def create_user(name, email, password, role="student", db_path=None):
    """Register a new user with hashed password."""
    name = name.strip()
    email = email.strip().lower()
    role = role.strip().lower()

    if not name:
        raise ValueError("Name is required.")
    if not email or "@" not in email:
        raise ValueError("A valid email address is required.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if role not in ("student", "teacher", "admin"):
        raise ValueError("Role must be 'student' or 'teacher'.")

    password_hash = generate_password_hash(password)

    conn = get_db_connection(db_path)
    try:
        with conn:
            if is_postgresql(conn):
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id",
                        (name, email, password_hash, role)
                    )
                    user_id = cur.fetchone()[0]
            else:
                cursor = conn.execute(
                    "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (name, email, password_hash, role)
                )
                user_id = cursor.lastrowid
        return get_user_by_id(user_id, db_path)
    except Exception as e:
        if "UNIQUE" in str(e) or "unique" in str(e).lower():
            raise ValueError("An account with this email already exists.")
        raise
    finally:
        conn.close()


def authenticate_user(email, password, db_path=None):
    """Authenticate user with email and password. Returns user dict or None."""
    user = get_user_by_email(email, db_path)
    if not user:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def get_user_by_email(email, db_path=None):
    """Find a user by normalized email."""
    if not email:
        return None
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
                row = cur.fetchone()
                return dict(row) if row else None
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id, db_path=None):
    """Find a user by ID."""
    if user_id is None:
        return None
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, name, email, role, created_at FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT id, name, email, role, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


# ---------------- Interview CRUD ----------------

def create_interview_record(interview_id, user_id, role_applied, target_skills, difficulty, total_questions, db_path=None):
    """Create a new interview record."""
    skills_str = ", ".join(target_skills) if isinstance(target_skills, list) else str(target_skills)
    conn = get_db_connection(db_path)
    try:
        with conn:
            if is_postgresql(conn):
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO interviews (id, user_id, role_applied, target_skills, difficulty, total_questions, status)
                        VALUES (%s, %s, %s, %s, %s, %s, 'in_progress')
                        """,
                        (str(interview_id), user_id, role_applied, skills_str, difficulty, total_questions)
                    )
            else:
                conn.execute(
                    """
                    INSERT INTO interviews (id, user_id, role_applied, target_skills, difficulty, total_questions, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'in_progress')
                    """,
                    (str(interview_id), user_id, role_applied, skills_str, difficulty, total_questions)
                )
    finally:
        conn.close()


def record_interview_answer(interview_id, question_id, question_text, difficulty, student_answer, evaluation, db_path=None):
    """Save an evaluated answer in the database."""
    score = float(evaluation.get("score", 0.0))
    max_score = float(evaluation.get("max_score", 10.0))
    correctness = int(evaluation.get("correctness", 0))
    relevance = int(evaluation.get("relevance", 0))
    completeness = int(evaluation.get("completeness", 0))
    clarity = int(evaluation.get("clarity", 0))
    eval_method = str(evaluation.get("evaluation_method", "llm"))
    feedback = evaluation.get("feedback", "")
    strengths_json = json.dumps(evaluation.get("strengths", []))
    improvements_json = json.dumps(evaluation.get("improvements", []))

    conn = get_db_connection(db_path)
    try:
        with conn:
            if is_postgresql(conn):
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO interview_answers (
                            interview_id, question_id, question_text, difficulty,
                            student_answer, score, max_score, correctness, relevance,
                            completeness, clarity, evaluation_method, feedback,
                            strengths_json, improvements_json
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (str(interview_id), str(question_id), question_text, difficulty,
                         student_answer, score, max_score, correctness, relevance,
                         completeness, clarity, eval_method, feedback,
                         strengths_json, improvements_json)
                    )
            else:
                conn.execute(
                    """
                    INSERT INTO interview_answers (
                        interview_id, question_id, question_text, difficulty,
                        student_answer, score, max_score, correctness, relevance,
                        completeness, clarity, evaluation_method, feedback,
                        strengths_json, improvements_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (str(interview_id), str(question_id), question_text, difficulty,
                     student_answer, score, max_score, correctness, relevance,
                     completeness, clarity, eval_method, feedback,
                     strengths_json, improvements_json)
                )
    finally:
        conn.close()


def finalize_interview(interview_id, total_score, max_score, percentage, db_path=None):
    """Mark an interview as completed with final scores."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            if is_postgresql(conn):
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE interviews
                        SET score = %s, max_score = %s, percentage = %s,
                            status = 'completed', completed_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (float(total_score), float(max_score), float(percentage), str(interview_id))
                    )
            else:
                conn.execute(
                    """
                    UPDATE interviews
                    SET score = ?, max_score = ?, percentage = ?,
                        status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (float(total_score), float(max_score), float(percentage), str(interview_id))
                )
    finally:
        conn.close()


def get_interview_by_id(interview_id, db_path=None):
    """Fetch an interview and its candidate user info."""
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT i.*, u.name as candidate_name, u.email as candidate_email
                    FROM interviews i
                    JOIN users u ON i.user_id = u.id
                    WHERE i.id = %s
                    """,
                    (str(interview_id),)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT i.*, u.name as candidate_name, u.email as candidate_email
                FROM interviews i
                JOIN users u ON i.user_id = u.id
                WHERE i.id = ?
                """,
                (str(interview_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_interview_answers(interview_id, db_path=None):
    """Retrieve all answers for an interview, formatted for reporting."""
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM interview_answers
                    WHERE interview_id = %s
                    ORDER BY id ASC
                    """,
                    (str(interview_id),)
                )
                rows = cur.fetchall()
                answers = []
                for r in rows:
                    ans = dict(r)
                    ans["strengths"] = json.loads(ans["strengths_json"] or "[]")
                    ans["improvements"] = json.loads(ans["improvements_json"] or "[]")
                    answers.append(ans)
                return answers
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM interview_answers
                WHERE interview_id = ?
                ORDER BY id ASC
                """,
                (str(interview_id),)
            )
            rows = cursor.fetchall()
            answers = []
            for r in rows:
                ans = dict(r)
                ans["strengths"] = json.loads(ans["strengths_json"] or "[]")
                ans["improvements"] = json.loads(ans["improvements_json"] or "[]")
                answers.append(ans)
            return answers
    finally:
        conn.close()


def get_student_interviews(user_id, db_path=None):
    """Get all past interviews for a given student."""
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM interviews
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    """,
                    (user_id,)
                )
                return [dict(r) for r in cur.fetchall()]
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM interviews
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ---------------- Teacher Analytics & Roster ----------------

def get_all_students(db_path=None):
    """Get a summary of all students with interview statistics for teachers."""
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        u.id,
                        u.name,
                        u.email,
                        u.created_at,
                        COUNT(i.id) as total_interviews,
                        SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed_interviews,
                        COALESCE(AVG(CASE WHEN i.status = 'completed' THEN i.percentage ELSE NULL END), 0.0) as average_percentage,
                        MAX(i.created_at) as last_interview_at
                    FROM users u
                    LEFT JOIN interviews i ON u.id = i.user_id
                    WHERE u.role = 'student' AND u.email NOT LIKE '%%@interviewbot.local'
                    GROUP BY u.id
                    ORDER BY u.name ASC
                    """
                )
                return [dict(r) for r in cur.fetchall()]
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT
                    u.id,
                    u.name,
                    u.email,
                    u.created_at,
                    COUNT(i.id) as total_interviews,
                    SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed_interviews,
                    COALESCE(AVG(CASE WHEN i.status = 'completed' THEN i.percentage ELSE NULL END), 0.0) as average_percentage,
                    MAX(i.created_at) as last_interview_at
                FROM users u
                LEFT JOIN interviews i ON u.id = i.user_id
                WHERE u.role = 'student' AND u.email NOT LIKE '%@interviewbot.local'
                GROUP BY u.id
                ORDER BY u.name ASC
                """
            )
            return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_class_analytics(db_path=None):
    """Get class-wide aggregate metrics for the teacher dashboard."""
    conn = get_db_connection(db_path)
    try:
        if is_postgresql(conn):
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(DISTINCT u.id) as total_students,
                        COUNT(DISTINCT i.id) as total_interviews,
                        SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed_interviews,
                        COALESCE(AVG(CASE WHEN i.status = 'completed' THEN i.percentage ELSE NULL END), 0.0) as class_average_percentage
                    FROM users u
                    LEFT JOIN interviews i ON u.id = i.user_id
                    WHERE u.role = 'student' AND u.email NOT LIKE '%@interviewbot.local'
                    """
                )
                row = cur.fetchone()
                stats = dict(row) if row else {
                    "total_students": 0,
                    "total_interviews": 0,
                    "completed_interviews": 0,
                    "class_average_percentage": 0.0,
                }

                # Calculate dimension averages across all completed answers
                cur.execute(
                    """
                    SELECT
                        COALESCE(AVG(a.correctness), 0.0) as avg_correctness,
                        COALESCE(AVG(a.relevance), 0.0) as avg_relevance,
                        COALESCE(AVG(a.completeness), 0.0) as avg_completeness,
                        COALESCE(AVG(a.clarity), 0.0) as avg_clarity
                    FROM interview_answers a
                    JOIN interviews i ON a.interview_id = i.id
                    WHERE i.status = 'completed'
                    """
                )
                dim_row = cur.fetchone()
                stats["dimension_averages"] = {
                    "correctness": round(dim_row["avg_correctness"], 2),
                    "relevance": round(dim_row["avg_relevance"], 2),
                    "completeness": round(dim_row["avg_completeness"], 2),
                    "clarity": round(dim_row["avg_clarity"], 2),
                }
                stats["class_average_percentage"] = round(stats["class_average_percentage"], 1)
                return stats
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT
                    COUNT(DISTINCT u.id) as total_students,
                    COUNT(DISTINCT i.id) as total_interviews,
                    SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) as completed_interviews,
                    COALESCE(AVG(CASE WHEN i.status = 'completed' THEN i.percentage ELSE NULL END), 0.0) as class_average_percentage
                FROM users u
                LEFT JOIN interviews i ON u.id = i.user_id
                WHERE u.role = 'student' AND u.email NOT LIKE '%@interviewbot.local'
                """
            )
            row = cursor.fetchone()
            stats = dict(row) if row else {
                "total_students": 0,
                "total_interviews": 0,
                "completed_interviews": 0,
                "class_average_percentage": 0.0,
            }

            # Calculate dimension averages across all completed answers
            dim_cursor = conn.execute(
                """
                SELECT
                    COALESCE(AVG(a.correctness), 0.0) as avg_correctness,
                    COALESCE(AVG(a.relevance), 0.0) as avg_relevance,
                    COALESCE(AVG(a.completeness), 0.0) as avg_completeness,
                    COALESCE(AVG(a.clarity), 0.0) as avg_clarity
                FROM interview_answers a
                JOIN interviews i ON a.interview_id = i.id
                WHERE i.status = 'completed'
                """
            )
            dim_row = dim_cursor.fetchone()
            stats["dimension_averages"] = {
                "correctness": round(dim_row["avg_correctness"], 2),
                "relevance": round(dim_row["avg_relevance"], 2),
                "completeness": round(dim_row["avg_completeness"], 2),
                "clarity": round(dim_row["avg_clarity"], 2),
            }
            stats["class_average_percentage"] = round(stats["class_average_percentage"], 1)
            return stats
    finally:
        conn.close()