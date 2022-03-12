import pygame
import os
import chess_rules as rules
import search_algo as algo

#Set players, 'engine' or 'user'
WPLAYER = 'user'
BPLAYER = 'engine'

# Colors, sizes and window
pygame.font.init()
COORD_FONT = pygame.font.SysFont('comicsans', 50)


WIDTH, HEIGHT = 700, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess!")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (220, 220, 220)
DARK = (20, 50, 200)
FPS = 60

size_square = 65 

#Start position for board printing
x_0 = WIDTH // 2 - 4 * size_square
y_0 = HEIGHT // 2 - 4 * size_square

#Squares of the chessboard
class square():
	def __init__(self, x_coord, y_coord, color):
		self.x = x_coord
		self.y = y_coord
		self.coord = (x_coord, y_coord)
		self.color = color

	#For printing and mouse movements of the pieces
	def rect(self):
		return pygame.Rect(x_0 + self.x * size_square, y_0 + self.y * size_square, size_square, size_square)


#Chess pieces
pieces_name = ('bB', 'bN', 'bQ', 'wB', 'wN', 'wQ', 'bK', 'bp', 'bR', 'wK', 'wp', 'wR')

pieces = dict()

for name in pieces_name:
	pieces[name] = pygame.image.load(os.path.join('chess_pieces', name + '.png'))
	pieces[name] = pygame.transform.scale(pieces[name], (size_square, size_square))

#Chessboard (no pieces)
board = []
for col in range(8):
	for lin in range(8):
		__, r = divmod(col + lin, 2)
		if r:
			color = DARK
		else:
			color = WHITE

		board.append(square(col, lin, color))

#Initializing current_state board
current_state = rules.start_board_position()


#Graphics
coordenadas = 'abcdefgh'

def draw_window(current_state, click_change = False, clicking = False, clicked_square = None, target_square = None):
	#Squares and coordinates
	WIN.fill(GREY)
	for square in board:
		pygame.draw.rect(WIN, square.color, square.rect())
	for line in range(8):
		draw_text = COORD_FONT.render(str(8-line), 1, BLACK)
		WIN.blit(draw_text, (x_0 - size_square // 2, y_0 + line * size_square + size_square // 3))
	for column in range(8):
			draw_text = COORD_FONT.render(coordenadas[column], 1, BLACK)
			WIN.blit(draw_text, (x_0 + column * size_square + size_square //  3, y_0 + 8 * size_square + size_square // 3))

	#Pieces
	if clicked_square and clicking:
		clicked_piece = ''
		for a in range(8):
			for b in range(8):
				piece = current_state.pieces[a, b]
				if piece:
					if (a, b) != clicked_square.coord:
						WIN.blit(pieces[piece], (x_0 + a * size_square, y_0 + b * size_square))
					else:
						clicked_piece = piece
						mx, my = pygame.mouse.get_pos()
		if clicked_piece:
			WIN.blit(pieces[clicked_piece], (mx - size_square // 2, my - size_square // 2))
	else:
		for a in range(8):
			for b in range(8):
				piece = current_state.pieces[a, b]
				if piece: 
					WIN.blit(pieces[piece], (x_0 + a * size_square, y_0 + b * size_square))

	#w_check, b_check = check_king(current_state)
	#if w_check:
	#	draw_text = COORD_FONT.render("White king in check", 1, BLACK)
	#elif b_check:
	#	draw_text = COORD_FONT.render("Black king in check", 1, BLACK)
	#else:
	#	draw_text = COORD_FONT.render("", 1, BLACK)

	#WIN.blit(draw_text, (0, 0))

	status = current_state.special[rules.special_dict['game_finished']]
	if status == 'w':
		draw_text = COORD_FONT.render("White wins", 1, BLACK)
	elif status == 'b':
		draw_text = COORD_FONT.render("Black wins", 1, BLACK)
	elif status == 'Draw':
		draw_text = COORD_FONT.render("Draw", 1, BLACK)
	else:
		draw_text = COORD_FONT.render("", 1, BLACK)

	WIN.blit(draw_text, (0, 0))


	pygame.display.update()

def user_selector(current_state):
	clock = pygame.time.Clock()
	run = True
	clicking = False 		#True if click is holded, false otherwise
	click_change = False	#True if click changed, false if not
	clicked_square = None	#Currently selected square, class square()
	target_square = None	#Where to move the piece
	while run:
		clock.tick(FPS)
		click_change = False
		mx, my = pygame.mouse.get_pos() #Mouse position
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if clicking == False:
						click_change = True
					else:
						click_change = False
					clicking = True
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					click_change = True
					clicking = False
		
		if click_change and clicking:
			for square in board:
				if square.rect().collidepoint(mx, my):
					clicked_square = square

		elif click_change and not clicking:
			for square in board:
				if square.rect().collidepoint(mx, my):
					target_square = square

		elif not click_change and not clicking:
			clicked_square = None
			target_square = None

		#Send move info to check if it's legal; if so, change current_state accordingly 
		if clicked_square and target_square and clicked_square != target_square:
			children = rules.legal_move_check(clicked_square.coord, target_square.coord, current_state)
			if children != False:
				if rules.finished_game_check(children):
					children.special[rules.special_dict['game_finished']] = rules.finished_game_check(children)
				return children

		draw_window(current_state, click_change, clicking, clicked_square, target_square)



def main(current_state):
	run = True
	while run:
		turn = current_state.turn
		if turn == 'w':
			if WPLAYER == 'engine':
				next_state = algo.minimax_algo(current_state, True, 2)
				#next_state = algo.first_instinct_move(current_state)
			else:
				next_state = user_selector(current_state)
		elif turn == 'b':
			if BPLAYER == 'engine':
				next_state = algo.minimax_algo(current_state, False, 2)
				#next_state = algo.random_move(current_state)
			else:
				next_state = user_selector(current_state)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()

		if next_state != False:
			current_state = next_state
			
		draw_window(current_state)


if __name__ == "__main__":
	main(current_state)
