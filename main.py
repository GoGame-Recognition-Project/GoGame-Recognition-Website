from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import Flask, render_template, Response, request, jsonify, flash, redirect, url_for
from forms import RegistrationForm, LoginForm
from flask_login import login_required, current_user
import cv2
import base64

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret-key-goes-here'

cam_index = 0

model = YOLO('model.pt')

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
                game_plot = go_game.initialize_game(ProcessFrame)
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
    global sgf_text
    return sgf_text

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

@app.route('/profile')
def profile():
    return render_template('profile.html', name=current_user.name)
 



@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', title='signup', form=form)

@app.route("/logout")
def logout():
    return "aaaa"

if __name__ == '__main__':
    app.run(debug=True)
