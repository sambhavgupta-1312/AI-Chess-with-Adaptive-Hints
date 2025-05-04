import os
import pygame
from pygame.locals import *
from chess.piece import Piece
from chess.chess import Chess
from chess.utils import Utils
from chess.hint_manager import HintManager
from chess.tooltip import ChessTooltip
import copy
# Move the button back to the right side
SUGGEST_BUTTON_RECT = pygame.Rect(660, 100, 140, 40)  # x, y, width, height
class Game:
    def __init__(self):
        # screen dimensions
        screen_width = 800
        screen_height = 670
        # flag to know if game menu has been showed
        self.menu_showed = False
        # flag to set game loop
        self.running = True
        # base folder for program resources
        self.resources = "res"
 
        # initialize game window
        pygame.display.init()
        # initialize font for text
        pygame.font.init()

        # create game window
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        # title of window
        window_title = "Chess"
        # set window caption
        pygame.display.set_caption(window_title)
        self.board = self.create_starting_board()
        # get location of game icon
        icon_src = os.path.join(self.resources, "chess_icon.png")
        print(icon_src)
        # load game icon
        icon = pygame.image.load(icon_src)
        # set game icon
        pygame.display.set_icon(icon)
        # update display
        pygame.display.flip()
        # set game clock
        self.clock = pygame.time.Clock()
        
        # Initialize hint manager and tooltip
        self.hint_manager = HintManager()
        self.tooltip = ChessTooltip(position=(150, 150), size=(450, 250))
        
        # Position for hint UI controls (right side of screen again)
        # Reposition with more spacing to prevent overlapping
        self.hint_manager.create_ui_elements(650, 160, 120, 25, 15)
        
        # Flag to track if minimax suggested move is showing
        self.showing_minimax_suggestion = False

    def create_starting_board(self):
        # Returns a standard 8x8 chess board setup
        return [
            ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_knight",
             "white_rook"],
            ["white_pawn"] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ["black_pawn"] * 8,
            ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_knight",
             "black_rook"]
        ]
    def evaluate_board(self,board):
        # Simple material count evaluation
        piece_values = {
            'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 0
        }
        value = 0
        for row in board:
            for piece in row:
                if piece:
                    color, ptype = piece.split('_')
                    if color == 'white':
                        value += piece_values[ptype]
                    else:
                        value -= piece_values[ptype]
        return value

    def piece_location_to_board(self,piece_location):
        board = [[None for _ in range(8)] for _ in range(8)]
        for file_idx, file_char in enumerate('abcdefgh'):
            for rank in range(1, 9):
                piece = piece_location[file_char][rank][0]
                x = file_idx
                y = 8 - rank  # rank 8 is row 0, rank 1 is row 7
                if piece:
                    board[y][x] = piece
        return board

    def generate_legal_moves(self,board, color):
        moves = []
        direction = -1 if color == 'white' else 1  # White moves up, black down

        for y in range(8):
            for x in range(8):
                piece = board[y][x]
                if piece and piece.startswith(color):
                    ptype = piece.split('_')[1]

                    # PAWN
                    if ptype == 'pawn':
                        ny = y + direction
                        # Move forward
                        if 0 <= ny < 8 and board[ny][x] is None:
                            moves.append(((x, y), (x, ny)))
                            # Double move on first move
                            if (color == 'white' and y == 6) or (color == 'black' and y == 1):
                                ny2 = y + 2 * direction
                                if board[ny2][x] is None:
                                    moves.append(((x, y), (x, ny2)))
                        # Captures
                        for dx in [-1, 1]:
                            nx = x + dx
                            if 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target and not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))

                    # KNIGHT
                    elif ptype == 'knight':
                        knight_moves = [
                            (x + 1, y + 2), (x + 2, y + 1), (x + 2, y - 1), (x + 1, y - 2),
                            (x - 1, y - 2), (x - 2, y - 1), (x - 2, y + 1), (x - 1, y + 2)
                        ]
                        for nx, ny in knight_moves:
                            if 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None or not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))

                    # BISHOP
                    elif ptype == 'bishop':
                        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # ROOK
                    elif ptype == 'rook':
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # QUEEN
                    elif ptype == 'queen':
                        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # KING
                    elif ptype == 'king':
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx == 0 and dy == 0:
                                    continue
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < 8 and 0 <= ny < 8:
                                    target = board[ny][nx]
                                    if target is None or not target.startswith(color):
                                        moves.append(((x, y), (nx, ny)))
        return moves

    def make_move(self,board, move):
        new_board = copy.deepcopy(board)
        (from_x, from_y), (to_x, to_y) = move
        new_board[to_y][to_x] = new_board[from_y][from_x]
        new_board[from_y][from_x] = None
        return new_board

    def minimax(self,board, depth, alpha, beta, maximizing, color):
        if depth == 0:
            return self.evaluate_board(board), None

        best_move = None
        moves = self.generate_legal_moves(board, color)
        if not moves:
            return self.evaluate_board(board), None

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False,
                                        'black' if color == 'white' else 'white')
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True,
                                        'black' if color == 'white' else 'white')
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def save_board_to_file(self,board, filename="board_state.txt"):
        with open(filename, "w") as f:
            for row in board:
                f.write(' '.join([piece if piece else '.' for piece in row]) + "\n")

    def suggest_move(self,board, turn):
        color = 'white' if turn['white'] else 'black'
        
        # Get board representation as a string for AI
        board_str = self.board_to_string(board)
        
        # Store the current board state for feedback processing
        self.current_board_state = board_str
        
        # Use the smart hint system instead of just minimax
        if not self.showing_minimax_suggestion:
            # Generate hint from AI
            hint = self.hint_manager.generate_hint(board_str)
            # Show hint in tooltip
            self.tooltip.show(hint)
            return None  # No move to highlight
        else:
            # Use minimax for move suggestion (original behavior)
            _, move = self.minimax(board, depth=3, alpha=float('-inf'), beta=float('inf'), maximizing=True, color=color)
            return move

    def board_to_string(self, board):
        """Convert board to string representation for AI"""
        result = ""
        for row in board:
            row_str = ' '.join([piece if piece else '.' for piece in row])
            result += row_str + "\n"
        return result

    def start_game(self):
        """Function containing main game loop""" 
        # chess board offset
        self.board_offset_x = 0
        self.board_offset_y = 35
        self.board_dimensions = (self.board_offset_x, self.board_offset_y)
        
        # get location of chess board image
        board_src = os.path.join(self.resources, "board.png")
        # load the chess board image
        self.board_img = pygame.image.load(board_src).convert()

        # get the width of a chess board square
        square_length = self.board_img.get_rect().width // 8

        # initialize list that stores all places to put chess pieces on the board
        self.board_locations = []

        # calculate coordinates of the each square on the board
        for x in range(0, 8):
            self.board_locations.append([])
            for y in range(0, 8):
                self.board_locations[x].append([self.board_offset_x+(x*square_length), 
                                                self.board_offset_y+(y*square_length)])

        # get location of image containing the chess pieces
        pieces_src = os.path.join(self.resources, "pieces.png")
        # create class object that handles the gameplay logic
        self.chess = Chess(self.screen, pieces_src, self.board_locations, square_length)

        # Font for hint UI
        self.hint_font = pygame.font.SysFont("Arial", 14)
        
        # Track current board state for feedback
        self.current_board_state = ""

        # game loop
        while self.running:
            self.clock.tick(5)
            # poll events
            for event in pygame.event.get():
                # get keys pressed
                key_pressed = pygame.key.get_pressed()
                # check if the game has been closed by the user
                if event.type == pygame.QUIT or key_pressed[K_ESCAPE]:
                    # set flag to break out of the game loop
                    self.running = False
                elif key_pressed[K_SPACE]:
                    self.chess.reset()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the hint manager handles the event
                    if self.hint_manager.handle_click(event.pos, self.current_board_state):
                        continue
                        
                    # Check if tooltip needs to handle the event
                    self.tooltip.handle_event(event)
                        
                    # Check if suggest button was clicked
                    if SUGGEST_BUTTON_RECT.collidepoint(event.pos):
                        board_2d = self.piece_location_to_board(self.chess.piece_location)
                        self.save_board_to_file(board_2d)
                        
                        # Toggle between minimax and smart hint system
                        if event.button == 3:  # Right click
                            self.showing_minimax_suggestion = not self.showing_minimax_suggestion
                        
                        suggested_move = self.suggest_move(board_2d, self.chess.turn)
                        if suggested_move:
                            self.highlighted_move = suggested_move
            winner = self.chess.winner

            if self.menu_showed == False:
                self.menu()
            elif len(winner) > 0:
                self.declare_winner(winner)
            else:
                self.game()
                self.draw_suggest_button()
                
                # Draw hint controls
                self.hint_manager.draw_controls(self.screen, self.hint_font)
                
                # Draw tooltip if visible
                self.tooltip.draw(self.screen)
                
                if hasattr(self, 'highlighted_move') and self.highlighted_move:
                    self.draw_highlighted_move(self.screen, self.highlighted_move)

            # update display
            pygame.display.flip()
            # update events
            pygame.event.pump()

        # call method to stop pygame
        pygame.quit()
    

    def menu(self):
        """method to show game menu"""
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        
        # Center the "Play" button properly
        button_width = 100
        button_height = 50
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # coordinates for "Play" button - properly centered
        start_btn = pygame.Rect((screen_width - button_width) // 2, 300, button_width, button_height)
        
        # show play button
        pygame.draw.rect(self.screen, black_color, start_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)
        # create text to be shown on the game menu
        welcome_text = big_font.render("Chess", False, black_color)
        created_by = small_font.render("Created by Sheriff", True, black_color)
        start_btn_label = small_font.render("Play", True, white_color)
        
        # show welcome text
        self.screen.blit(welcome_text, 
                      ((self.screen.get_width() - welcome_text.get_width()) // 2, 
                      150))
        # show credit text
        self.screen.blit(created_by, 
                      ((self.screen.get_width() - created_by.get_width()) // 2, 
                      self.screen.get_height() - created_by.get_height() - 100))
        # show text on the Play button
        self.screen.blit(start_btn_label, 
                      ((start_btn.x + (start_btn.width - start_btn_label.get_width()) // 2, 
                      start_btn.y + (start_btn.height - start_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if "Play" button was clicked
            if start_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, start_btn, 3)
                
                # change menu flag
                self.menu_showed = True
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = True


    def game(self):
        # background color
        color = (0,0,0)
        # set backgound color
        self.screen.fill(color)
        
        # show the chess board
        self.screen.blit(self.board_img, self.board_dimensions)

        # call self.chess. something
        self.chess.play_turn()
        # draw pieces on the chess board
        self.chess.draw_pieces()

    def draw_suggest_button(self):
        # Use the global SUGGEST_BUTTON_RECT for consistency
        button_color = (50, 50, 50)
        if self.showing_minimax_suggestion:
            button_color = (100, 50, 50)  # Reddish if showing minimax suggestion
        pygame.draw.rect(self.screen, button_color, SUGGEST_BUTTON_RECT)
        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render("Suggest Move", True, (255, 255, 255))
        text_rect = text.get_rect(center=SUGGEST_BUTTON_RECT.center)
        self.screen.blit(text, text_rect)

    def declare_winner(self, winner):
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for play again button
        reset_btn = pygame.Rect(250, 300, 140, 50)
        # show reset button
        pygame.draw.rect(self.screen, black_color, reset_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)

        # text to show winner
        text = winner + " wins!" 
        winner_text = big_font.render(text, False, black_color)

        # create text to be shown on the reset button
        reset_label = "Play Again"
        reset_btn_label = small_font.render(reset_label, True, white_color)

        # show winner text
        self.screen.blit(winner_text, 
                      ((self.screen.get_width() - winner_text.get_width()) // 2, 
                      150))
        
        # show text on the reset button
        self.screen.blit(reset_btn_label, 
                      ((reset_btn.x + (reset_btn.width - reset_btn_label.get_width()) // 2, 
                      reset_btn.y + (reset_btn.height - reset_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if reset button was clicked
            if reset_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, reset_btn, 3)
                
                # change menu flag
                self.menu_showed = False
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = False
            # reset game
            self.chess.reset()
            # clear winner
            self.chess.winner = ""

    def draw_highlighted_move(self,screen, move):
        if move:
            (from_x, from_y), (to_x, to_y) = move
            square_size = 80  # Use your actual square size
            highlight_color = (0, 255, 0, 100)  # semi-transparent green
            s = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            s.fill(highlight_color)
            screen.blit(s, (from_x * square_size, from_y * square_size))
            screen.blit(s, (to_x * square_size, to_y * square_size))

