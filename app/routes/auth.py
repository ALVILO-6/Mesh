from flask import Blueprint, render_template, request, redirect, url_for, make_response, current_app

from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models.auth import User
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.get('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.post('/login/validate')
def login_validate():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Username and password must be filled", 400

    user = User.query.filter_by(username=username).first()

    if user is None:
        return "User not found", 400
    
    if not user.check_password(password):
        return "Incorrect password", 400

    remember = request.form.get('remember-me') is not None

    now = datetime.now(timezone.utc)

    # Check session
    if user.logged_in and user.active_on:
        expired = (now - user.active_on) > current_app.permanent_session_lifetime

        if not expired:
            return "User is logged in on another device", 400
        
        # Session expired
        user.logged_in = False
        user.active_on = None
    
    # Login Success
    login_user(user, remember=remember)

    user.logged_in = True
    user.active_on = now

    db.session.commit()

    expired = now + current_app.permanent_session_lifetime

    response = make_response('')
    response.headers['HX-Redirect'] = url_for('home.dashboard')
    response.headers['X-Session-Expires'] = str(int(expired.timestamp()))
    return response

@auth_bp.get('/sign-up')
def sign_up():
    return render_template('auth/sign-up.html')

@auth_bp.post('/sign-up/validate')
def sign_up_validate():
    username = request.form.get('username')
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    confirm_password = request.form.get('confirm-password')

    # Empty input
    if not username or not email or not password or not confirm_password:
        return 'All fields are required', 400
    
    # Password mismatch
    if password != confirm_password:
        return 'Password mismatch', 400
    
    username_exists = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()

    if username_exists and email_exists:
        return 'Username and email are already taken', 400
    
    if username_exists:
        return 'Username is already taken', 400
    
    if email_exists:
        return 'Email is already taken', 400
    
    user = User(username=username, email=email)

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()

        response = make_response('')
        response.headers['HX-Redirect'] = url_for('auth.login')
        return response

    except Exception:
        db.session.rollback()
        return 'Internal Server Error', 500
    
@auth_bp.post('/logout')
def logout():
    # Check if user is authenticated (not anonymous)
    if current_user.is_authenticated:
        current_user.logged_in = False
        current_user.active_on = None
        db.session.commit()

    logout_user()

    response = make_response('')
    response.headers['HX-Redirect'] = url_for('auth.login')
    return response

@auth_bp.get('/check-session')
def check_session():
    if not current_user.is_authenticated:
        response = make_response("", 401)
        response.headers["HX-Trigger"] = "sessionExpired"
        return response

    now = datetime.now(timezone.utc)
    remaining = current_user.active_on + current_app.permanent_session_lifetime - now

    seconds_left = remaining.total_seconds()

    # Session Expired
    if seconds_left <= 3:
        response = make_response("", 401)
        response.headers["HX-Trigger"] = "sessionExpired"
        return response

    # Session Warning
    if seconds_left <= 5:
        response = make_response("WARNING")
        response.headers["HX-Trigger"] = "sessionWarning"
        return response

    return "OK", 200