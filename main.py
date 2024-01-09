from ultralytics import YOLO
from GoStreamDetection.GoGame import *
from GoStreamDetection.GoBoard import *
from GoStreamDetection.GoVisual import *
from flask import Flask, render_template, Response, request, jsonify, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_login import login_required, current_user
from flask_mail import Message
import cv2
import base64
from flask_sqlalchemy import SQLAlchemy
from models import User
from __init__ import app, db, bcrypt, mail
import secrets
from PIL import Image
import os




cam_index = 0

model = YOLO('GoStreamDetection/model.pt')

usual_message = "Everything is OK"
message = "Nothing is being streamed for the moment"
defaut_turn = "No game is being played at the moment"
resigned = False

ProcessFrame = None
Process = True
initialized = False
sgf_text = None
empty_board = cv2.imread("static/empty_board.jpg")
game_plot = empty_board
process_thread = None
go_game = None
transparent_mode = False
camera = None

STARTED = False
STOPPED = False
PAUSED = False
QUIT = False

def new_game(transparent_mode=False):
    
    global go_game, initialized, game_plot
    game = sente.Game()
    go_visual = GoVisual(game)
    go_board = GoBoard(model)
    go_game = GoGame(game, go_board, go_visual, transparent_mode)
    game_plot = empty_board
    initialized = False

def processing_thread(ProcessFrame=None):
    """
        Process the detection algorithm
        
        Update:
            game_plot, sgf_text
        Send error to message if there is one
        """
    
    global game_plot, message, initialized, sgf_text

    if not ProcessFrame is None:
        try:
            if not initialized:
                game_plot, sgf_text = go_game.initialize_game(ProcessFrame)
                initialized = True
                message = usual_message
            else:    
                game_plot, sgf_text = go_game.app_loop(ProcessFrame)
                message = usual_message
        except Exception as e:
            message = "Error : " + str(e)
                
def generate_plot(frame=None):
    """
        Generate a plot representing the game
        
        Returns:
            Image
        """
    global game_plot

    processing_thread(frame)
    ###### condition deja implementé dans gogame? A revoir
    if transparent_mode and not frame is None:
        to_plot = game_plot
    else:
        to_plot = go_game.go_visual.current_position()
    
    _, img_encoded = cv2.imencode('.jpg', to_plot)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    return img_base64

@app.route('/initialize_new_game')
def initialize_new_game():
    
    new_game()
    return Response(status=204)

@app.route('/set_rules', methods=["POST"])
def set_rules():
    global transparent_mode, go_game
    try:
        data = request.get_json()
        transparent_mode = data["TRANSPARENT_MODE"]
        go_game.set_transparent_mode(transparent_mode)
        return Response(status=204)
    except Exception as e:
        return Response(status=502)

@app.route('/start_play', methods=['POST'])
def start_play():
    new_game()
    return Response(status=204)

@app.route('/play_stone', methods=['POST'])
def play_stone():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    go_game.play_a_move(x, y)

    return Response(status=204)

@app.route('/turn', methods=['GET'])
def show_turn():

    global turn 
        
    if go_game.is_over() and resigned == False:
        turn = str(go_game.get_winner()) + " wins."
        
    elif go_game.is_over() and resigned == True:
        if str(go_game.get_winner()) == "BLACK":
            turn = "WHITE resigned. BLACK wins."
        elif str(go_game.get_winner()) == "WHITE":
            turn = "BLACK resigned. WHITE wins."
    else:
        turn = str(go_game.current_turn()) + " to play"

    return {'turn': turn}

@app.route('/correct', methods=['POST'])
def correct(old_pos, new_pos):
    go_game.correct_stone_js(old_pos, new_pos)
    return Response(status=204)
    
@app.route('/resign', methods=['POST'])
def resign():
    global resigned
    try:
        go_game.resign()
        resigned = True
        return Response(status=204)
    except Exception as e:
        print(e)
        return Response(status=502)
    

@app.route('/win', methods=['GET'])
def winner():
    return {"winner": str(go_game.get_winner())}


@app.route('/update_state', methods=["POST"])
def update_state():
    """
        Route to update the image and the message to display 
        
        Returns:
            message
            image
    """
    global message

    data = request.get_json()
   
    if 'image' in data:
        try:
            image_data_url = data['image']
            # Extract the base64-encoded image data
            _, image_base64 = image_data_url.split(',')
            # if image_base64:
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decode the image using OpenCV
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            return {'message': message, 'image' : generate_plot(frame)}
        except Exception as e:
            print(e)
            return Response(status=502)
    else:
        return {'message': message, 'image' : generate_plot()}

@app.route('/get_config', methods=['GET'])
def get_config():
    global STARTED, STOPPED
    config_set = {'STARTED': STARTED, 'STOPPED': STOPPED, "PAUSED": PAUSED, "QUIT": QUIT}
    return jsonify(config_set)

@app.route('/set_config', methods=['POST'])
def set_config():
    global STARTED, STOPPED, PAUSED, QUIT
    
    data = request.get_json()
    
    STARTED = data['STARTED']
    STOPPED = data['STOPPED']
    PAUSED = data['PAUSED']
    QUIT = data['QUIT']
    
    return Response(status=204)

@app.route('/controls', methods=["POST"])
def controls():
    """
        Change the current move
    """
    control = request.data.decode('utf-8')
    if control == "initial":
        go_game.go_visual.initial_position()
    elif control == "previous":
        go_game.go_visual.previous()
    elif control == "next":
        go_game.go_visual.next()
    elif control == "last":
        go_game.go_visual.final_position()
    else:
        return Response(status=500)
    print("Control success")
    
    return Response(status=204)

@app.route('/upload', methods=['POST'])
def process():
    """
        Route which enables us to load the sgf text
    """
    file = request.files['file']
    file_path = file.filename
    try:
        new_game()
        go_game.go_visual.load_game_from_sgf(file_path)
        message = "Uploaded"
    except Exception as e:
        message = "Error:" + str(e)

    return Response(status=204)

@app.route('/undo', methods=['POST'])
def undo():
    """
    Undo last played move
    """
    try:
        go_game.delete_last_move()
        return Response(status=204)
    except Exception as e:
        print(e)
        return Response(status=502)

@app.route('/get_sgf_txt')
def get_sgf_txt():
    """
        Route which returns the sgf text to be uploaded
        """

    return {"sgf": go_game.get_sgf()}

@app.route('/')
def index():
    """Route to display HTML page"""
    return render_template('Home.html')

@app.route('/home')
def home():
    """Route to display HTML page"""
    return render_template('Home.html')

@app.route('/game')
def game():
    """
    Route to get to the streaming page in game mode
    """
    return render_template("game.html")

@app.route('/choice')
def choice():
    """
    Route to get to the streaming page in game mode
    """
    return render_template("choice.html")

@app.route('/play')
def play():
    """
    Route to get to the streaming page in game mode
    """
    new_game()
    return render_template("play.html")
@app.route('/transparent')
def transparent():
    """
        Route to get to the streaming page in transparent mode
        """
    return render_template("game.html")

@app.route('/sgf')
def sgf():
    """
        Route to get to the streaming page in transparent mode
    """
    new_game()
    return render_template("sgf.html")

@app.route('/historique')
def historique():
    """
        Route to get to the summary page
    """
    return render_template("Historique.html")

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@login_required
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_picture = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for('static', filename='profile_pics/' + current_user.profile_picture)
    return render_template('profile.html', title='Account',
                           profile_picture=profile_picture, form=form)
 

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

with app.app_context():
    db.create_all()
