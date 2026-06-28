from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from app.extensions import db
from app.models.auth import User

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
    
    # Success
    login_user(user)

    return redirect(url_for('home.dashboard'))


@auth_bp.get('/sign-up')
def sign_up():
    return render_template('auth/sign-up.html')

@auth_bp.post('/sign-up/validate')
def sign_up_validate():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User(username=username, email=email)

    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        return str(e), 500