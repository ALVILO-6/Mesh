from app.extensions import login_manager
from app.models.auth import User

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))