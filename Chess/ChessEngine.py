# Responsible for storing data about the current state of game
# Responsible for saving move logs
# Resonsible for valid moves at a time





class GameState():


    # ======================================================== Variables Define ========================================================
    def __init__(self) -> None:

        # Board is an 8*8 2d list. Each element has 2 characters.
        # The first character represent the color of the piece.
        # The second character represents the type of the piece.
        # '--' represent any space without any piece.


        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

 

        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'p':self.getPawnMoves, 'R':self.getPawnMoves, 'N':self.getKnightMoves, 'R':self.getRookMoves,
                              'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}

        self.whiteKingLocation = (7, 4) # To keep track of kings location for track the checking stuff
        self.blackKingLocation = (0, 4)
        
        self.inCheck = False
        self.pins = []
        self.checks = []

        self.enpassantPossible = () # Coords where an enpassant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]

        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.undoFlag = False
        self.checkmate = False
        self.stalemate = False


    # ======================================================== Make Move ===============================================================
    def makeMove(self, move):
        # Takes Move as a parameter and executes it.
        # This function won't work for Casteling, Pawn Promotion and en-passant 
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Swap players
        # Update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion 
        if move.isPawnPromotion :
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'


        # Enpassant
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--' # Capturing the pawn

        # Update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # To make sure only on 2 square pawn advance it updates
            self.enpassantPossible = ((move.startRow + move.endRow)//2 , move.startCol)
        else:
            self.enpassantPossible = () 


        # Castle Move
        if move.isCastleMove :
            if move.endCol - move.startCol == 2: # Kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol + 1] # Moves the rook
                self.board[move.endRow][move.endCol + 1] = '--' # Erase old rook
            else: # Queenside castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # Moves the rook
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update castling right - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    # ======================================================== Undo Move ===============================================================
    def undoMove(self): 
        if len(self.moveLog) != 0 : # Make sure tht there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns back
            
            # Update the king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo enpassant
            if move.enPassant :
                self.board[move.endRow][move.endCol] = '--' # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured # Puts the pawn back on the corrct square it was captured from

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
        

            # Undo castling right

            self.castleRightsLog.pop() # Get rid of new castle rights from the move we are undoing
            self.currentCastlingRight = self.castleRightsLog[-1] # Set the current castle rights to the last move we did
    
            # Undo Castle Move
            if move.isCastleMove :
                if move.endCol - move.startCol == 2: # Kingside castle move
                    self.board[move.endRow][move.endCol +1] = self.board[move.endRow][move.endCol -1] # Puts rook back to its pre location
                    self.board[move.endRow][move.endCol -1] = '--'

                else: # Queenside Castle move
                    self.board[move.endRow][move.endCol -2] = self.board[move.endRow][move.endCol +1]
                    self.board[move.endRow][move.endCol +1] = '--'

            self.checkmate = False
            self.stalemate = False


    # ======================================================= Update Castle Rights ======================================================
    def updateCastleRights(self, move):

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False

        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7: # Rook on the bottom row
                if move.startCol == 0: # Left Rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right Rook
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0: # Rook on the bottom row
                if move.startCol == 0: # Left Rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right Rook
                    self.currentCastlingRight.wks = False

        # If a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False

        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


    # ======================================================= Get Valid Moves ===========================================================
    def getValidMoves(self):
        # All moves considering checks     
        moves = []
        self.inCheck, self.pins, self.checks, ally = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1 : # Only 1 check ; block check or move king
                moves = self.getAllPossibleMoves()

                # To block a check you must move a piece in one of the squares
                # between the enemy and the king
                check = self.checks[0] # Check info
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # Enemy piece causing the check
                if pieceChecking[1] == 'N':  # If the checking enemy is knight the only valid move is capturing the knight
                    validSquares = [(checkRow, checkCol)]
                else:
                    validSquares = []
                    for i in range(1,8): 
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # Check 2 and 3 are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # Once you get to the enemy piece checking
                            break
                
                # Get rid of any moves tht dont block check. And/or move the king
                for i in range(len(moves)-1 , -1, -1):
                    if moves[i].pieceMoved[1] != 'K': # Move doesnt move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # The move wont block check or capture the checking piece enemy
                            moves.remove(moves[i])
       
            else: # Double Checks! King MUST move.
                self.getKingMoves(kingRow, kingCol, moves)  

        else: #Not in check, so all moves are fine!
            moves = self.getAllPossibleMoves()


        # ------------- Check / Stale Mate -------------------------------

        if len(moves) == 0 : # Either checkmate or stalemate
                if self.inCheck:
                    self.checkmate = True
                else:
                    self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # ------------- Get Castle Moves ---------------------------------
        self.getCastleMoves(kingRow, kingCol, moves, 'w' if self.whiteToMove else 'b')
        
        return moves


    # ======================================================== All Possible Moves ========================================================
    def getAllPossibleMoves(self):
        # All moves without considering checks
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of columns in given rows
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # Calls the appropriate move function based on piece type
                
        return moves


    # ======================================================== Check Pins & Checks ======================================================
    def checkForPinsAndChecks (self):
        pins = [] # Squares where the allies pinned piece is and direction pinned from
        checks = [] # Squares where enemy is applying a check
        inCheck = False

        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Check outward from king for pins and checks and keep track of pins
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # Reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i 
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8 :
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        # We wrote '!= "k"' here cuz we check all possible moves of our king
                        # by adding a phantom king (virtual move which aint showed to player)
                        # and the phantom king checks the directions leading to it and sees the
                        # real king which causes trouble for us!
                        if possiblePin == (): # 1st allied piece can be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1) Orthogonally away from king and piece is a rook
                        # 2) Diagonally away from king and the piece is a bishop
                        # 3) 1 square away from king and the piece is pawn
                        # 4) Any direction and the piece is a queen
                        # 5) Any direction 1 square away and piece is a king
                        # (this is necessary for a king to prevent other kings moving to his territory)

                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or \
                            (i == 1 and type == 'K'):
                                if possiblePin == (): # No ally piece blocking the way, so check!
                                    inCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                                    break

                                else: # Piece blocking, so its pin.
                                    pins.append(possiblePin)
                                    break
                        
                        else: # Enemy piece not applying check
                            break
                else:
                    break


        # Check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8 :
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # Enemy knight attacking the king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks, (startRow, startCol)


    # ======================================================== In Check =================================================================
    def inCheck(self):
        # Determine if the current player is in check
        if self.whiteToMove :
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    # ======================================================== Square Under Attack ========================================================
    def squareUnderAttack(self, r, c):
        # Determine if the enemy can attack the square r, c
        self.whiteToMove = not self.whiteToMove # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch the turn back

        for move in oppMoves:
            if move.endRow == r and move.endCol == c : # Square is under attack
                return True

        return False












# =========================================================== Species Moves ============================================================

    # -------------------------------------------------------- Pawn Moves --------------------------------------------------------
    def getPawnMoves(self, r, c, moves):
        # Get all pawn moves for the pawn located at row, col and add these moves to the list
        piecePinned = False 
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow =   0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation

        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
       
        pawnPromotion = False


        if self.board[r + moveAmount][c] == '--': # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r+moveAmount == backRow: # if piece gets to back rank then it is a pawn promotion
                    pawnPromotion = True
                moves.append(Move((r,c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))

                if r == startRow and self.board[r+2*moveAmount][c] == '--': # 2 square moves
                    moves.append(Move((r,c), (r+2*moveAmount,c), self.board))

        if c-1 >= 0 : #Capture to left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow:  # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r,c) , (r+moveAmount, c-1), self.board, pawnPromotion=pawnPromotion))
                
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r : # Solving the weird enpassant bug
                        if kingCol < c : # king is on the left of the pawn
                            # inside range between the king and the pawn; outside range between pawn border
                            insideRange = range(kingCol+1, c-1)
                            outsideRange = range(c+1, 8)
                        else: #King right of pawn
                            insideRange = range(kingCol-1, c, -1)
                            outsideRange = range(c-2, -1, -1)

                        for i in insideRange:
                            if self.board[r][i] != '--': # Some other piece beside enpassant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'): # Attacking Piece
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c), (r+moveAmount, c-1), self.board, enPassant=True))

        
        if c +1 <= 7 : # Capture to right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:  # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r,c) , (r+moveAmount, c+1), self.board, pawnPromotion=pawnPromotion))
                
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r : # Solving the weird enpassant bug
                        if kingCol < c : # king is on the left of the pawn
                            # inside range between the king and the pawn; outside range between pawn border
                            insideRange = range(kingCol+1, c)
                            outsideRange = range(c+2, 8)
                        else: #King right of pawn
                            insideRange = range(kingCol-1, c+1, -1)
                            outsideRange = range(c-1, -1, -1)

                        for i in insideRange:
                            if self.board[r][i] != '--': # Some other piece beside enpassant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'): # Attacking Piece
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c), (r+moveAmount, c+1), self.board, enPassant=True))


    # -------------------------------------------------------- Rook Moves --------------------------------------------------------
    def getRookMoves(self, r, c, moves):
        # Get all Rook moves for the Rook located at row, col and add these moves to the list
        piecePinned = False 
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # Cant remove queen from pin on rook moves, 
                                               # only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break


        directions = ((-1,0), (0,-1), (1,0), (0,1)) # Up , Left, Down, Right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # On board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': # Empty space valid
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # Enemy piece valid
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break

                        else: # Friendly piece invalid
                            break
                else: # Off board 
                    break

    # -------------------------------------------------------- Bishop Moves --------------------------------------------------------
    def getBishopMoves(self, r, c, moves):
        # Get all Bishop moves for the Bishop located at row, col and add these moves to the list
        piecePinned = False 
        pinDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (1,1), (1,-1), (-1,1)) # 4 diaganols
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8): # Can move maximumly 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8 : # Is the end-point on the board?
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': # Empty Space Valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # Enemy color Valid
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break
                        else: # Friendly Piece Invalid
                            break
                else: # Off Board
                    break

    # -------------------------------------------------------- Knight Moves --------------------------------------------------------
    def getKnightMoves(self, r, c, moves):
        # Get all Knight moves for the Knight located at row, col and add these moves to the list
        piecePinned = False 
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8 :
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor : # Not an ally piece (empty or enemy piece)
                        moves.append(Move((r,c), (endRow, endCol), self.board)) 

    # -------------------------------------------------------- King Moves --------------------------------------------------------
    def getKingMoves(self, r, c, moves):
        # Get all King moves for the King located at row, col and add these moves to the list
        kingMoves = ((0,1), (0,-1), (1,0), (-1,0), (-1,1), (-1,-1), (1,1), (1,-1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8 : # Target place on the board
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor:    # Target place either empty or enemy on it
                    # Place king on target square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck , pins, checks, ally = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))

                    # Place king back on its own location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    # -------------------------------------------------------- Queen Moves --------------------------------------------------------
    def getQueenMoves(self, r, c, moves):
        # Get all Queen moves for the Queen located at row, col and add these moves to the list
         # Queen moves is the combination of bishop & rook
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)








    # ======================================================= Castle Moves ===============================================================
    # Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    def getCastleMoves(self, r, c, moves, allyColor):
        if self.squareUnderAttack(r, c):
            return # Can't castle while we are in check!
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)

        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)
          
    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove = True))
            pass

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c -3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove = True))

            




class Move():

    ranksToRows = {'1':7, '2':6, '3':5, '4':4,
                   '5':3, '6':2, '7':1, '8':0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {'a':0, 'b':1, 'c':2, 'd':3,
                   'e':4, 'f':5, 'g':6, 'h':7}

    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False, isCastleMove = False):
        self.startSq = startSq
        self.endSq = endSq
        self.startRow = int(startSq[0])
        self.startCol = int(startSq[1])
        self.endRow = int(endSq[0])
        self.endCol = int(endSq[1])
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pawnPromotion = pawnPromotion
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove

        # Pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7) :
            self.isPawnPromotion = True
        
        # Enpassant
        self.enPassant = enPassant
        if self.enPassant:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
    


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # Make chess feel like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile (self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]        


class CastleRights():

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks 
        self.bks = bks 
        self.wqs = wqs 
        self.bqs = bqs 














