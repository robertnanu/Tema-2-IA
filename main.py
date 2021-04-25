from typing import Sized
import pygame
from pygame.locals import *
from copy import deepcopy
import time
import sys

# initialize the pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

choose_color = input("Cu ce culoare doriti sa jucati?  Ex: BLACK sau WHITE\n")




# RGB
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
bg = (204, 102, 0)

if choose_color == 'BLACK':
    choose_color = BLACK
else:
    choose_color = WHITE

font = pygame.font.SysFont('Constantia', 30)

# pentru a putea adauga imaginea cu coroana din folder ul de assets
CROWN = pygame.transform.scale(pygame.image.load('assets/crown.png'), (44, 25))

# nu l mai folosesc
FPS = 60

clicked = False

# create the screen
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Nanu Robert-Ionut --> Dame')

# -----------------------------------------------------------------------
class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        """
            @param row: randul pe care ne aflam in matricea tablei
            @param col: coloana pe care ne aflam in matricea tablei
            @param color: culoarea piesei respective
        """
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

        """
        if self.color == WHITE:
            self.direction = -1
        else:
            self.direction = 1     
        """

    def calc_pos(self):
        """
            calculez exact mijlocul patratelului meu pentru a putea construi cercurile
        """
        # right in the middle of the square because we have circular pieces
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE //2

    def make_king(self):
        """
            Inseamna ca piesa devine rege
        """
        self.king = True
    
    def draw(self, win):
        """
            Aceasta functie deseneaza un cerc mare gri si inca unul mai mic de o alta culoare pe a da impresia de contur gri la fiecare piesa
            @param win: display ul creat la inceput
        """
        radius = SQUARE_SIZE // 2 - self.PADDING
        # I'm just drawing a smaller circle inside of a big circle
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        """
            Reinitializeaza randul si coloana in functie de noua mutare
            @param row: randul
            @param col: coloana
        """
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return str(self.color)

class Board:
    def __init__(self):
        self.board = []
        #self.selected_piece = None
        # number of pieces remaining
        self.black_left = self.white_left = 12
        self.black_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        """
            Imi desenez tabla de joc, cu patrate negre si albe
            Umplu intregul ecran cu negru iar apoi din doi in doi marchez cu alb
            @param win: display ul creat la inceput
        """
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, WHITE, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        """
            O estimare
        """
        return self.white_left - self.black_left + (self.white_kings * 0.5 - self.black_left * 0.5)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        """
            Muta piesa "piece" pe locul cu randul "row" si coloana "col"
            @param piece: piesa pe care dorim s-o mutam
            @param row: randul unde dorim sa realizam mutarea
            @param col: coloana unde dorim sa realizam mutarea
        """
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.black_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)
        
        print('Stare initiala:\n')
        print("  |  0  1  2  3  4  5  6  7")
        print("---------------------------")
        t = -1
        for row in range(ROWS):
            t += 1
            print(t, end = " ")
            print('|', end = " ")
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        print(' X', end = " ")
                    elif row > 4:
                        print(' 0', end = " ")
                    else:
                        print(' #', end = " ")
                else:
                    print(' #', end = " ")
            print()

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        """
            Remove piece
            @param pieces: piesele
        """
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == BLACK:
                    self.black_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.white_left <= 0:
            return BLACK
        elif self.black_left <= 0:
            return WHITE
        
        return None 
    
    def get_valid_moves(self, piece):
        """
            Obtine mutarile valide ale unei piese selectate
            @param piece: piesa careia vrem sa i obtinem mutarile valide
        """
        moves = {} # empty dictionary
        # La cheia de mai jos voi tine minte punctele peste care am sarit pentru a ajunge acolo
        # (4, 5): [(3, 4)]
        left = piece.col - 1 # ce am in stanga
        right = piece.col + 1 # ce am in dreapta
        row = piece.row

        # verific daca mutarea este valida in jos sau sus, in functie de culoare sau daca este sau nu rege
        if piece.color == WHITE or piece.king: # row - 3: nu vreau sa ma uit mai departe de 2 piese, -1: mergi in sus, left: de unde incepem cu coloana
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
    
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """
            Aceasta functie traverseaza in stanga jos sau sus in functie de culoare, pe diagonale, pentru a vedea mutarile
            posibile si pentru a verifica daca este posibila cucerirea mai multor piese dintr o singura mutare
            @param start: randul de unde pornesc
            @param stop: randul la care sa ma opresc
            @param color: culoarea piesei careia doresc sa i aflu posibilele mutari valide
            @param left: punctul de plecarea din punct de vedere a coloanei atunci cand traversam in stanga
            @param step: merg in sus sau in jos in functie de culoare
            @param skipped[]: voi muta doar in punctele unde am sarit peste anumite piese
        """
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0: # am iesit de pe tabla
                break
            
            current = self.board[r][left]
            if current == 0: # am gasit o mutare valida
                if skipped and not last: # am sarit deja peste ceva si nu mai pot sari peste altceva
                    break
                elif skipped: # am sarit peste mai multe piese
                    moves[(r, left)] = last + skipped # combinam piesa sarita anterior cu piesa pe care o pot sari acum pentru a sti ca pot sari peste mai multe piese
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                        # daca putem sari peste mai multe piese
                    moves.update(self._traverse_left(r+step, row, step, color, left-1,skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1,skipped=last))
                break
            elif current.color == color: # nu putem sari peste o piesa de aceeasi culoare cu a noastra
                break
            else:
                last = [current]

            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        """
            Aceasta functie traverseaza in dreapta jos sau sus in functie de culoare, pe diagonale, pentru a vedea mutarile
            posibile si pentru a verifica daca este posibila cucerirea mai multor piese dintr o singura mutare
            @param start: de unde pornesc
            @param stop: cand sa ma opresc
            @param color: culoarea piesei careia doresc sa i aflu posibilele mutari valide
            @param right: punctul de plecarea din punct de vedere a coloanei atunci cand traversam in dreapta
            @param step: merg in sus sau in jos in functie de culoare
            @param skipped[]: voi muta doar in punctele unde am sarit peste anumite piese
        """
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r,right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1,skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1,skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1
        
        return moves

    def __repr__(self):
        return str(self.board)

