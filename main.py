from ultralytics import YOLO
from GoStreamDetection.GoGame import *
from GoStreamDetection.GoBoard import *
from GoStreamDetection.GoVisual import *
from flask import Flask, render_template, Response, request, jsonify
import cv2
import base64
from __init__ import app

cam_index = 0

model = YOLO('GoStreamDetection/model.pt')

usual_message = "Everything is well detected"
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
    """
    Initialize a new game of Go by intializing all three instances of GoGame, GoVisual and GoBoard.
    
    Args:
        transparent_mode (bool): If True, the board will be transparent.
        
    Returns:
        None
    """
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
                game_plot, sgf_text = go_game.main_loop(ProcessFrame)
                message = usual_message
        except Exception as e:
            message = str(e)
                
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
    """
    Initializes a new game of Go.
    
    Args:
        None
        
    Returns:
        None
    """
    new_game()
    return Response(status=204)

@app.route('/set_rules', methods=["POST"])
def set_rules():
    """
    Button to set transparent/free or game mode.
    
    Args:
        None
        
    Returns:
        Response: A response object with status code 204 if successful, or status code 502 if there is an error.
    """
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
    """
    Button to start a new game of Go by initializing GoGame, GoBoard and GoVisual instances.
    
    Args:
        None
        
    Returns:
        Response: A response object with status code 204.
    """
    new_game()
    return Response(status=204)

@app.route('/play_stone', methods=['POST'])
def play_stone():
    """
    Play a stone on the Go board. Takes the coordinates from a click on the board and sends them to GoGame.
    
    Args:
        None
        
    Returns:
        Response: A response object with status code 204.
    """
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    go_game.play_a_move(x, y)

    return Response(status=204)

@app.route('/turn', methods=['GET'])
def show_turn():
    """
    Return whose turn to play if the game is still not over. Else, return who won, precising if it's a win by opponent resigning.
    
    Args:
        None
        
    Returns:
        dict: A dictionary containing the current turn of the game.
    """
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
def correct():
    """
    Correct the position of a stone in a Go game.
    It receives a POST request with JSON data containing the selected stone and target stone.

    Args:
        None. The function gets data from the POST request.

    Returns:
        A Response object with a status code. 
        204: The correction was successful.
        502: The correction was not possible or an error occurred.

    Raises:
        Exception: An error occurred while correcting the stone position.
    """
    
    data = request.get_json()

    if 'selectedStone' in data:
        try:
            selected_stone = data['selectedStone']
            target_stone = data['targetStone']

            go_game.correct_stone(selected_stone, target_stone)
            return Response(status=204)
        except Exception as e:
            print("Correction is not possible")
            return Response(status=502)
    return Response(status=502)
    
@app.route('/resign', methods=['POST'])
def resign():
    """
    This function handles the resignation of a player in a Go game.
    It receives a POST request and calls the resign method of the go_game object.
    If the resignation is successful, it sets the global variable 'resigned' to True and returns a 204 status code.
    If an error occurs, it returns a 502 status code.

    Args:
        None. The function does not take any arguments.

    Returns:
        A Response object with a status code. 
        204: The resignation was successful.
        502: An error occurred during the resignation process.

    """
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
    """
    This function returns the winner of a Go game.
    It receives a GET request and calls the get_winner method of the go_game object.
    It returns a dictionary with the key 'winner' and the value being the winner of the game.

    Args:
        None. The function does not take any arguments.

    Returns:
        A dictionary with the key 'winner' and the value being the winner of the game.
    """
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
    """
    This function returns the configuration set of a Go game.
    It receives a GET request and returns a dictionary with the game's configuration set.
    The configuration set includes the states 'STARTED', 'STOPPED', 'PAUSED', and 'QUIT'.

    Args:
        None. The function does not take any arguments.

    Returns:
        A dictionary with the game's configuration set.
    """
    global STARTED, STOPPED
    config_set = {'STARTED': STARTED, 'STOPPED': STOPPED, "PAUSED": PAUSED, "QUIT": QUIT}
    return jsonify(config_set)

@app.route('/set_config', methods=['POST'])
def set_config():
    """
    This function sets the configuration of a Go game.
    It receives a POST request with JSON data containing the game's configuration set.
    The configuration set includes the states 'STARTED', 'STOPPED', 'PAUSED', and 'QUIT'.
    If the configuration is set successfully, it returns a 204 status code.

    Args:
        None. The function gets data from the POST request.

    Returns:
        A Response object with a status code. 
        204: The configuration was set successfully.

    """
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

@app.route('/stream')
def stream():
    """
    Route to get to the streaming page in game mode
    """
    return render_template("stream.html")


@app.route('/play')
def play():
    """
    Route to get to the streaming page in game mode
    """
    new_game()
    return render_template("play.html")

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


