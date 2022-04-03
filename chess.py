import re
import numpy as np
from piece import Piece
from playsound import playsound

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
EMPTY_SQUARE = "\u26AC"
FILE_TO_NUM = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
FILES = ["a","b","c","d","e","f","g","h"]

class Chess:

    def __init__(self, FEN=None):
        self.init_board_and_piece_rep(FEN)
        self.generate_legal_moves()
        self.game_loop()
    
    def __repr__(self):
        """
            Generates string representation of board.
        """

        board_repr = "  \u250F" + "\u2501"*17 + "\u2513" + "\n"
        for i in range(8):
            board_repr += str(8-i) + " \u2503 "
            for j in range(8):
                if self.board[i][j] is None:
                    board_repr += EMPTY_SQUARE
                else:
                    board_repr += repr(self.board[i][j])
                
                board_repr += " "

            board_repr += "\u2503\n"

        board_repr += "  \u2517" + "\u2501"*17 + "\u251B" + "\n"
        board_repr += "    a b c d e f g h"
        return board_repr

    def init_board_and_piece_rep(self, FEN):
        """
            Initializes board and pieces from FEN-string, either starting FEN or given FEN.
        """

        black_pieces = []
        white_pieces = []
        board = np.full((8,8), None)

        if FEN is None:
            fen_split = STARTING_FEN.replace(' ', '/').split('/')
        else:
            fen_split = FEN.replace(' ', '/').split('/')


        for i, part in enumerate(fen_split[:8]):
            j = 0
            for piece_type in part:
                if piece_type.isdigit():
                    j += int(piece_type)
                else:
                    # instantiate piece and add to reps
                    piece = Piece((i,j), piece_type)

                    if piece_type.islower():
                        black_pieces.append(piece)
                    else:
                        white_pieces.append(piece)

                    board[i][j] = piece
                    j += 1
                    

        self.pieces = {"b":black_pieces, "w":white_pieces}
        self.board = board

        self.side_to_move = fen_split[8]

        # '-' means neither side can castle, 
        # 'K', 'Q', 'k', 'q' is used for king and queen castling for both sides, (e.g. "KQkq")
        self.castling_ability = fen_split[9]
        
        # en passant target square if legal, legality needs to be checked
        self.en_passant_target_square = fen_split[10]

        # number of half moves since capture or pawn move
        self.halfmove_clock = fen_split[11] 
        
        # number of full moves, incremented after black's moves
        self.fullmove_counter = fen_split[12] #number of full moves

        self.white_king_check = False
        self.black_king_check = False

    def generate_legal_moves(self):
        """
            Iterates list of pieces of the side to move next, and generates all legal moves.
        """

        for piece in self.pieces[self.side_to_move]:
            piece.generate_legal_moves(self.board)

    def game_loop(self):
        """
            Game loop
        """

        # print board
        print(self)

        # get move from player
        move = input(":")
        if move == "q":
            self.quit_sequence()


        # perform move if possbile
        moved = self.move(move)

        # refresh terminal
        print("\n"*50)

        # plays move-sound if successful, or error-sound if not
        # generates legal moves for next side to move
        if moved:
            playsound("sounds/move.mp3")
            if self.side_to_move == "b":
                self.side_to_move = "w"
            else:
                self.side_to_move = "b"

            self.generate_legal_moves()
        else:
            print(f"Move '{move}' is not legal\n")
            playsound("sounds/failed_move.mp3")

        # repeat
        self.game_loop()
        
    def move(self, move):
        """
            Performs the move given as argument. 
            Checks for different types of moves: castling, capture, move, etc.

            Returns True if move was successful, False if not.
        """
        # checkmate
        if "#" in move:
            #TODO
            pass

        # check
        if "+" in move:
            #TODO
            pass

        # castling
        if "O-" in move:
            return self.castle(move)

        # non-capturing move
        if "x" not in move:
            return self.non_capturing_move(move)

        if "x" in move:
            return self.capturing_move(move)

        return False

    def chess_notation_to_indices(self, notation):
        """
            Maps position in chess notation to board indices.

            Return position in board indices
        """

        return (8 - int(notation[1]), FILE_TO_NUM[notation[0]])

    def indices_to_chess_notation(self, pos):
        """
            Maps position in board indices to chess notation.

            Return position in chess notation
        """

        return FILES[pos[1]] + str(8 - pos[0])

    def non_capturing_move(self, move):
        """
            Performs non-capturing move.

            Returns True if move was successful, False if not.
        """
        
        try:
            move_square = re.findall("([a-h][1-8])", move)[0]
        except:
            return False

        pos_to_move = self.chess_notation_to_indices(move_square)
        
        # pawn move
        if (len(move) == 2) or ("=" in move) or (move[0].islower()):

            # find pawn to move
            piece_to_move = self.find_pawn_to_move(move, pos_to_move)

            # check if move is legal
            if (piece_to_move is None) or (move_square not in piece_to_move.legal_moves):
                return False

            # move piece and update pos
            self.move_piece_and_update_pos(piece_to_move, pos_to_move)

            # check special case of promotion
            if "=" in move:
                piece_to_move.piece_type = move[3]
                piece_to_move.update_piece_symbol()

            return True

        # other piece to move
        elif (len(move) > 2) and (len(move) < 6):

            # find piece to move
            piece_to_move = self.find_piece_to_move(move)

            # check if move is legal
            if (piece_to_move is None) or (move_square not in piece_to_move.legal_moves):
                return False
            
            # move piece and update pos 
            self.move_piece_and_update_pos(piece_to_move, pos_to_move)

            return True

        return False

    def capturing_move(self, move):
        """
            Performs capturing move and removes captured piece.

            Returns True if capture was successful, False if not.
        """

        move_square = re.findall("([a-h][1-8])", move)[0]
        pos_to_move = self.chess_notation_to_indices(move_square)

        # check if there a piece to capture
        if self.board[pos_to_move] is None:
            return False


        captured_piece = self.board[pos_to_move]
        captured_side = "w" if self.side_to_move == "b" else "b"

        moved = self.non_capturing_move(move)

        if moved:
            # remove captured piece from list
            self.pieces[captured_side].remove(captured_piece)
            return True

        return False

    def find_pawn_to_move(self, move, pos_to_move):
        """
            Finds correct pawn to move. Faster to directly access via logic rather than iterating over all pieces.

            Returns Piece object to move, None if no piece found
        """

        piece_to_move = None

        # capture
        if "x" in move:

            if self.side_to_move == "w":
                piece_to_move = self.board[pos_to_move[0]+1][FILE_TO_NUM[move[0]]]
            else:
                piece_to_move = self.board[pos_to_move[0]-1][FILE_TO_NUM[move[0]]]

        # move
        else:

            if self.side_to_move == "w":
                # single push
                piece_to_move = self.board[pos_to_move[0]+1][pos_to_move[1]]
                
                # double push
                if piece_to_move is None:
                    piece_to_move = self.board[pos_to_move[0]+2][pos_to_move[1]]

            else:
                # single push
                piece_to_move = self.board[pos_to_move[0]-1][pos_to_move[1]]
                
                # double push
                if piece_to_move is None:
                    piece_to_move = self.board[pos_to_move[0]-2][pos_to_move[1]]


        return piece_to_move

    def find_piece_to_move(self, move):
        """
            Iterates list of pieces of the side to move, and finds the correct piece to move. 
            There may be two pieces of same type able to perform the same move.

            Returns Piece object to move, None if no piece found
        """
            
        # move can be made by two of same type
        rank_idx = -1
        file_idx = -1
        if ((len(move) == 4) and ("x" not in move)) or ((len(move) == 5) and ("x" in move)):
            # is in same file
            if move[1].isdigit():
                rank_idx = int(move[1])
            # can move to same square
            else: 
                file_idx = FILE_TO_NUM[move[1]]


        move_square = re.findall("([a-h][1-8])", move)[0]

        # find piece to move, finds correct piece if two of same type can move to square
        piece_to_move = None
        for piece in self.pieces[self.side_to_move]:
            if (piece.piece_type.upper() == move[0]) and (move_square in piece.legal_moves):
                if file_idx != -1:
                    if file_idx == piece.pos[1]:
                        piece_to_move = piece
                        break
                elif rank_idx != -1:
                    if rank_idx == piece.pos[0]:
                        piece_to_move = piece
                        break
                else:
                    piece_to_move = piece
                    break

        return piece_to_move

    def move_piece_and_update_pos(self, piece_to_move, pos_to_move):
        """
            Moves piece to square and updates the position of the piece.
        """

        # move pawn
        self.board[pos_to_move] = piece_to_move
        self.board[piece_to_move.pos] = None
        
        # update pos
        piece_to_move.pos = pos_to_move

    def castle(self, move):
        """
            Performs castling move, either kingside or queenside. 
            Checks if castling is allowed, performs move, and updates castling_ability.

            Returns True if successful, False if not.
        """

        # castling kingside
        if move == "O-O":
            castling_notation = "K" if self.side_to_move == "w" else "k"
            rank = 7 if castling_notation.isupper() else 0

            # check if castling is possible
            if self.castling_is_legal(move, castling_notation, rank):

                # get pieces
                king = self.board[rank][4]
                rook = self.board[rank][7]

                # move pieces
                self.board[rank][4] = None
                self.board[rank][5] = rook
                self.board[rank][6] = king
                self.board[rank][7] = None

                # update pos
                king.pos = (rank, 6)
                rook.pos = (rank, 5)

            else:
                return False

        # castling queenside
        if move == "O-O-O":
            castling_notation = "Q" if self.side_to_move == "w" else "q"
            rank = 7 if castling_notation.isupper() else 0

            # check if castling is possible
            if self.castling_is_legal(move, castling_notation, rank):

                # get pieces
                king = self.board[rank][4]
                rook = self.board[rank][0]

                # move pieces
                self.board[rank][0] = None
                self.board[rank][2] = king
                self.board[rank][3] = rook
                self.board[rank][4] = None

                # update pos
                king.pos = (rank, 2)
                rook.pos = (rank, 3)

            else:
                return False

        # remove white or black castling ability
        if castling_notation.isupper():
            self.castling_ability = ''.join(ch for ch in self.castling_ability if not ch.isupper())
        else:
            self.castling_ability = ''.join(ch for ch in self.castling_ability if not ch.islower())
    

        return True

    def castling_is_legal(self, move, castling_notation, rank):
        """
            Checks if castling is legal. 
            Checks if side to move have castling ability, squares are empty and not threatened.

            Return True if castling is legal, False if not
        """

        # rook or king has not moved, or already castled
        pieces_have_not_moved = castling_notation in self.castling_ability

        # squares between rook and king are empty
        empty_between = self.empty_squares_between(move, rank)

        # the other side's pieces do not threaten empty squares between
        castling_threatened = self.castle_threatened(move, rank)

        return pieces_have_not_moved and empty_between and (not castling_threatened)

    def empty_squares_between(self, move, rank):
        """
            Checks if squares between king and rook are empty. Cannot castle over own or opponent pieces.

            Returns True if all squares are empty, False if not
        """

        if move == "O-O":
            return (self.board[rank][5] is None) and (self.board[rank][6] is None)
        elif move == "O-O-O":
            return (self.board[rank][1] is None) and (self.board[rank][2] is None) and (self.board[rank][3] is None)
        
        return False

    def castle_threatened(self, move, rank):
        """
            Checks if squares between king and rook is threatened by any of the opponent's pieces.

            Return True if any sqaure is threatened, False if not.
        """
        
        pieces = self.pieces["b"] if self.side_to_move == "w" else self.pieces["w"]

        if move == "O-O":
            f_square = self.indices_to_chess_notation((rank,5))
            g_square = self.indices_to_chess_notation((rank,6))
            for piece in pieces:
                if (f_square in piece.legal_moves) or (g_square in piece.legal_moves):
                    return True

        elif move == "O-O-O":
            b_square = self.indices_to_chess_notation((rank,1))
            c_square = self.indices_to_chess_notation((rank,2))
            d_square = self.indices_to_chess_notation((rank,3))
            for piece in pieces:
                if (b_square in piece.legal_moves) or (c_square in piece.legal_moves) or (d_square in piece.legal_moves):
                    return True

        return False

    def quit_sequence(self):
        """
            Quit sequence. Prints the FEN-string and exits.
        """

        self.print_FEN()
        exit(0)

    def print_FEN(self):
        """
            Parses board, builds FEN-string and prints it.
        """

        fen = ""

        for i in range(8):
            fen += "/"
            empty = 0
            for j in range(8):
                if self.board[i][j] is None:
                    empty += 1
                else:
                    if empty != 0:
                        fen += str(empty)

                    fen += self.board[i][j].piece_type
                    empty = 0

            if empty != 0:
                fen += str(empty)

        fen = fen[1:] + " "
        
        fen += self.side_to_move + " " + self.castling_ability + " " + self.en_passant_target_square + " " \
                + self.halfmove_clock + " " + self.fullmove_counter

        print("FEN: " + fen)

if __name__ == "__main__":
    a = Chess()