class Game:
    def __init__(self, win):
            self.selected = None
            self.board = Board()
            self.turn = BLACK
            self.valid_moves = {}
            self.win = win
    
    def update(self):
        """
            Se ocupa de desenarea mutarilor valide
        """
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def winner(self):
        return self.board.winner()

    def reset(self):
        self.selected = None
        self.board = Board()
        self.turn = BLACK
        self.valid_moves = {}
    
    def select(self, row, col):
        """
            Aceasta functie se va ocupa direct si de mutare, daca este valida
            @param row: randul
            @param col: coloana
        """
        # daca am selectat ceva
        if self.selected:
            result = self._move(row, col) #realizam mutarea la row si col daca este posibila
            if not result: #mutarea incercata anterior nu a fost valida
                self.selected = None #altfel vom incerca sa selectam alta piesa pentru a o muta
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True #am selectat o piesa valida
            
        return False

    def _move(self, row, col):
        """
            Vrem sa realizam mutarea la row si col
            @param row: randul
            @param col: coloana
        """
        piece = self.board.get_piece(row, col)
        # sa nu alegem sa mutam cumva intr un loc unde exista deja o piesa
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col) #realizam mutarea
            skipped = self.valid_moves[(row, col)]
            if skipped: # inseamna ca am sarit peste ea si trebuie eliminata de pe tabla
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        """
            @param moves: (moves e un dictionar) mutarile valide returnate in urma algoritmilor de traverse realizate in class Board
        """
        for move in moves: # loops prin toate cheile dictionarului
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        """
            Schimba culoarea celui care trebuie sa mute
        """
        self.valid_moves = {} # sa dispara punctele albastre in urma mutarii
        if self.turn == BLACK:
            self.turn = WHITE
        else:
            self.turn = BLACK

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        
        #print(str(self.board))
        marime = len(str(self.board))
        print("\nTabla dupa mutarea calculatorului:\n")
        print("  |  0  1  2  3  4  5  6  7")
        print("---------------------------")
        i = 0
        t = 0
        ok = 0
        print(ok, end = " ")
        print("|", end = " ")
        while i < marime:
            if str(self.board)[i] == '0' and str(self.board)[i-1] == '(':
                print(' X', end = " ")
                t += 1
                i += 7
            elif str(self.board)[i] == '2' and str(self.board)[i-1] == '(':
                print(' 0', end = " ")
                t += 1
                i += 7
            elif str(self.board)[i] == '0':
                print(' #', end = " ")
                t += 1
                i += 2
            if t == 8:
                print()
                ok += 1
                if ok < 8:
                    print(ok, end = " ")
                    print("|", end = " ")
                t = 0
            i += 1
            #print(i)
            #print(marime)
        """
        if self.turn == BLACK:
            print("\nEste randul pieselor albe:\n")
        else:
            print("\nEste randul pieselor negre:\n")
        """

        self.change_turn()

    def __repr__(self):
        return str(self.board)

