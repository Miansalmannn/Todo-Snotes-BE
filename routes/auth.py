from flask import Blueprint, request, jsonify, render_template_string
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import timedelta
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template_string('''
            <h2>Login</h2>
            <form method="post">
                Username: <input type="text" name="username"><br><br>
                Password: <input type="password" name="password"><br><br>
                <input type="submit" value="Login">
            </form>
            <p>Don't have an account? <a href="{{ url_for('auth.register') }}">Register here</a></p>
        ''')

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))

        response = jsonify(message="Login successful")
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,     
            samesite='Lax',
            max_age=86400 
        )
        return response, 200

    return jsonify(error="Invalid username or password"), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        return jsonify(error="Username and password are required."), 400

    if User.query.filter_by(username=username).first():
        return jsonify(error="Username already exists."), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(days=1))

    response = jsonify(message=f"User {username} registered successfully.")
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=86400
    )
    return response, 201



@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logged out"})
    response.set_cookie("access_token", "", max_age=0, path="/")
    return response
