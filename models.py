from __init__ import db
from flask_login import UserMixin
import cv2


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
    profile_picture = cv2.imread("static/Default_pfp.png")

    def __init__(self) -> None:
        super().__init__()

    def set_country(self, country):
        self.country = country

    def update_games_played(self):
        self.games_played += 1
    
    def set_profile_picture(self, path):
        self.profile_picture = cv2.imread(str(path))


    

