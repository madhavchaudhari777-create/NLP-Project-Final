from uuid import uuid4
<<<<<<< HEAD
import pandas as pd
import os
=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    session,
)

from app.ai.dialogue_manager import DialogueManager
from app.auth import (
    get_current_user,
    login_required,
    login_user,
    logout_user,
    teacher_required,
)
from app.db import (
    authenticate_user,
    create_interview_record,
    create_user,
    finalize_interview,
    get_all_students,
    get_class_analytics,
    get_interview_answers,
    get_interview_by_id,
    get_student_interviews,
    get_user_by_email,
    get_user_by_id,
    record_interview_answer,
)
from app.services.interview_service import InterviewService
from app.services.question_service import QuestionService
from app.services.report_service import ReportService

main = Blueprint("main", __name__)
question_service = QuestionService()
report_service = ReportService()

# In-memory active interview sessions for stateful dialog flow.
interview_sessions = {}


def get_session_service():
    """Return the InterviewService for the current browser session."""
    interview_id = session.get("interview_id")
    interview = interview_sessions.get(interview_id)
    return interview["service"] if interview else None


def public_question(question):
    """Return only the fields needed by the frontend."""
    return {
        "id": str(question["id"]),
        "question": question["question"],
        "difficulty": question["difficulty"],
    }


def choose_next_question(interview, difficulty):
    """Choose an unanswered question at the requested difficulty if possible."""
    remaining = [
        item for item in interview["questions"]
        if item["id"] not in interview["answered_question_ids"]
    ]

    if not remaining:
        return None

    # Prefer the current adaptive difficulty.
    matching = [
        item for item in remaining
        if item["difficulty"] == difficulty
    ]

    if matching:
        return matching[0]

    return remaining[0]


def get_or_create_context_user(candidate_name=None):
    """Return the logged in user or a guest user record for unauthenticated runs."""
    current_user = get_current_user()
    if current_user:
        return current_user

    guest_email = "guest@interviewbot.local"
    guest = get_user_by_email(guest_email)
    if not guest:
        guest = create_user(
            name=candidate_name or "Guest Candidate",
            email=guest_email,
            password="GuestPassword123!",
            role="student",
        )
    return guest


# ---------------- Web Pages ----------------

