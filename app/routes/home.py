from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.extensions import db
from app.models.auth import User

home_bp = Blueprint('home', __name__)

@home_bp.get('/dashboard')
@login_required
def dashboard():
    return render_template('home/dashboard.html')