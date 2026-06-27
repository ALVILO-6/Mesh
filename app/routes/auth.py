from flask import Blueprint, render_template

auth_bp = Blueprint('auth', __name__)

@auth_bp.get('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.get('/sign-up')
def sign_up():
    return render_template('auth/sign-up.html')