@main.route("/")
def home():
    view = "dashboard" if get_current_user() else "login"
    return render_template("index.html", initial_view=view)


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("index.html", initial_view="login")

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify(success=False, error="Please provide login credentials."), 400

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    user = authenticate_user(email, password)
    if not user:
        return jsonify(success=False, error="Invalid email or password."), 401

    login_user(user)
    return jsonify(
        success=True,
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    ), 200


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("index.html", initial_view="register")

    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify(success=False, error="Please provide registration details."), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    role = str(data.get("role", "student")).strip().lower()

    if role not in ("student", "teacher"):
        role = "student"

    try:
        user = create_user(name=name, email=email, password=password, role=role)
        login_user(user)
        return jsonify(
            success=True,
            user={
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
        ), 201
    except ValueError as err:
        return jsonify(success=False, error=str(err)), 400
    except Exception:
        current_app.logger.exception("Registration failed.")
        return jsonify(success=False, error="Unable to register account. Please try again."), 500


@main.route("/dashboard")
def dashboard_page():
    return render_template("index.html", initial_view="dashboard")


@main.route("/teacher")
def teacher_page():
    return render_template("index.html", initial_view="teacher")


@main.route("/interview")
def interview_page():
    return render_template("index.html", initial_view="interview")


@main.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return jsonify(success=True, message="Successfully logged out."), 200


@main.route("/api/me", methods=["GET"])
def current_user_info():
    user = get_current_user()
    if not user:
        return jsonify(authenticated=False, user=None), 200
    return jsonify(
        authenticated=True,
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    ), 200


<<<<<<< HEAD
@main.route("/api/dataset/stats", methods=["GET"])
def dataset_stats():
    """Return cleaned dataset preprocessing statistics (CO1 evidence)."""
    try:
        df = pd.read_parquet("dataset/processed/asag2024_cleaned.parquet")
        stats = {
            "total_records": int(len(df)),
            "columns": list(df.columns),
            "duplicate_records": int(df.duplicated().sum()),
        }
        if "grade" in df.columns:
            stats["grade_distribution"] = df["grade"].value_counts().to_dict()
        if "normalized_grade" in df.columns:
            stats["normalized_grade_distribution"] = df["normalized_grade"].value_counts().to_dict()
        return jsonify(success=True, stats=stats), 200
    except Exception as e:
        current_app.logger.exception("Dataset stats failed.")
        return jsonify(success=False, error=str(e)), 500


=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
# ---------------- Student Dashboard Endpoints ----------------

@main.route("/api/student/dashboard", methods=["GET"])
@login_required
def student_dashboard_data():
    user = get_current_user()
    interviews = get_student_interviews(user["id"])

    completed = [i for i in interviews if i.get("status") == "completed"]
    total_completed = len(completed)
    avg_percentage = (
        round(sum(float(i.get("percentage", 0.0)) for i in completed) / total_completed, 1)
        if total_completed > 0
        else 0.0
    )

    # Calculate dimensional stats across candidate's answers
    dim_totals = {"correctness": 0, "relevance": 0, "completeness": 0, "clarity": 0}
    total_answers = 0

    for item in completed:
        answers = get_interview_answers(item["id"])
        for ans in answers:
            total_answers += 1
            for dim in dim_totals:
                dim_totals[dim] += ans.get(dim, 0)

    dim_averages = {
        k: round(v / total_answers, 1) if total_answers > 0 else 0.0
        for k, v in dim_totals.items()
    }

    sorted_dims = sorted(dim_averages.items(), key=lambda p: p[1], reverse=True)
    strongest = sorted_dims[0][0] if total_answers > 0 else "N/A"
    weakest = sorted_dims[-1][0] if total_answers > 0 else "N/A"

    return jsonify(
        success=True,
        user={"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]},
        stats={
            "total_interviews": len(interviews),
            "completed_interviews": total_completed,
            "average_percentage": avg_percentage,
            "questions_answered": total_answers,
            "dimension_averages": dim_averages,
            "strongest_area": strongest,
            "weakest_area": weakest,
        },
        interviews=interviews,
    ), 200


@main.route("/api/interview/<interview_id>/report", methods=["GET"])
@login_required
def get_interview_full_report(interview_id):
    user = get_current_user()
    interview = get_interview_by_id(interview_id)
    if not interview:
        return jsonify(success=False, error="Interview not found."), 404

    # Allow student who took it, or teacher/admin
    if interview["user_id"] != user["id"] and user.get("role") not in ("teacher", "admin"):
        return jsonify(success=False, error="Unauthorized to view this interview report."), 403

    answers = get_interview_answers(interview_id)
    if not answers:
        return jsonify(
            success=True,
            interview=interview,
            report=None,
            answers=[],
            message="No answered questions recorded for this session.",
        ), 200

    report_input = [
        {
            "question": a["question_text"],
            "difficulty": a["difficulty"],
            "evaluation": {
                "score": a["score"],
                "max_score": a["max_score"],
                "correctness": a["correctness"],
                "relevance": a["relevance"],
                "completeness": a["completeness"],
                "clarity": a["clarity"],
                "feedback": a["feedback"],
                "strengths": a["strengths"],
                "improvements": a["improvements"],
            },
            "student_answer": a["student_answer"],
            "evaluation_method": a["evaluation_method"],
        }
        for a in answers
    ]

    report = report_service.generate_report(
        report_input,
        candidate_name=interview.get("candidate_name") or "Candidate",
        role=interview.get("role_applied") or "General",
    )

    return jsonify(
        success=True,
        interview=interview,
        report=report,
        answers=answers,
    ), 200


# ---------------- Teacher Admin Endpoints ----------------

@main.route("/api/teacher/analytics", methods=["GET"])
@teacher_required
def teacher_analytics():
    stats = get_class_analytics()
    return jsonify(success=True, analytics=stats), 200


<<<<<<< HEAD
@main.route("/api/teacher/topics", methods=["GET"])
@teacher_required
def teacher_topics():
    """Run LDA topic modeling on completed interview answers (CO3)."""
    from app.ai.nlp_processor import NLPProcessor
    try:
        nlp = NLPProcessor()
        result = nlp.extract_topics_lda([
            "What is a variable in Python?",
            "Explain decorators in Python.",
            "How does a Python generator work?",
            "What is supervised machine learning?",
            "What is the difference between classification and regression?",
            "Explain overfitting and how to reduce it.",
            "What is a primary key in a database?",
            "Explain the difference between WHERE and HAVING in SQL.",
            "What is the difference between a process and a thread?",
            "What is Docker and why is it used?",
            "What is an API?",
            "What is middleware in a backend application?",
            "What is React and why is it used?",
            "What is TypeScript and how is it different from JavaScript?",
            "What is Natural Language Processing?",
            "What is tokenization in NLP?",
        ], n_topics=3, n_words=5)
        return jsonify(success=True, topics=result), 200
    except Exception as e:
        current_app.logger.exception("Topic modeling failed.")
        return jsonify(success=False, error=str(e)), 500


=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
@main.route("/api/teacher/students", methods=["GET"])
@teacher_required
def teacher_students_list():
    students = get_all_students()
    return jsonify(success=True, students=students), 200


@main.route("/api/teacher/student/<int:student_id>", methods=["GET"])
@teacher_required
def teacher_student_detail(student_id):
    student = get_user_by_id(student_id)
    if not student:
        return jsonify(success=False, error="Student not found."), 404

    interviews = get_student_interviews(student_id)
    return jsonify(
        success=True,
        student=student,
        interviews=interviews,
    ), 200


# ---------------- Interview Flow (Active Arena) ----------------

@main.route("/setup", methods=["GET", "POST"])
def interview_setup():
    if request.method == "GET":
        return render_template("index.html")

    data = request.get_json(silent=True) if request.is_json else request.form

    if data is None:
        return jsonify(
            success=False,
            error="Please submit valid interview setup details.",
        ), 400

    name = data.get("name", "")
    role = data.get("role", "")
    difficulty = data.get("difficulty", "Beginner")

    name = name.strip() if isinstance(name, str) else ""
    role = role.strip() if isinstance(role, str) else ""
    difficulty = difficulty.strip() if isinstance(difficulty, str) else ""

    skills_input = data.get("skills", [])

    if isinstance(skills_input, str):
        skills = [
            item.strip()
            for item in skills_input.split(",")
            if item.strip()
        ]
    elif isinstance(skills_input, list):
        skills = [
            item.strip()
            for item in skills_input
            if isinstance(item, str) and item.strip()
        ]
    else:
        skills = []

    raw_count = data.get("number_of_questions", 2)

    try:
        if isinstance(raw_count, bool):
            raise ValueError

        number_of_questions = int(raw_count)

        if isinstance(raw_count, float) and not raw_count.is_integer():
            raise ValueError

        if (
            isinstance(raw_count, str)
            and str(number_of_questions) != raw_count.strip()
        ):
            raise ValueError

    except (TypeError, ValueError):
        return jsonify(
            success=False,
            error="Number of questions must be a whole number.",
        ), 400

    if not name:
        return jsonify(success=False, error="Candidate name is required."), 400

    if not role:
        return jsonify(
            success=False,
            error="Please select an interview role.",
        ), 400

    if not skills:
        return jsonify(
            success=False,
            error="Please enter at least one skill.",
        ), 400

    if difficulty not in QuestionService.VALID_DIFFICULTIES:
        return jsonify(
            success=False,
            error="Please select a valid difficulty level.",
        ), 400

    if not 1 <= number_of_questions <= 10:
        return jsonify(
            success=False,
            error="Please request between 1 and 10 questions.",
        ), 400

    try:
        questions = question_service.get_questions(
            role=role,
            skills=skills,
            difficulty=difficulty,
            number_of_questions=number_of_questions,
        )
    except (ValueError, RuntimeError) as error:
        return jsonify(success=False, error=str(error)), 400
    except Exception:
        current_app.logger.exception("Interview setup failed.")
        return jsonify(
            success=False,
            error="Unable to prepare the interview. Please try again.",
        ), 500

    # Keep reference answers privately on the server.
    question_pool = []

    for index, question in enumerate(questions):
        question_pool.append({
            "id": str(question.get("id", index + 1)),
            "question": question.get("question", ""),
            "difficulty": question.get("difficulty", difficulty),
            "reference_answer": question.get("reference_answer"),
        })

    if not question_pool:
        return jsonify(
            success=False,
            error="No interview questions could be prepared.",
        ), 400

    dialogue_manager = DialogueManager()
<<<<<<< HEAD
    dialogue_manager.total_questions = len(questions)
=======
    dialogue_manager.total_questions = number_of_questions
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
    dialogue_manager.current_difficulty = difficulty

    interview_service = InterviewService(
        dialogue_manager=dialogue_manager,
    )

    old_id = session.get("interview_id")
    if old_id:
        interview_sessions.pop(old_id, None)

    interview_id = str(uuid4())

    # Resolve context user (logged in user or guest)
    user = get_or_create_context_user(candidate_name=name)

    interview = {
        "id": interview_id,
        "user_id": user["id"],
        "service": interview_service,
        "candidate": {
            "name": name,
            "role": role,
            "skills": skills,
            "difficulty": difficulty,
        },
        "questions": question_pool,
<<<<<<< HEAD
        "total_questions": len(questions),
=======
        "total_questions": number_of_questions,
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        "answered_question_ids": set(),
        "current_question_id": None,
    }

    first_question = choose_next_question(interview, difficulty)
    interview["current_question_id"] = first_question["id"]
    interview_sessions[interview_id] = interview
    session["interview_id"] = interview_id

    # Persist interview to SQLite database
    create_interview_record(
        interview_id=interview_id,
        user_id=user["id"],
        role_applied=role,
        target_skills=skills,
        difficulty=difficulty,
<<<<<<< HEAD
        total_questions=len(questions),
=======
        total_questions=number_of_questions,
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
    )

    return jsonify(
        success=True,
        interview_id=interview_id,
        candidate={
            **interview["candidate"],
<<<<<<< HEAD
            "number_of_questions": len(questions),
        },
        question=public_question(first_question),
        progress={"answered": 0, "total": len(questions)},
=======
            "number_of_questions": number_of_questions,
        },
        question=public_question(first_question),
        progress={"answered": 0, "total": number_of_questions},
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
    ), 200


@main.route("/evaluate", methods=["POST"])
def evaluate_answer():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            success=False,
            error="Please submit a valid JSON answer.",
        ), 400

    answer = data.get("answer", "")
    question_id = data.get("question_id")
    question = data.get("question", "")

    if not isinstance(answer, str) or not answer.strip():
        return jsonify(
            success=False,
            error="Please enter your answer before submitting.",
        ), 400

    interview_id = session.get("interview_id")
    interview = interview_sessions.get(interview_id) if interview_id else None

    if interview is None:
        return jsonify(
            success=False,
            error="No active interview found. Please start a new interview.",
        ), 400

    if question_id is not None:
        question_id = str(question_id)
        question_item = next(
            (
                item for item in interview["questions"]
                if item["id"] == question_id
            ),
            None,
        )
    else:
        question_item = next(
            (
                item for item in interview["questions"]
                if item["question"].strip() == question.strip()
            ),
            None,
        )

    if question_item is None:
        return jsonify(
            success=False,
            error="This question does not belong to the active interview.",
        ), 400

    question_id = question_item["id"]

    if question_id != interview["current_question_id"]:
        return jsonify(
            success=False,
            error="This is not the current interview question.",
        ), 400

    if question_id in interview["answered_question_ids"]:
        return jsonify(
            success=False,
            error="This question has already been answered.",
        ), 400

    try:
        result = interview["service"].process_answer(
            question=question_item["question"],
            answer=answer.strip(),
            role=interview["candidate"]["role"],
            reference_answer=question_item.get("reference_answer"),
            max_score=10,
            question_id=question_id,
        )
    except ValueError as error:
        return jsonify(success=False, error=str(error)), 400
