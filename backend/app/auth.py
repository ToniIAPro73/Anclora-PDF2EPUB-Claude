from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from .database import get_db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _generate_token(user_id):
    exp_seconds = current_app.config.get("JWT_EXPIRATION", 3600)
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(seconds=exp_seconds)}
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            db = next(get_db())
            user = db.query(User).filter(User.id == data.get("user_id")).first()
            if user is None:
                raise jwt.InvalidTokenError
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        finally:
            db.close()
        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    db = next(get_db())
    try:
        # Verificar si el usuario ya existe
        if db.query(User).filter(User.username == username).first():
            return jsonify({"error": "User already exists"}), 400

        # Crear nuevo usuario
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = _generate_token(user.id)
        return jsonify({"token": token}), 201
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    db = next(get_db())
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = _generate_token(user.id)
        return jsonify({"token": token})
    finally:
        db.close()
