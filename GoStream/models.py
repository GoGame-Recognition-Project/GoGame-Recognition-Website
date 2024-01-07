from flask_login import UserMixin, login_manager
from GoStream.__init__ import db, login_manager, app
from itsdangerous import TimedSerializer as Serializer



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
    profile_picture = db.Column(db.String(20), nullable=False, default='static/profile_pics/Default_pfp.png')

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

    

