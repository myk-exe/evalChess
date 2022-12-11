import random



pieceScore = {'K':0, 'Q':10, 'R':5, 'B':3, 'N':3, 'p':1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3 # More depths take exponentialy time in MinMax method!



# Knights wanna be as close to center as possible
knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 2, 2, 2, 2, 2, 2, 1],
                        [1, 2, 3, 3, 3, 3, 2, 1],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [1, 2, 3, 3, 3, 3, 2, 1],
                        [1, 2, 2, 2, 2, 2, 2, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1]]


# Biship wants to be on the diagonal
bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 4, 3, 3, 4, 3, 2],
                    [3, 4, 3, 2, 2, 3, 4, 3],
                    [4, 3, 2, 1, 1, 2, 3, 4]]


queenScores =  [[1, 1, 1, 3, 1, 1, 1, 1],
                    [1, 2, 3, 3, 3, 1, 1, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 2, 3, 3, 3, 2, 2, 1],
                    [1, 4, 3, 3, 3, 4, 2, 1],
                    [1, 1, 2, 3, 3, 1, 1, 1],
                    [1, 1, 1, 3, 1, 1, 1, 1]]


# Probably better to try to place rooks on open files, or on same file as other rook/queen

rookScores =   [[4, 3, 4, 4, 4, 4, 3, 4],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 2, 2, 2, 1, 1],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [4, 3, 4, 4, 4, 4, 3, 4]]



whitePawnScores =  [[8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0]]


blackPawnScores =  [[0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 0, 0, 1, 1, 1],
                        [1, 1, 2, 3, 3, 2, 1, 1],
                        [1, 2, 3, 4, 4, 3, 2, 1],
                        [2, 3, 3, 5, 5, 3, 3, 2],
                        [5, 6, 6, 7, 7, 6, 6, 5],
                        [8, 8, 8, 8, 8, 8, 8, 8],
                        [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = { 'N':knightScores,
                        'Q':queenScores,
                        'B':bishopScores,
                        'R':rookScores,
                        'bp':blackPawnScores,
                        'wp':whitePawnScores }





def findRandomMove(validmoves):
    return validmoves[random.randint(0, len(validmoves)-1)]


# ====================================================== 2 Depth MinMax =====================================================================
# Greedy alghorithm
# This only looks 2 move aheads 
def findBestMove(gs, validMoves): 

    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE # From Black's prespective this is the worst condition
    bestMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate :
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves: # This loop goes through my opponents all possible moves and finds the best move they can
                                             # have after my each move. (their best move = our worse move!)
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkmate :
                    boardScore =  CHECKMATE
                elif gs.stalemate:
                    boardScore = STALEMATE
                else:
                    boardScore = -turnMultiplier * scoreMaterial(gs.board)
                if boardScore > opponentMaxScore :
                    opponentMaxScore = boardScore
                    bestMove = playerMove
                gs.undoMove()

        if opponentMaxScore < opponentMinMaxScore: # Whats the best response of enemy to my move? if its score is less than my enemy's
                                                   # prev move, so thts the move I should take!
            opponentMinMaxScore = opponentMaxScore
            bestMove = playerMove
        gs.undoMove()


    return bestMove

# Score the board based on material
def scoreMaterial(board):
    boardScore = 0
    for row in board:
        for square in row:
            if square[0] == 'w': # White material advantage is positive
                boardScore += pieceScore[square[1]]
            elif square[0] == 'b': # Black material advantage is negative
                boardScore -= pieceScore[square[1]]

    return boardScore


# ===================================================== <N> Depth MinMax ====================================================================
# MinMax II
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

def findMoveMinMax(gs, validMoves,  depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()
        return minScore 

# Rmmbr: A positive score good for white & a negative score good for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return  -CHECKMATE # Black wins
        else:
            return CHECKMATE # White winsff

    elif gs.stalemate:
        return STALEMATE


    boardScore = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                # Score it positionally
                piecePositionScore = 0
                if square[1] != 'K': # No position table for king
                    if square[1] == 'p': # For pawns
                        piecePositionScore = piecePositionScores[square][row][col]
                    else: # For other pieces
                        piecePositionScore = piecePositionScores[square[1]][row][col]


                if square[0] == 'w': # White material advantage is positive
                    boardScore += pieceScore[square[1]] + piecePositionScore * 0.1
                elif square[0] == 'b': # Black material advantage is negative
                    boardScore -= pieceScore[square[1]] + piecePositionScore * 0.1

    return boardScore


# ========================================================= Nega Max =========================================================================
# Same as MinMax; just shorter!

def findBestMoveNegaMax(gs, validMoves):
    global nextMove
    
    nextMove = None
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


# ===================================================== Nega Max Alpha Beta ==================================================================
# Same as MinMax; just shorter!

def findBestMoveNegaMaxAlphaBeta(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
   
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # Move ordering - implemetn later


    maxScore = -CHECKMATE
    random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: # Pruning happens
            alpha = maxScore
        if alpha >= beta:
            break # We dont need to check unneccessary moves

    return maxScore