# -----------------------------------------------------------------------

class Buton:
	def __init__(self, display=None, left=0, top=0, w=0, h=0,culoareFundal=(53,80,115), culoareFundalSel=(89,134,194), text="", font="arial", fontDimensiune=16, culoareText=(255,255,255), valoare=""):
		self.display=display		
		self.culoareFundal=culoareFundal
		self.culoareFundalSel=culoareFundalSel
		self.text=text
		self.font=font
		self.w=w
		self.h=h
		self.selectat=False
		self.fontDimensiune=fontDimensiune
		self.culoareText=culoareText
		#creez obiectul font
		fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
		self.textRandat=fontObj.render(self.text, True , self.culoareText) 
		self.dreptunghi=pygame.Rect(left, top, w, h) 
		#aici centram textul
		self.dreptunghiText=self.textRandat.get_rect(center=self.dreptunghi.center)
		self.valoare=valoare

	def selecteaza(self,sel):
		self.selectat=sel
		self.deseneaza()
	def selecteazaDupacoord(self,coord):
		if self.dreptunghi.collidepoint(coord):
			self.selecteaza(True)
			return True
		return False

	def updateDreptunghi(self):
		self.dreptunghi.left=self.left
		self.dreptunghi.top=self.top
		self.dreptunghiText=self.textRandat.get_rect(center=self.dreptunghi.center)

	def deseneaza(self):
		culoareF= self.culoareFundalSel if self.selectat else self.culoareFundal
		pygame.draw.rect(self.display, culoareF, self.dreptunghi)	
		self.display.blit(self.textRandat ,self.dreptunghiText) 

class GrupButoane:
	def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=10,left=0, top=0):
		self.listaButoane=listaButoane
		self.indiceSelectat=indiceSelectat
		self.listaButoane[self.indiceSelectat].selectat=True
		self.top=top
		self.left=left
		leftCurent=self.left
		for b in self.listaButoane:
			b.top=self.top
			b.left=leftCurent
			b.updateDreptunghi()
			leftCurent+=(spatiuButoane+b.w)

	def selecteazaDupacoord(self,coord):
		for ib,b in enumerate(self.listaButoane):
			if b.selecteazaDupacoord(coord):
				self.listaButoane[self.indiceSelectat].selecteaza(False)
				self.indiceSelectat=ib
				return True
		return False

	def deseneaza(self):
		#atentie, nu face wrap
		for b in self.listaButoane:
			b.deseneaza()

	def getValoare(self):
		return self.listaButoane[self.indiceSelectat].valoare


############# ecran initial ########################

def deseneaza_alegeri(display) :
	btn_alg=GrupButoane(
		top=30, 
		left=30,  
		listaButoane=[
			Buton(display=display, w=150, h=30, text="Player VS Player", valoare="pvp"), 
			Buton(display=display, w=150, h=30, text="Player VS Computer", valoare="pvc")
			],
		indiceSelectat=1)
	btn_juc=GrupButoane(
		top=100, 
		left=30, 
		listaButoane=[
			Buton(display=display, w=35, h=30, text="Easy", valoare="e"), 
			Buton(display=display, w=35, h=30, text="Hard", valoare="h")
			], 
		indiceSelectat=0)
	ok=Buton(display=display, top=170, left=30, w=40, h=30, text="ok", culoareFundal=(155,0,55))
	btn_alg.deseneaza()
	btn_juc.deseneaza()
	ok.deseneaza()
	while True:
		for ev in pygame.event.get(): 
			if ev.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif ev.type == pygame.MOUSEBUTTONDOWN: 
				pos = pygame.mouse.get_pos()
				if not btn_alg.selecteazaDupacoord(pos):
					if not btn_juc.selecteazaDupacoord(pos):
						if ok.selecteazaDupacoord(pos):
							display.fill((0,0,0)) #stergere ecran 
							#tabla_curenta.draw(WIN)
							return btn_juc.getValoare(), btn_alg.getValoare()
		pygame.display.update()