<<<<<<< HEAD
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        current_app.logger.exception("Answer evaluation failed.")
        return jsonify(
            success=False,
            error=f"Server error: {str(e)}",
            traceback=tb,
=======
    except Exception:
        current_app.logger.exception("Answer evaluation failed.")
        return jsonify(
            success=False,
            error="Unable to evaluate this answer. Please try again.",
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        ), 500

    interview["answered_question_ids"].add(question_id)

<<<<<<< HEAD
    # Persist the answer evaluation in SQLite (never crash the request if DB fails).
    try:
        record_interview_answer(
            interview_id=interview_id,
            question_id=question_id,
            question_text=question_item["question"],
            difficulty=result.get("difficulty", question_item.get("difficulty", "Intermediate")),
            student_answer=answer.strip(),
            evaluation=result["evaluation"],
        )
    except Exception:
        current_app.logger.exception("Failed to persist interview answer.")
=======
    # Persist the answer evaluation in SQLite
    record_interview_answer(
        interview_id=interview_id,
        question_id=question_id,
        question_text=question_item["question"],
        difficulty=result.get("difficulty", question_item.get("difficulty", "Intermediate")),
        student_answer=answer.strip(),
        evaluation=result["evaluation"],
    )
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082

    answered = len(interview["answered_question_ids"])
    total = interview["total_questions"]
    finished = answered >= total

    state = dict(result["interview_state"])
    state["interview_complete"] = finished

    # If interview is complete, finalize record in database
    if finished:
<<<<<<< HEAD
        try:
            history = interview["service"].get_evaluation_history()
            total_score = sum(
                float(item["evaluation"].get("score", 0.0)) for item in history
            )
            max_possible = sum(
                float(item["evaluation"].get("max_score", 10.0)) for item in history
            )
            percentage = round(
                (total_score / max_possible * 100), 1
            ) if max_possible > 0 else 0.0
            finalize_interview(
                interview_id=interview_id,
                total_score=total_score,
                max_score=max_possible,
                percentage=percentage,
            )
        except Exception:
            current_app.logger.exception("Failed to finalize interview.")
=======
        history = interview["service"].get_evaluation_history()
        total_score = sum(float(item["evaluation"].get("score", 0.0)) for item in history)
        max_possible = sum(float(item["evaluation"].get("max_score", 10.0)) for item in history)
        percentage = round((total_score / max_possible * 100), 1) if max_possible > 0 else 0.0
        finalize_interview(
            interview_id=interview_id,
            total_score=total_score,
            max_score=max_possible,
            percentage=percentage,
        )
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082

    next_question = None

    if not finished:
        next_difficulty = interview["service"].dialogue_manager.current_difficulty
        next_question = choose_next_question(interview, next_difficulty)

<<<<<<< HEAD
        # Fallback: if choose_next_question returns None but there are still
        # unanswered questions, find one manually.
        if next_question is None and answered < total:
            for item in interview["questions"]:
                if item["id"] not in interview["answered_question_ids"]:
                    next_question = item
                    break

        if next_question is None:
=======
        if next_question is None:
            current_app.logger.error(
                "Question pool exhausted before the requested question count."
            )
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
            return jsonify(
                success=False,
                error="No more questions are available. Please restart the interview.",
            ), 500

        interview["current_question_id"] = next_question["id"]

    return jsonify(
        success=True,
        evaluation=result["evaluation"],
<<<<<<< HEAD
        interview_complete=state.get("interview_complete", False),
        adaptation=result.get("adaptation", {}),
        interview_state=state,
        next_question=public_question(next_question) if next_question else None,
        progress={
            "answered": len(interview["answered_question_ids"]),
            "total": interview["total_questions"],
        },
=======
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
        
        reference_answer=question_item.get("reference_answer"),
        show_reference_answer=(
        result["evaluation"].get("answer_status") in [
            "incorrect",
            "irrelevant"
        ]
        or float(result["evaluation"].get("score", 0)) < 6
        ),
        
<<<<<<< HEAD
                nlp_summary={
=======
        nlp_summary={
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
            "word_count": result["nlp_analysis"].get(
                "word_count", len(answer.strip().split())
            ),
            "skills_detected": result["nlp_analysis"].get("skills", []),
            "keywords": result["nlp_analysis"].get("keywords", []),
<<<<<<< HEAD
            "sentiment": result["nlp_analysis"].get("sentiment", {}),
            "similarity": result["evaluation"].get("semantic_similarity"),
            "similarity_engine": result["evaluation"].get("semantic_engine"),
        },
=======
        },
        adaptation=result["adaptation"],
        interview_state=state,
        progress={"answered": answered, "total": total},
        interview_complete=finished,
        next_question=(
            public_question(next_question) if next_question else None
        ),
>>>>>>> 175a800e5e426185646cda9d95847bc0bdb8e082
    ), 200


@main.route("/next-question", methods=["GET"])
def next_question():
    """Return the current unanswered question."""
    interview_id = session.get("interview_id")
    interview = interview_sessions.get(interview_id) if interview_id else None

    if interview is None:
        return jsonify(
            success=False,
            error="No active interview found. Please start a new interview.",
        ), 400

    if len(interview["answered_question_ids"]) >= interview["total_questions"]:
        return jsonify(
            success=False,
            error="The interview is complete.",
        ), 400

    current_id = interview["current_question_id"]

    question_item = next(
        (
            item for item in interview["questions"]
            if item["id"] == current_id
        ),
        None,
    )

    if question_item is None:
        return jsonify(
            success=False,
            error="No current question is available.",
        ), 400

    return jsonify(
        success=True,
        question=public_question(question_item),
        progress={
            "answered": len(interview["answered_question_ids"]),
            "total": interview["total_questions"],
        },
    ), 200
