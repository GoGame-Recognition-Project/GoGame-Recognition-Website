import threading
import copy
from ultralytics import YOLO
from GoGame import *
from GoBoard import *
from GoVisual import *
from flask import Flask, render_template, Response, request, send_file
import cv2
import base64

cam_index = 0

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  



model = YOLO('model.pt')

usual_message = "La caméra est bien fixée et tout est Ok"
message = "Rien n'a encore été lancé "
# disabled_button = 'stop-button'


ProcessFrame = None
Process = True
initialized = False
sgf_text = None
empty_board = cv2.imread("static/empty_board.jpg")
game_plot = empty_board
process_thread = None
go_game = None
transparent_mode = False


def New_game(transparent_mode=False):
    
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
            message = "Erreur : "+str(e)
                
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

# # def end_camera():
# #     global process_thread, camera_running, disabled_button
# #     if camera_running:
# #         process_thread.join()  # Wait for the thread to finish before stopping
# #         camera_running = False
# #         disabled_button = 'stop-button'   # Define the ID of the button to desactivate

# # def open_camera():
# #     """Open the camera"""
# #     global camera, process_thread, disabled_button, camera_running
# #     if not camera_running:
# #         camera = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
# #         process_thread = threading.Thread(target=processing_thread, args=(camera,))
# #         process_thread.start()
# #         camera_running = True
# #         disabled_button = 'start-button'  # Define the ID of the button to desactivate

@app.route('/')
def index():
    """Route to display HTML page"""
    return render_template('Home.html')

@app.route('/home')
def home():
    """Route to display HTML page"""
    return render_template('Home.html')

@app.route('/update')
def afficher_message():
    """
        Route to update the image and the message to display 
        
        Returns:
            message
            image
    """

    return {'message': message, 'image' : generate_plot()}

# def generate_frames():
#     """
#         Generate an image from the video stream
        
#         Returns:
#             Image
#     """
#     global ProcessFrame, camera
#     while True:  
#         try:
#             success, frame = camera.read()  # Read the image from the camera
#             if not success:
#                 break
            
#             else:
#                 ProcessFrame = copy.deepcopy(frame)
#                 _, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#         except Exception:
#             print('Exception: Camera not detected')
#             break
    




@app.route('/sgf_controls')
def getval3():
    """
        Change the current move
    """
    global transparent_mode
    
    transparent_mode = False
    
    i = request.form['psw2']
    if i =='2':
        go_game.go_visual.initial_position()
    elif i == '3':
        go_game.go_visual.previous()
    elif i == '4':
        go_game.go_visual.next()
    elif i == '5':
        go_game.go_visual.final_position() 
    print(i)   
    # return send_file()
    # return render_template('sgf.html', disabled_button=disabled_button)


@app.route('/upload', methods=['POST'])
def process():
    """
        Route which enables us to load the sgf text
        """
    global transparent_mode
    
    transparent_mode = False
    file = request.files['file']
    file_path = file.filename
    try:
        go_game.go_visual.load_game_from_sgf(file_path)
        message = "Le fichier a été correctement chargé"
    except Exception as e:
        message = "L'erreur est "+str(e)
    

    return render_template('sgf.html')

@app.route('/credit')
def credit():
    """
        Route to get to the credit page
        """
    return render_template("credits.html")


    
@app.route('/historique')
def historique():
    """
        Route to get to the summary page
    """
    return render_template("Historique.html")


@app.route('/game')
def game():
    """
    Route to get to the streaming page in game mode
    """
    global transparent_mode
    
    transparent_mode = False

    return render_template("game.html")

@app.route('/transparent')
def transparent():
    """
        Route to get to the streaming page in transparent mode
        """
    go_game.set_transparent_mode(True)
    global transparent_mode
    
    transparent_mode = False
    return render_template("transparent.html")

@app.route('/sgf')
def sgf():
    """
        Route to get to the streaming page in transparent mode
        """
    global transparent_mode
    
    transparent_mode = False
    return render_template("sgf.html")



if __name__ == '__main__':
    New_game()
    # process_thread = threading.Thread(target=processing_thread, args=())
    # process_thread.start()
    app.run(debug=True)
    
# %%
