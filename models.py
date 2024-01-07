from flask_login import UserMixin, login_manager
from __init__ import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(1000), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    # country = db.Column(db.String(100))
    # games_played = db.Column(db.Integer)
    # games_won = db.Column(db.Integer)
    # games_lost = db.Column(db.Integer)
    # games_streamed = db.Column(db.Integer)
    profile_picture = db.Column(db.String(20), nullable=False, default='static/Default_pfp.png')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_picture}')"


    

