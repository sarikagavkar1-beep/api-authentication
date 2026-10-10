
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "dev-only-change-this-secret-before-deployment")
app.config["JWT_ALGORITHM"] = "HS256"
TOKEN_MINUTES = 30

# Demo users only. In a real application, store users in a database.
USERS = {
    "student": {
        "password_hash": generate_password_hash("Student@123"),
        "role": "user",
    },
    "admin": {
        "password_hash": generate_password_hash("Admin@123"),
        "role": "admin",
    },
}


def create_access_token(username, role):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm=app.config["JWT_ALGORITHM"])


def token_required(role=None):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            scheme, _, token = header.partition(" ")
            if scheme.lower() != "bearer" or not token:
                return jsonify(error="Missing token. Use Authorization: Bearer <token>."), 401
            try:
                payload = jwt.decode(
                    token,
                    app.config["JWT_SECRET"],
                    algorithms=[app.config["JWT_ALGORITHM"]],
                )
            except jwt.ExpiredSignatureError:
                return jsonify(error="Token has expired. Please log in again."), 401
            except jwt.InvalidTokenError:
                return jsonify(error="Invalid token."), 401

            username = payload.get("sub")
            if username not in USERS:
                return jsonify(error="Unknown user."), 401
            if role and payload.get("role") != role:
                return jsonify(error="You do not have permission to access this resource."), 403
            request.current_user = {"username": username, "role": payload.get("role")}
            return view_function(*args, **kwargs)
        return wrapped
    return decorator


@app.get("/")
def index():
    return jsonify(
        project="API Authentication Learning Lab",
        endpoints={
            "POST /register": "Create a demo account",
            "POST /login": "Get a JWT access token",
            "GET /api/profile": "Protected endpoint; requires Bearer token",
            "GET /api/admin": "Admin-only endpoint; requires admin token",
            "GET /health": "Health check",
        },
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = data.get("password", "")
    if len(username) < 3:
        return jsonify(error="Username must be at least 3 characters."), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify(error="Password must be at least 8 characters."), 400
    if username in USERS:
        return jsonify(error="Username already exists."), 409
    USERS[username] = {
        "password_hash": generate_password_hash(password),
        "role": "user",
    }
    return jsonify(message="Account created. You can now log in."), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = data.get("password", "")
    user = USERS.get(username)
    if not user or not isinstance(password, str) or not check_password_hash(user["password_hash"], password):
        return jsonify(error="Invalid username or password."), 401
    token = create_access_token(username, user["role"])
    return jsonify(
        access_token=token,
        token_type="Bearer",
        expires_in_seconds=TOKEN_MINUTES * 60,
    )


@app.get("/api/profile")
@token_required()
def profile():
    return jsonify(message="You accessed a protected endpoint.", user=request.current_user)


@app.get("/api/admin")
@token_required(role="admin")
def admin():
    return jsonify(message="Admin access granted.", user=request.current_user)


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="Endpoint not found."), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify(error="HTTP method not allowed for this endpoint."), 405


if __name__ == "__main__":
    # Debug mode is intentionally disabled.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
