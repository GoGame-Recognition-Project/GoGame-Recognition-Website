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
    
# @app.route('/video_feed')
# def video_feed():
#     """
#     Route to send the video stream 
#     """
#     print("in video feed")
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# def end_camera():
#     """stop the camera """
#     global camera
#     camera.release()

# def open_camera():
#     """open the camera """
#     global camera
#     camera = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)


# @app.route('/cam', methods=['POST', 'GET'])
# def getval():
#     """
#         Route to send the video stream 
#     """
#     global disabled_button, transparent_mode
    
#     transparent_mode = False
 
#     try:
#         k = request.form['psw1']
#         if k == '0':
#             open_camera()
#             if camera.read()[0]:
#                 New_game()
#                 disabled_button = 'start-button'
#         elif k == '1':
#             end_camera()
#             disabled_button = 'stop-button'
#     except Exception:
#         print("Exception: Page can not be refreshed")
    
    
#     return render_template('partie.html', disabled_button=disabled_button)

# @app.route('/t', methods=['POST', 'GET'])
# def getvaltransparent():
#     """
#     Route to send the video stream 
#     """
#     global disabled_button, transparent_mode
    
#     transparent_mode = True
#     try:
#         k = request.form['psw1']
#         if k == '0':
#             open_camera()
#             if camera.read()[0]:
#                 New_game(True)
#                 disabled_button = 'start-button'
#         elif k == '1':
#             end_camera()
#             disabled_button = 'stop-button'
#     except Exception:
#         print("Exception: Page can not be refreshed")
        
#     return render_template('transparent.html', disabled_button=disabled_button)

# @app.route('/game', methods=['POST'])
# def getval2():
#     """
#         Change the current move
#     """
#     global transparent_mode
    
#     transparent_mode = False
    
#     i = request.form['psw2']
#     if i =='2':
#         go_game.go_visual.initial_position()
#     elif i == '3':
#         go_game.go_visual.previous()
#     elif i == '4':
#         go_game.go_visual.next()
#     elif i == '5':
#         go_game.go_visual.final_position() 
#     print(i)   
#     return render_template('partie.html', disabled_button=disabled_button)

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

# @app.route('/rules', methods=['POST'])
# def handle_rules():
#     """
#         Check if we want to apply rules, still not implemented
#     """
#     global rules_applied, transparent_mode
    
#     transparent_mode = False
    
#     rules_applied = request.form['psw3']
#     if rules_applied == "True":
#         go_game.set_transparent_mode(False)
#         rules_applied = "False"
#     else : 
#         go_game.set_transparent_mode(True)
#         print("########pas de regles")
#         rules_applied = "True"
#     return render_template('partie.html', disabled_button=disabled_button)

# @app.route('/change_place', methods=['POST'])
# def change_place():
#     """
#         Route to get the piece that we want to change its position
#         """
#     global transparent_mode
    
#     transparent_mode = False
    
#     old_pos = request.form['input1']
#     new_pos = request.form['input2']
#     try:
#         go_game.correct_stone(old_pos,new_pos)
#     except Exception as e:
#         message = "L'erreur est "+str(e)
#     return render_template('partie.html', disabled_button=disabled_button)

# @app.route('/get_sgf_txt')
# def get_sgf_txt():
#     """
#         Route which returns the sgf text to be uploaded
#         """
#     global sgf_text
#     return sgf_text

@app.route('/upload', methods=['POST'])
def process():
    """
        Route which enables us to save the sgf text
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

# @app.route('/undo', methods=['POST'])
# def undo():
#     """
#     undo last played move
#     """
#     global transparent_mode
    
#     transparent_mode = False
    
#     go_game.delete_last_move()
#     return render_template("partie.html")
    
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
