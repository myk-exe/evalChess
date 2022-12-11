# This is our main driver file
# This will be responsible for handling user input and displaying current GameState object!


import pygame as p
import ChessEngine
import ChessAI




WIDTH = HEIGHT = 512 # 400 is another option
DIMENSION = 8 # 8*8 board
SQ_SIZE = HEIGHT/DIMENSION
MAX_FPS = 15 # For animation later on
IMAGES = {}



# ================================================================ IMAGES ================================================================
# Initialize a global dict of images. It will be called exactly once in the main
def Load_Images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bp',
              'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR', 'wp'
    ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Pix/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # We can access images using IMAGES['bp']
     

# ================================================================ MAIN ================================================================

# Defining our main driver for the code. This will handle user input and updating the graphics.
def main():
    # ------------------------------------------ Variables Defininig ----------------------------------------------------------------
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('Chess')
    Icon = p.image.load('logo.png')
    p.display.set_icon(Icon)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag variable for when a move is made
    Load_Images() # Only do this once before while loop
    running = True
    sqSelected = () # No square is selected, keep track of the last click of the user
    playerClicks = [] # Keep track of player clicks (two tuples: [(7, 4), (4, 4)])
    animate = False # Flag variable when we wanna animate move
    gameover = False # True when one side loses
    playerOne = True # One --> White | True --> Human
    playerTwo = False # Two --> Black | False --> AI


    while running:

        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        # ========================================================== Input Handling =========================================================
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # ===================================================== Mouse Handlers ===========================================================
            # ------ Mouse Clicked ----------------------------
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameover and humanTurn:
                    location = p.mouse.get_pos() # (x, y) location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    # ------------------------- Click Condition ------------------------------------
                    if sqSelected == (row,col): # The user clicked the same square
                        sqSelected = () # Deselect
                        playerClicks = [] # Clear Player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # append for both 1st and 2nd clicks

                    # -------------------------- 1st Click -----------------------------------------
                    if len(playerClicks) == 1:
                        # You cant move, blank spaces!
                        if gs.board[int(playerClicks[0][0])][int(playerClicks[0][1])] == '--':
                            playerClicks = []
                            sqSelected = ()

                        # You cant move the other user's pieces! 
                        elif gs.whiteToMove and gs.board[int(playerClicks[0][0])][int(playerClicks[0][1])][0] == 'b':
                            playerClicks = []
                            sqSelected = ()
                           
                        elif not gs.whiteToMove and gs.board[int(playerClicks[0][0])][int(playerClicks[0][1])][0] == 'w':
                            playerClicks = []
                            sqSelected = ()

                    # -------------------------- 2nd Click -----------------------------------------
                    elif len(playerClicks) == 2: # After 2nd click
                        
                        # When the user clicks two of its own pieces, it means the first one, our user rlly doesnt want it!
                        if gs.board[int(playerClicks[0][0])][int(playerClicks[0][1])][0] == gs.board[int(playerClicks[1][0])][int(playerClicks[1][1])][0]:
                            playerClicks.remove(playerClicks[0])
                
                        else:

                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    animate = True
                                    sqSelected = () # Reset User Clicks
                                    playerClicks = []
                            if not moveMade: # Invalid moves clicked
                                playerClicks = [playerClicks[0]]

            # ===================================================== Key Handlers =============================================================

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo when 'z' is pressed
                    if playerTwo:
                        gs.undoMove()

                    else:
                        gs.undoMove()
                        gs.undoMove()

                    moveMade = True
                    animate = False
                    gameover = False

                if e.key == p.K_r: # Reset the board when 'r' is pressed 
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameover = False

        # ======================================================== Artificial Intelligence ===================================================
        if not gameover and not humanTurn and validMoves != []:

            if len(gs.moveLog) >= 4: # To solve the forever looping problem of making the same moves!
                if gs.moveLog[-1].startSq == gs.moveLog[-3].endSq and \
                    gs.moveLog[-1].endSq == gs.moveLog[-3].startSq and \
                        gs.moveLog[-2].startSq == gs.moveLog[-4].endSq and \
                            gs.moveLog[-2].endSq == gs.moveLog[-4].startSq:
                            AIMove = ChessAI.findRandomMove(validMoves)
                else:
                    AIMove = ChessAI.findBestMoveNegaMaxAlphaBeta(gs, validMoves)
                    if AIMove:
                        pass
                    else:
                        AIMove = ChessAI.findRandomMove(validMoves)
                        
                gs.makeMove(AIMove)
                moveMade = True
                animate = True

            else:
                AIMove = ChessAI.findBestMoveNegaMaxAlphaBeta(gs, validMoves)
                if AIMove:
                    pass
                else:
                    AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True

        else:
            pass

        # ---------------------------------------------------------- After Move Stuff ----------------------------------------------------------
        if moveMade:  # Only check the validmoves again when we do a move
                      # ..to avoid doing this every frame!
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock) # To animate the last made move
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        
        # ========================================================== GameOver options ========================================================
        # Black Wins
        if (gs.whiteToMove and gs.checkmate) or (gs.whiteToMove and len(validMoves) == 0):
            drawText(screen, 'Black Wins')
            gameover = True
        # White Wins
        elif (not gs.whiteToMove and gs.checkmate) or (not gs.whiteToMove and len(validMoves) == 0):
            drawText(screen, "White Wins")
            gameover = True
        # Withdraw
        elif gs.stalemate:
            drawText(screen, '-Withdraw-')

        clock.tick(MAX_FPS)
        p.display.flip()



# ======================================================== GHRAPHICS ========================================================================

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != (): # To make sure user has selected sth at all!
        r, c = sqSelected
        if gs.board[int(r)][int(c)][0] == ('w' if gs.whiteToMove else 'b'): # User selected their own pieces

            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency value --> 255: solid   0: trasparent
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            # Highlight moves from tht square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draws Squares on the board.
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of those squares.
 
# Draw the squares on the board. The top left square is always light!
def drawBoard(screen):
    global colors
    # colors = [p.Color('white'), p.Color('gray')]
    # colors = [p.Color( 232 ,235, 239), p.Color( 125, 135, 150)] # Diamond
    colors = [p.Color(234, 221, 202), p.Color(193, 154, 107)] # Light Brown Theme



    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw the pieces on the board using the current GameState.board 
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--': # Not empty sqaure
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Animating the move
def animateMove (move, screen, board, clock):
    global colors
    coords = [] # List of coords tht the anime will move through it
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # Frames to move one square of anime
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount )
        # dR*frame/frameCount --> this is the ratio of how much
        # we have been through our anime!
        drawBoard(screen)
        drawPieces(screen, board)

        # Erase the piece moved from its ending!
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Draw captured piece onto the rectangle
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)


            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # 60 FPS

def drawText(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    textObject = font.render(text, 0, p.Color('White'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == '__main__':
    main()





