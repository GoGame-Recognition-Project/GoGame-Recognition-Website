from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

def initialize_app(app):
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)


if __name__ == '__main__':
<<<<<<< HEAD
    initialize_app(app)
=======
    app = create_app()        
>>>>>>> 8b951ceb96b9ef8c200eed3957b8f1a0ec5a94f5
    app.run(debug=True)
