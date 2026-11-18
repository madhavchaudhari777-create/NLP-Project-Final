from functools import wraps
from flask import jsonify, redirect, request, session, url_for
from app.db import get_user_by_id


def login_user(user):
    """Store authenticated user details in the Flask session."""
    session["user_id"] = user["id"]
    session["user_role"] = user["role"]
    session["user_name"] = user["name"]
    session.permanent = True


def logout_user():
    """Clear user authentication details from the session."""
    session.pop("user_id", None)
    session.pop("user_role", None)
    session.pop("user_name", None)
    session.pop("interview_id", None)


def get_current_user():
    """Return the currently authenticated user dictionary, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def login_required(f):
    """Decorator to ensure the user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            if request.is_json or request.path.startswith("/api/") or request.path in ("/setup", "/evaluate"):
                return jsonify(
                    success=False,
                    error="Authentication required. Please sign in.",
                    redirect="/login",
                ), 401
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Decorator to ensure the user has teacher or admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify(
                    success=False,
                    error="Authentication required. Please sign in as a teacher.",
                    redirect="/login",
                ), 401
            return redirect(url_for("main.home"))
        if user.get("role") not in ("teacher", "admin"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify(
                    success=False,
                    error="Access restricted to teachers.",
                ), 403
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function