def minimax(position, depth, max_player, game):
    if depth == 0 or position.winner() != None:
        return position.evaluate(), position
    
    if max_player:
        maxEval = float('-inf')
        best_move = None
        if choose_color == BLACK:
            for move in get_all_moves(position, WHITE, game):
                evaluation = minimax(move, depth-1, False, game)[0]
                maxEval = max(maxEval, evaluation)
                if maxEval == evaluation:
                    best_move = move
        else:
            for move in get_all_moves(position, BLACK, game):
                evaluation = minimax(move, depth-1, False, game)[0]
                maxEval = max(maxEval, evaluation)
                if maxEval == evaluation:
                    best_move = move
        
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in get_all_moves(position, RED, game):
            # aplic algoritmul minimax pe toate mutarile posibile
            evaluation = minimax(move, depth-1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        
        return minEval, best_move


def simulate_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)

    return board


def get_all_moves(board, color, game):
    moves = []

    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            draw_moves(game, board, piece)
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, game, skip)
            moves.append(new_board)
    
    return moves


def draw_moves(game, board, piece):
    valid_moves = board.get_valid_moves(piece)
    board.draw(game.win)
    pygame.draw.circle(game.win, (0,255,0), (piece.x, piece.y), 50, 5) # dark green
    game.draw_valid_moves(valid_moves.keys())
    pygame.display.update()
    pygame.time.delay(100)

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():

    run = True
    clock = pygame.time.Clock()
    dificultate, tip_joc = deseneaza_alegeri(WIN)
    print(tip_joc)
    print(dificultate)
    time_startGame = int(round(time.time() * 1000))
    game = Game(WIN)

    if tip_joc == 'pvc':
        # inseamna ca joc impotriva AI
        mutari_calc = 0
        mutari_om = 0
        while run:
            clock.tick(FPS)
            """
            for row in range(ROWS):
                for col in range(COLS):
                    piece = game.board[row][col]
                    if piece == BLACK
            """

            if game.turn != choose_color:
                if game.turn == BLACK:
                    print("\nEste randul pieselor negre:")
                else:
                    print("\nEste randul pieselor albe:")
                # Get the time in ms before the move
                t_before = int(round(time.time() * 1000))
                if choose_color == BLACK:
                    if dificultate == 'e':
                        value, new_board = minimax(game.get_board(), 6, WHITE, game)
                    else:
                        value, new_board = minimax(game.get_board(), 86, WHITE, game)
                else:
                    if dificultate == 'e':
                        value, new_board = minimax(game.get_board(), 6, BLACK, game)
                    else:
                        value, new_board = minimax(game.get_board(), 86, WHITE, game)
                game.ai_move(new_board)
                mutari_calc += 1
                # Get the time in ms after the move
                t_after = int(round(time.time() * 1000))
                print("\nCalculatorul a \"gandit\" timp de " + str(t_after - t_before) + " milisecunde.")
                if game.turn == BLACK:
                    print("\nEste randul pieselor negre:")
                else:
                    print("\nEste randul pieselor albe:")

            if game.winner() != None:
                if game.winner() == BLACK:
                    print("\nNegrul este castigator!")
                    WIN.fill(BLACK)
                else:
                    print("\nAlbul este castigator!")
                    WIN.fill(WHITE)
                time_endGame = int(round(time.time() * 1000))
                print("Jocul a rulat timp de " + str(time_endGame - time_startGame) + " milisecunde.")
                print("\nIn aceasta partida calculatorul a realizat: " + str(mutari_calc) + " mutari, iar omul a realizat: " + str(mutari_om // 2) + " mutari.")
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    time_endGame = int(round(time.time() * 1000))
                    print("\nJocul a fost oprit fortat prin inchiderea ferestrei!")
                    print("\nJocul a rulat timp de " + str(time_endGame - time_startGame) + " milisecunde.")
                    print("\nIn aceasta partida calculatorul a realizat: " + str(mutari_calc) + " mutari, iar omul a realizat: " + str(mutari_om // 2) + " mutari.")
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)
                    mutari_om += 1

            game.update()
        
        pygame.quit()
        sys.exit()
    else:
        # inseamna ca joc impotriva player
        while run:
            
            if game.winner() != None:
                print(game.winner())
                time_endGame = int(round(time.time() * 1000))
                print("Jocul a rulat timp de " + str(time_endGame - time_startGame) + " milisecunde.")
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    time_endGame = int(round(time.time() * 1000))
                    print("Jocul a rulat timp de " + str(time_endGame - time_startGame) + " milisecunde.")
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

            game.update()
        
        pygame.quit()

main()