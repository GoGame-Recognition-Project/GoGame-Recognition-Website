import numpy as np
import sente



class GoGame:
    """
    GoGame is the class responsible for managing the game, comparing frames and finding the newly played move
    """

    def __init__(self, game, board_detect, go_visual, transparent_mode):
        """
        Constructor method for the GoGame class.

        Parameters:
        -----------
        game : Sente
            The game instance associated with the GoGame.

        board_detect : GoBoard
            The GoBoard instance responsible for board detection.

        go_visual : GoVisual
            The GoVisual instance for visualizing the Go board.

        Attributes:
        -----------
        moves : list
            List to store the moves made in the game.

        board_detect : GoBoard
            GoBoard instance responsible for board detection.

        go_visual : GoVisual
            GoVisual instance for visualizing the Go board.

        game : Sente
            Game instance associated with the GoGame.

        current_player : None
            Placeholder for the current player in the game.

        """
        self.game = game
        self.board_detect = board_detect
        self.go_visual = go_visual
        self.current_player = None
        self.transparent_mode = transparent_mode
        self.moves = []
    
    def set_transparent_mode(self, bool_):
        self.transparent_mode = bool_


    def initialize_game(self, frame, current_player="BLACK"):
        """
        Initialize the game state based on the provided frame and current player.

        This function resets the moves, sets the current player, processes the frame using the board detection module,
        populates the game based on the detected stones, and adjusts the active player if needed.

        Args:
            frame: The frame to initialize the game.
            current_player (str): The current player to set, either "BLACK" or "WHITE".

        Returns:
            Tuple: A tuple containing the current position on the board and the SGF representation of the game.
        """
        # Reset moves and set the current player
        self.moves = []
        self.current_player = current_player

        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)
        
        if self.transparent_mode:
            detected_state = self.transparent_mode_moves()
            return self.go_visual.draw_transparent(detected_state), None
        else:
            # Populate the game based on the detected stones
            self.auto_play_game_moves()

            # Check and adjust the active player if needed
            if not self.game.get_active_player().name == current_player:
                self.game.pss()

            return self.go_visual.current_position(), self.get_sgf()
    
    
    def main_loop(self, frame):
        """
        Main loop for processing frames and updating the game state.

        This function takes a frame as input, processes it using the board detection module,
        and returns the current position on the board along with the SGF representation of the game.

        Args:
            frame: The frame to be processed.

        Returns:
            Tuple: A tuple containing the current position on the board and the SGF representation of the game.
        """
        # Set the current frame for the instance
        self.frame = frame

        # Process the frame using the board detection module
        self.board_detect.process_frame(frame)

        if self.transparent_mode:
            detected_state = self.transparent_mode_moves()
            return self.go_visual.draw_transparent(detected_state), None
        else:
            self.define_new_move()        
            return self.go_visual.current_position(), self.get_sgf()
    
    def transparent_mode_moves(self):
        return np.transpose(self.board_detect.get_state(), (1, 0, 2))
        

    def play_move(self, x, y, stone_color):
        """
        Play a move in the game at the specified position.

        Args:
            x (int): The x-coordinate of the move.
            y (int): The y-coordinate of the move.
            stone_color (int): The color of the stone to be played (1 for black, 2 for white).

        Returns:
            None
        """
        # Determine the color of the stone based on the stone_color parameter
        color = "white" if stone_color == 2 else "black"

        try:
            # Attempt to play the move in the game using sente.stone
            self.game.play(x, y, sente.stone(stone_color))

        except sente.exceptions.IllegalMoveException as e:
            # Handle different types of illegal move exceptions and raise a custom Exception with details
            error_message = f"[GoGameException]: A violation of go game rules has been found in position {x}, {y}\n"

            if "self-capture" in str(e):
                raise Exception(error_message + f" --> {color} stone at this position results in self-capture")
            if "occupied point" in str(e):
                raise Exception(error_message + " --> The desired move lies on an occupied point")
            if "Ko point" in str(e):
                raise Exception(error_message + " --> The desired move lies on a Ko point")
            if "turn" in str(e) and "It is not currently" in str(e):
                raise Exception(error_message + f"It is not currently {color}'s turn\n")

            # If the exception doesn't match any specific cases, raise a general exception with the original message
            raise Exception(error_message + str(e))

            
    
    def define_new_move(self):
        """
        Define a new move based on the difference between the current game state and the detected state.

        This function compares the current state of the game with the detected state from the board detection module,
        identifies the new black and white stone positions, and plays moves accordingly in the game.

        Returns:
            None
        """
        # Get the detected state from the board detection module
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))

        # Get the current state of black and white stones in the game
        current_state = self.game.numpy(["black_stones", "white_stones"])

        # Calculate the difference between the detected state and the current state
        difference = detected_state - current_state

        # Identify the indices of newly added black and white stones
        black_stone_indices = np.argwhere(difference[:, :, 0] == 1)
        white_stone_indices = np.argwhere(difference[:, :, 1] == 1)

        # Handle the case where more than one stone was added
        if len(black_stone_indices) + len(white_stone_indices) > 1:
            print("[GoGame Log] - More than one stone was added!")
            return

        # Play a move for a newly added black stone
        if len(black_stone_indices) != 0:
            self.play_move(black_stone_indices[0][0] + 1, black_stone_indices[0][1] + 1, 1)  # 1 is black_stone
            self.moves.append(('B', (black_stone_indices[0][0], 18 - black_stone_indices[0][1])))
            print(f"[GoGame Log] - Black stone was played at ({black_stone_indices[0][0], 18 - black_stone_indices[0][1]})")
            return

        # Play a move for a newly added white stone
        if len(white_stone_indices) != 0:
            self.play_move(white_stone_indices[0][0] + 1, white_stone_indices[0][1] + 1, 2)  # 2 is white_stone
            self.moves.append(('W', (white_stone_indices[0][0], 18 - white_stone_indices[0][1])))
            print(f"[GoGame Log] - White stone was played at ({white_stone_indices[0][0], 18 - white_stone_indices[0][1]})")
            return

        # Print a message if no moves were detected
        print("No new move detected!")

    
    def auto_play_game_moves(self):
        """
        Automatically populates the game board with moves based on the detected state.

        This function retrieves the detected state from the board detection module,
        identifies the indices of black and white stones, and plays moves for each player.

        Black stones are represented by player 1, and white stones are represented by player 2.
        After playing all black and white stones, the function passes a turn for each player.

        Returns:
            None
        """
        # Get the detected state from the board detection module
        detected_state = np.transpose(self.board_detect.get_state(), (1, 0, 2))

        # Identify the indices of black and white stones on the board
        black_stone_indices = np.argwhere(detected_state[:, :, 0] == 1)
        white_stone_indices = np.argwhere(detected_state[:, :, 1] == 1)

        # Play moves for black stones
        for stone in black_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 1)
            self.game.pss()

        # Pass a turn after playing all black stones
        self.game.pss()

        # Play moves for white stones
        for stone in white_stone_indices:
            self.play_move(stone[0] + 1, stone[1] + 1, 2)
            self.game.pss()

        # Pass a turn after playing all white stones
        self.game.pss()

    def correct_stone(self, old_pos, new_pos):
        """
        Manually correct the position of a stone on the board. 
        The first version (self.correct_stone) was supposed to be used when the user directly submits the positions of the stones.
        This second version was made when we started using JavaScript for the website and we could make correction more user friendly.

        This function corrects the position of a stone on the board by checking if the new position is already occupied,
        and then moving the stone to the new position
        while preserving the order of moves.

        Args:
            old_pos (tuple): The old position of the stone (e.g., (1, 1)).
            new_pos (tuple): The new position to correct the stone to (e.g., (19, 19)).

        Returns:
            None
        """

        new_x, new_y = new_pos
        old_x, old_y = old_pos

        # Iterate through the moves to check if the new position is already occupied
        for i in range(len(self.get_moves())):
            
            if int(self.get_moves()[i].get_x()+1) == new_x and int(self.get_moves()[i].get_y()+1) == new_y:
                return
            
            else:
                # If the old position is found, correct the stone's position
                if int(self.get_moves()[i].get_x()+1) == old_x and int(self.get_moves()[i].get_y()+1) == old_y:
                    deleted_moves = self.get_moves()[i - len(self.get_moves()):]
                    self.game.step_up(len(self.get_moves()) - i)
                    self.game.play(new_x, new_y)
                    deleted_moves.pop(0)
                    for move in deleted_moves:
                        x, y, color = move.get_x()+1, move.get_y()+1, move.get_stone().name
                        self.game.play(x,y)

    def delete_last_move(self):
        """
         Delete the last move in the game sequence.

        This function steps up the game to remove the last move from the game sequence.

        Returns:
        None
        """
        
        self.game.step_up()
    
    def play_a_move(self, x, y):
        """
         Delete the last move in the game sequence.

        This function steps up the game to remove the last move from the game sequence.

        Args:
            x (int): the x coordinate of the desired move
            y (int): the y coordinate of the desired move

        Returns:
        None
        """
        self.game.play(x, y)
    
    def current_turn(self):
        """
        Get the name of the active player.

        This function returns the name (BLACK or WHITE) of the player whose turn it is in the game.

        Returns:
            str: The name of the active player.
        """
        return self.game.get_active_player().name
    
    def is_over(self):
        """
        Check if the game is over.

        This function checks if the game has ended.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.game.is_over()
    
    def get_winner(self):
        """
        Get the name of the winner.

        This function returns the name of the player who won the game.

        Returns:
            str: The name of the winner.
        """
        return self.game.get_winner().name
    
    def game_results(self):
        """
        Get the results of the game.

        This function returns the score of the game.

        Returns:
            dict: The results of the game.
        """
        results = self.game.score()
        return results
    
    def resign(self):
        """
        Resign from the game.

        This function allows a player to resign from the game.

        Returns:
            str: A message indicating the player has resigned.
        """
        return self.game.resign()

    def get_moves(self):
        """
        Remove pass move; when we use game.pss(), a move named "u19" is added to the sequence. 

        Returns:
        --------
        moves: List
            Cleaned sequence
        """
        moves = []
        for move in self.game.get_sequence():
            if move.get_x() == 19 and move.get_y() == 19:
                continue
            moves.append(move)
        return moves


    def get_sgf(self):
        """
        Get the SGF (Smart Game Format) representation of the current game.

        Returns:
            str: The SGF representation of the game.
        """
        # Use the sente.sgf.dumps function to convert the game to SGF format
        return sente.sgf.dumps(self.game)

