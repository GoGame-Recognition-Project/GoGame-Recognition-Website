from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import render_template, Response, request, jsonify, Blueprint
import cv2
import base64
from __init__ import db

main = Blueprint('main', __name__)

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
SESSION_IS_OPEN = True

def new_game(transparent_mode=False):
    
    global go_game, initialized, game_plot
    game = sente.Game()
    go_visual = GoVisual(game)
    go_board = GoBoard(model)
    go_game = GoGame(game, go_board, go_visual, transparent_mode)
    game_plot = empty_board
    initialized = False

def processing_thread():
    """
        Process the detection algorithm
        
        Update:
            game_plot, sgf_text
        Send error to message if there is one
        """
    
    global ProcessFrame, game_plot, message, initialized, sgf_text

    if not ProcessFrame is None:
        try:
            if not initialized:
                game_plot = go_game.initialize_game(ProcessFrame)
                initialized = True
                message = usual_message
            else:    
                game_plot, sgf_text = go_game.main_loop(ProcessFrame)
                message = usual_message
        except Exception as e:
            message = "Error : " + str(e)
                
def generate_plot():
    """
        Generate a plot representing the game
        
        Returns:
            Image
        """
    global game_plot
    
    processing_thread()
    if transparent_mode:
        to_plot = game_plot
    else:
        to_plot = go_game.go_visual.current_position()
    
    _, img_encoded = cv2.imencode('.jpg', to_plot)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    return img_base64

def generate_frames():
    """
        Generate an image from the video stream
        
        Returns:
            Image
    """
    global ProcessFrame, camera, SESSION_IS_OPEN
    while SESSION_IS_OPEN:
        print("inside while loop")
        try:
            success, frame = camera.read()  # Read the image from the camera
            if not success:
                break
            
            else:
                ProcessFrame = copy.deepcopy(frame)
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception:
            print('Exception: Camera not detected')
            # break

@main.route('/video_feed')
def video_feed():
    """
    Route to send the video stream 
    """
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/close_camera', methods=["POST"])
def close_camera():
    """stop the camera """
    global camera, STOPPED, SESSION_IS_OPEN
    
    data = request.data.decode('utf-8')
    print(data)
    if data == 'false':
        SESSION_IS_OPEN = False
    else:
        SESSION_IS_OPEN = True

    camera.release()
    STOPPED = True
    print("the camera has been closed")
    return Response(status=204)

@main.route('/open_camera', methods=["POST"])
def open_camera():
    """open the camera """
    global camera, STARTED
    camera = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    success, frame = camera.read()
    if success:
        print("camera started")
        STARTED = True
        new_game()
        return Response(status=204)
    print("camera not opened")
    return Response(status=502)


@main.route('/start_play', methods=['POST'])
def start_play():
    new_game()
    return Response(status=204)

@main.route('/play_stone', methods=['POST'])
def play_stone():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    go_game.play_a_move(x, y)

    return Response(status=204)

@main.route('/turn', methods=['GET'])
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
    
@main.route('/resign', methods=['POST'])
def resign():
    global resigned
    go_game.resign()
    resigned = True
    return Response(status=204)

@main.route('/win', methods=['GET'])
def winner():
    return {"winner": str(go_game.get_winner())}

@main.route('/update_state')
def update_state():
    """
        Route to update the image and the message to display 
        
        Returns:
            message
            image
    """
    global message

    return {'message': message, 'image' : generate_plot()}

@main.route('/get_config', methods=['GET'])
def get_config():
    global STARTED, STOPPED
    config_set = {'STARTED': STARTED, 'STOPPED': STOPPED}
    return jsonify(config_set)

@main.route('/controls', methods=["POST"])
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

@main.route('/upload', methods=['POST'])
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

@main.route('/undo', methods=['POST'])
def undo():
    """
    Undo last played move
    """

    go_game.delete_last_move()
    
    return Response(status=204)

@main.route('/')
def index():
    """Route to display HTML page"""
    return render_template('Home.html')

@main.route('/home')
def home():
    """Route to display HTML page"""
    return render_template('Home.html')

@main.route('/game')
def game():
    """
    Route to get to the streaming page in game mode
    """
    if not initialized:
        try:
            camera.release()
        except:
            pass
    return render_template("game.html")
@main.route('/play')
def play():
    """
    Route to get to the streaming page in game mode
    """
    return render_template("play.html")
@main.route('/transparent')
def transparent():
    """
        Route to get to the streaming page in transparent mode
        """
    return render_template("game.html")

@main.route('/sgf')
def sgf():
    """
        Route to get to the streaming page in transparent mode
    """

    return render_template("sgf.html")

@main.route('/historique')
def historique():
    """
        Route to get to the summary page
    """
    return render_template("Historique.html")

@main.route('/profile')
def profile():
    return render_template('profile.html')

