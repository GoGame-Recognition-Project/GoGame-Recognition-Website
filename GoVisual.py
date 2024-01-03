import numpy as np
import cv2
import sente


class GoVisual:
    """
    class GoVisual: 
    creates a go game visual representation given a Sente game provided by the Sente class
    can navigate through the game using methods such as previous or next while managing the game's logic
    The same instance of Sente is used in the GoGame class, which means it gets automatically updated each move 
    and the attributes of the class get updated via the initialize_param function
    """

    def __init__(self, game):
        """
        Constructor method for GoBoard.

        Parameters:
        -----------
        game : Sente
            the game instance created by Sente and updated by GoGame 
        """
        self.game = game
        self.board_size = 19
        self.last_move = None
        self.cursor = len(self.get_moves())
        self.track_progress = True    
    

    def get_stones(self, board):
        """
        Count and collect positions of the stones on the board.

        Parameters:
        -----------
        moves : list
            A Sequence of moves provided by Sente

        """
        black_stones = []
        white_stones = []
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                if np.array_equal(board[i, j], [1, 0]):  # Black stone
                    black_stones.append((i, j))
                elif np.array_equal(board[i, j], [0, 1]):  # White stone
                    white_stones.append((i, j))
        return black_stones, white_stones

    def update_param(self):
        """
        Initialize parameters of the GoBoard based on the specified number of moves.
        The method should keep track of all the "lost" or deleted moves while using the self.previous method 
        and ensure we're at the right current number of moves.
        The use of both "moves" and "board" is necessary: moves contains the order of stones, which is crucial since we want to navigate through the game
        while board omit the stones that shouldn't be showed (captured, illegal stones).

        Parameters:
        -----------
        nb_moves : int, optional
            Number of moves to initialize the board with. Default is 0.
            Can be positive (used in self.next()) or negative (self.previous()).

        Returns:
        -----------
            None
        """
        deleted_moves = []
        if self.cursor - len(self.get_moves()) != 0:
            deleted_moves = self.get_moves()[self.cursor - len(self.get_moves()):]
        self.game.step_up(len(self.get_moves()) - self.cursor)
        black_stones, white_stones = self.get_stones(self.game.numpy(["black_stones", "white_stones"]))        
        
        if self.get_moves() != []:
            self.last_move = self.get_moves()[-1]

        for move in deleted_moves:
                x, y, color = move.get_x()+1, move.get_y()+1, move.get_stone().name
                self.game.play(x,y)
        return black_stones, white_stones

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
    
    def initial_position(self):
        """
        Display the initial position with the first move

        Returns:
        --------
        numpy array
            The resulted board drawn with only the first played move
        """
        self.track_progress = False
        self.cursor = 1

    def final_position(self):
        """
        Display the final position 

        Returns:
        --------
        numpy array
            The resulted board drawn with all the played moves 
        """
        self.track_progress = True
 

    def current_turn(self):
        """
        Display whose turn to play

        Returns:
        --------
        string
            The color of the current turn
        """
        if self.last_move.get_stone().name == 'BLACK':
            return 'WHITE' 
        elif self.last_move.get_stone().name == 'WHITE' or self.cursor == 0:
            return 'BLACK'
        
    def previous(self):
        """
        Display the previous position

        Returns:
        --------
        numpy array
            The board one move before the displayed position
        """
        self.track_progress = False
        if self.cursor > 1:
            self.cursor -= 1


    def next(self):
        """
        Display the next position

        Returns:
        --------
        numpy array
            The board one move after the displayed position
        """
        self.track_progress = False
        if self.cursor < len(self.get_moves()):
            self.cursor +=1
        
        if self.cursor == len(self.get_moves()):
            self.track_progress = True

    def current_position(self):
        """
        Display the current position

        Returns:
        --------
        numpy array
            The board
        """
        if self.track_progress:
            self.cursor = len(self.get_moves())

        black_stones, white_stones = self.update_param()
        return self.drawBoard(black_stones, white_stones)


    def drawBoard(self, black_stones, white_stones):
        """
        Draw the board of the Go game

        Parameters:
        -----------
        number_of_moves_to_show : int
            Define moves we want to plot on the board

        Returns:
        --------
        numpy array
            The resulted board 
        """
    
        square_size = 30
        circle_radius = 12
        
        #set up the board's background
        board =np.full(((self.board_size+1)*square_size, (self.board_size+1)*square_size, 3), (69, 166, 245), dtype=np.uint8)
        board2 = np.zeros((self.board_size, self.board_size))
        
        for i in range(1, self.board_size+1):
            # Vertical lines and letters
            cv2.line(board, (square_size*i, square_size), (square_size*i, square_size*(self.board_size)), (0, 0, 0), thickness=1)
            cv2.putText(board, chr(ord('A') + i-1), (square_size*i, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
            cv2.putText(board, chr(ord('A') + i-1), (square_size*i, 585), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

            # Horizontal lines and letters
            cv2.line(board, (square_size, square_size*i), (square_size*(self.board_size), square_size*i), (0, 0, 0), thickness=1)
            cv2.putText(board, str(i), (5, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
            cv2.putText(board, str(i), (580, square_size*i), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

        # Draw stones
        for stone in black_stones:
            row, col = stone
            board2[row, col] = 1
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(66, 66, 66), thickness=2) # draw the edge
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(0, 0, 0), thickness=-1) # draw the stone

        for stone in white_stones:
            row, col = stone
            board2[row, col] = 1
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(66, 66, 66), thickness=2) # draw the edge
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(255, 255, 255), thickness=-1) # draw the stone
        
        #setting the contour of the last move to a different color
        if self.last_move is not None:
            row, col, color = self.last_move.get_x(), self.last_move.get_y(), self.last_move.get_stone().name
            stone_color = (0, 0, 0) if color == 'BLACK' else (255, 255, 255)
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=(0,0,255), thickness=2) 
            cv2.circle(board, ((row+1)*square_size, (col+1)*square_size), circle_radius, color=stone_color, thickness=-1) 

        return board

    def load_game_from_sgf(self, sgf_url):
        """
        Load a game from an SGF (Smart Game Format) file.

        This function loads a game from the specified SGF file, plays the default sequence,
        and returns the current position on the board.
        This serves as intialization, to use the next/previous buttons, we should call and the show the output of self.current_position()

        Args:
            sgf_url (str): The URL or file path of the SGF file.

        Returns:
            Tuple: A tuple containing the current position on the board.
        """
        self.game = sente.sgf.load(sgf_url)
        self.game.play_sequence(self.game.get_default_sequence())
        return self.current_position()

    def draw_transparent(self, detected_state):
        """
        Draw the board without taking into account game rules. Show exactly what's on the board.
        This makes using previous and next impossible.

        Args:
            detected_state: numpy.ndarray
            the current state of the board: the stones and their positions stored in a 19x19x2 board like the sente.Board19
        
        Returns:
            numpy.ndarray
            The visual board to plot
        """
        self.last_move = None
        black_stones, white_stones = self.get_stones(detected_state)
        return self.drawBoard(black_stones, white_stones)
