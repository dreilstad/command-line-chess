import numpy as np

PIECE_REPR = {
    ("w", "P"): "\u265F",
    ("w", "R"): "\u265C",
    ("w", "N"): "\u265E",
    ("w", "B"): "\u265D",
    ("w", "K"): "\u265A",
    ("w", "Q"): "\u265B",
    ("b", "p"): "\u2659",
    ("b", "r"): "\u2656",
    ("b", "n"): "\u2658",
    ("b", "b"): "\u2657",
    ("b", "k"): "\u2654",
    ("b", "q"): "\u2655",
}

FILES = ["a","b","c","d","e","f","g","h"]

class Piece:

    def __init__(self, pos, piece_type):
        self.pos = pos
        self.piece_type = piece_type
        
        if piece_type.islower():
            self.color = "b"
        else:
            self.color = "w"

        self.piece_symbol = PIECE_REPR[(self.color, self.piece_type)]

        if (pos[0] == 6 and self.piece_type == "P") or (pos[0] == 1 and self.piece_type == "p"):
            self.initial_rank = True
        else:
            self.initial_rank = False
        

    def __repr__(self):
        """
            Returns piece symbol for printing.
        """

        return self.piece_symbol

    def update_piece_symbol(self):
        """
            Updates piece symbol when promoting pawn.
        """

        self.piece_symbol = PIECE_REPR[(self.color, self.piece_type)]

    def indices_to_chess_notation(self, pos):
        """
            Maps position in board indices to chess notation.

            Return position in chess notation
        """

        return FILES[pos[1]] + str(8 - pos[0])

    def generate_legal_moves(self, board):
        """
            Generates all legal moves for piece. 
            Types of movement: pawn push, linear, diagonal, knight hopping, king 
        """

        legal_moves = []
        pos = self.pos

        # pawns
        if self.piece_type == "p" or self.piece_type == "P":
            self.pawn_movement(board, pos, legal_moves)


        # horizontal and vertical movement, rooks and queen
        if self.piece_type == "r" or self.piece_type == "R" or self.piece_type == "q" or self.piece_type == "Q":
            self.linear_movement(board, pos, legal_moves)
            

        # diagonal movement, bishops and queen
        if self.piece_type == "b" or self.piece_type == "B" or self.piece_type == "q" or self.piece_type == "Q":
            self.diagonal_movement(board, pos, legal_moves)


        # knight movement
        if self.piece_type == "n" or self.piece_type == "N":
            self.knight_movement(board, pos, legal_moves)


        # king movement
        if self.piece_type == "k" or self.piece_type == "K":
            self.king_movement(board, pos, legal_moves)

        self.legal_moves = legal_moves

    def pawn_movement(self, board, pos, legal_moves):
        """
            Finds all legal pawn movement, both pawn pushes and pawn captures.
        """

        # search downwards on board for black pawns, and upwards for white pawns
        search_dir = 1
        if self.color == "w":
            search_dir = -1

        # checks if square above is empty
        i = pos[0] + 1 * search_dir
        j = pos[1]
        if (i > -1 and i < 8) and (board[i][j] is None):
            legal_moves.append(self.indices_to_chess_notation((i, j)))

        # checks if two squares above is empty and pawn can double push
        i = pos[0] + 2 * search_dir
        j = pos[1]
        if (i > -1 and i < 8) and (board[i][j] is None) and self.initial_rank:
            legal_moves.append(self.indices_to_chess_notation((i, j)))

        # checks if there is an opponent piece diagonally to the left to capture
        i = pos[0] + 1 * search_dir
        j = pos[1] - 1
        if (i > -1 and i < 8) and (j > -1 and j < 8) and (board[i][j] is not None) and (board[i][j].color != self.color):
            legal_moves.append(self.indices_to_chess_notation((i, j)))

        # checks if there is an opponent piece diagonally to the right to capture
        i = pos[0] + 1 * search_dir
        j = pos[1] + 1
        if (i > -1 and i < 8) and (j > -1 and j < 8) and (board[i][j] is not None) and (board[i][j].color != self.color):
            legal_moves.append(self.indices_to_chess_notation((i, j)))

    def linear_movement(self, board, pos, legal_moves):
        """
            Finds all legal linear movement. Searches horizontally and vertically from piece position.
        """

        rank_left = np.arange(pos[1]-1, -1, -1)
        rank_right = np.arange(pos[1]+1, 8)
        file_up = np.arange(pos[0]-1, -1, -1)
        file_down = np.arange(pos[0]+1, 8)

        # search rank left
        self.iterate_moves(zip(np.full_like(rank_left, pos[0]), rank_left), board, legal_moves)

        # search rank right
        self.iterate_moves(zip(np.full_like(rank_right, pos[0]), rank_right), board, legal_moves)

        # search file up
        self.iterate_moves(zip(file_up, np.full_like(file_up, pos[1])), board, legal_moves)

        # search file down
        self.iterate_moves(zip(file_down, np.full_like(file_down, pos[1])), board, legal_moves)

    def diagonal_movement(self, board, pos, legal_moves):
        """
            Finds all legal diagonal movement. Searches diagonally in X-pattern centered at piece position.
        """

        rank_left = np.arange(pos[1]-1, -1, -1)
        rank_right = np.arange(pos[1]+1, 8)
        file_up = np.arange(pos[0]-1, -1, -1)
        file_down = np.arange(pos[0]+1, 8)

        # search diagonally up and left
        self.iterate_moves(zip(file_up, rank_left), board, legal_moves)

        # search diagonally up and right
        self.iterate_moves(zip(file_up, rank_right), board, legal_moves)

        # search diagonally down and left
        self.iterate_moves(zip(file_down, rank_left), board, legal_moves)

        # search diagonally down and right
        self.iterate_moves(zip(file_down, rank_right), board, legal_moves)

    def knight_movement(self, board, pos, legal_moves):
        """
            Finds all legal knight moves. Searches all L's out from piece position.
        """


        def iterate_knight_moves(indices):
            for i, j in indices:
                if (i > -1 and i < 8) and (j > -1 and j < 8):
                    if board[i][j] is not None:
                        if board[i][j].color != self.color:
                            legal_moves.append(self.indices_to_chess_notation((i, j)))
                    else:
                        legal_moves.append(self.indices_to_chess_notation((i, j)))

        indices = np.full(8, None)

        # upper left corner squares
        indices[0] = (pos[0]-1, pos[1]-2) #left
        indices[1] = (pos[0]-2, pos[1]-1) #right

        # upper right corner squares
        indices[2] = tuple([sum(x) for x in zip(indices[1], (0,2))])
        indices[3] = tuple([sum(x) for x in zip(indices[0], (0,4))])

        # lower left corner squares
        indices[4] = tuple([sum(x) for x in zip(indices[0], (2,0))])
        indices[5] = tuple([sum(x) for x in zip(indices[1], (4,0))])

        # lower right corner squares
        indices[6] = tuple([sum(x) for x in zip(indices[0], (3,3))])
        indices[7] = tuple([sum(x) for x in zip(indices[1], (3,3))])

        iterate_knight_moves(indices)

    def king_movement(self, board, pos, legal_moves):
        """
            Finds all legal king movement. Searches non-capturing moves and capturing moves.
        """

        # search around king
        for i in range(pos[0]-1, pos[0]+2):
            for j in range(pos[1]-1, pos[1]+2):
                if (i > -1 and i < 8) and (j > -1 and j < 8) and ((i, j) != pos):
                    if board[i][j] is not None:
                        if board[i][j].color != self.color:
                            legal_moves.append(self.indices_to_chess_notation((i, j)))
                    else:
                        legal_moves.append(self.indices_to_chess_notation((i, j)))

    def iterate_moves(self, indices, board, legal_moves):
        """
            Helper function for iterating board in a certain direction given as argument
        """

        for i, j in indices:
            if board[i][j] is not None:
                if board[i][j].color != self.color:
                    legal_moves.append(self.indices_to_chess_notation((i, j)))
                break
            else:
                legal_moves.append(self.indices_to_chess_notation((i, j)))
