from flask_login import UserMixin, login_manager
from datetime import datetime
from __init__ import db, login_manager, app
from itsdangerous import URLSafeTimedSerializer as Serializer



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
    profile_picture = db.Column(db.String(20), nullable=False, default='Default_pfp.png')
    streamed_games = db.relationship('StreamedGame', backref='streamer', lazy=True)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_picture}')"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    class StreamedGame(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        Black = db.Column(db.String(100), nullable=False)
        White = db.Column(db.String(100), nullable=False)
        Tournament = db.Column(db.String(100), nullable=False)
        date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        sgf = db.Column(db.Text, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

        def __repr__(self):
            return f"Post('{self.Black}', {self.White}')"

