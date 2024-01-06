from flask_login import UserMixin, login_manager
from __init__ import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000), unique=True)
    country = db.Column(db.String(100))
    games_played = db.Column(db.Integer)
    games_won = db.Column(db.Integer)
    games_lost = db.Column(db.Integer)
    games_streamed = db.Column(db.Integer)
    profile_picture = db.Column(db.String(20), nullable=False, default='static/Default_pfp.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
    def __init__(self) -> None:
        super().__init__()

    def set_country(self, country):
        self.country = country

    def update_games_played(self):
        self.games_played += 1
    
    def set_profile_picture(self, path):
        self.profile_picture = cv2.imread(str(path))


    

