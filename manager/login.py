import traceback
import jwt
import datetime
from hashlib import sha256
from functools import wraps
from flask import request, jsonify, Blueprint, session
from flask import current_app as app
from database_connection import DatabaseConnection


auth_bp = Blueprint("auth_bp", __name__)


blacklisted_tokens = {}  # TODO: Implement a mechanism to blacklist tokens


def generate_token(user_id):
    try:
        token = jwt.encode(
            {
                "user_id": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            app.secret_key,
            algorithm="HS256",
        )
        return token
    except Exception as e:
        print(f"Error encoding token: {e}")
        traceback.print_exc()
        return None


def decode_token(token):
    try:
        return jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Token is missing"}), 401
        try:
            token = auth_header.split(" ")[1]
            if token in blacklisted_tokens:
                return jsonify({"error": "You're logged out."}), 401
            data = decode_token(token)
            if "error" in data:
                return jsonify(data), 401
            session["user_id"] = data["user_id"]
            return f(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            return jsonify({"error": "Token is invalid"}), 401

    return decorated_function


def hash_password(password):
    return sha256(password.encode()).hexdigest()


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        username = data["username"]
        email = data["email"]
        password = hash_password(data["password"])
        db = DatabaseConnection.get_instance()
        db.write(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password),
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data["username"]
        email = data["email"]
        password = hash_password(data["password"])
        db = DatabaseConnection.get_instance()
        user = db.read_one(
            "SELECT * FROM users WHERE (username = %s OR email = %s) AND password = %s",
            (
                username,
                email,
                password,
            ),
        )
        if user:
            token = generate_token(user[0])
            return jsonify({"status": "success", "token": token}), 200
        else:
            return (
                jsonify(
                    {"status": "failure", "message": "Invalid username or password"}
                ),
                401,
            )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
@auth_required
def logout():
    try:
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        blacklisted_tokens[token] = True
        return jsonify({"status": "success"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/is-logged-in", methods=["GET"])
@auth_required
def is_logged_in():
    try:
        if "user_id" in session:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure"}), 401
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
