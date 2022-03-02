#All game logic is contained in this file
#
#

import numpy as np
import search_algo as search
import heapq

#Dictionary of special moves
special_dict = dict()
special_dict['w0-0'] = 0
special_dict['b0-0'] = 1
special_dict['w0-0-0'] = 2
special_dict['b0-0-0'] = 3
special_dict['passant'] = 4
special_dict['game_finished'] = 5


#This class must contain all specifications of a position
class state_board():
	def __init__(self, pieces = np.zeros(64, dtype = 'U2').reshape(8,8), turn = 'w'):
		self.pieces = pieces
		self.turn = turn
		self.special = [False for i in range(6)]
		self.parent = None

	def place_piece(self, piece_name, coord):
		self.pieces[coord] = piece_name

	#info_type: 'b0-0', 'b0-0-0', 'w0-0', 'w0-0-0', 'passant', ...
	def change_special(self, info_type, value):
		self.special[special_dict[info_type]] = value

	def change_turn(self, turn):
		self.turn = turn

	def set_parent(self, parent):
		self.parent = parent

	def copy(self):
		copy_state = state_board()
		copy_state.pieces = np.copy(self.pieces)
		copy_state.turn = self.turn
		copy_state.special = self.special.copy()
		copy_state.parent = self.parent

		return copy_state

#Dict to translate chess algebraic coordinates (ex. 'b5', 'e4') to internal coordinates
algebraic_to_internal = dict()
__aux_coord = "abcdefgh"

for i in range(8):
	for j in range(8):
		algebraic_to_internal[__aux_coord[i] + str(j + 1)] = (i, 7 - j)

#Set state to initial chess position
def start_board_position():

	#Pawns
	state = state_board()
	for i in range(8):
		state.place_piece('bp', (i, 1))
		state.place_piece('wp', (i, 6))
	
	#Pieces
	state.place_piece('bR', algebraic_to_internal['a8'])
	state.place_piece('bR', algebraic_to_internal['h8'])
	state.place_piece('bN', algebraic_to_internal['b8'])
	state.place_piece('bN', algebraic_to_internal['g8'])
	state.place_piece('bB', algebraic_to_internal['c8'])
	state.place_piece('bB', algebraic_to_internal['f8'])
	state.place_piece('bQ', algebraic_to_internal['d8'])
	state.place_piece('bK', algebraic_to_internal['e8'])
	state.place_piece('wR', algebraic_to_internal['a1'])
	state.place_piece('wR', algebraic_to_internal['h1'])
	state.place_piece('wN', algebraic_to_internal['b1'])
	state.place_piece('wN', algebraic_to_internal['g1'])
	state.place_piece('wB', algebraic_to_internal['c1'])
	state.place_piece('wB', algebraic_to_internal['f1'])
	state.place_piece('wQ', algebraic_to_internal['d1'])
	state.place_piece('wK', algebraic_to_internal['e1'])
	
	#Castling rights
	state.change_special('b0-0', True)
	state.change_special('w0-0', True)
	state.change_special('b0-0-0', True)
	state.change_special('w0-0-0', True)
	
	return state

def reverse_color(color):
	if color == 'w':
		return 'b'
	elif color == 'b':
		return 'w'

#Piece scope: These are not necessarily legal moves. To check if it's actually legal, a few constraints relating to the king must be met

#Return scope of piece at coord, at board state 'state'
def piece_scope(coord, state):
	x, y = coord
	moves = []
	if state.pieces[coord] == '':
		return moves
	piece = state.pieces[coord][1]
	color = state.pieces[coord][0]

	#Pawn
	if piece == 'p':
		#White pawn
		if color == 'w':
			if y == 6: #Pawn initial position
				if not state.pieces[x, y-1]:
					moves.append((x, y-1))
					if not state.pieces[x, y-2]:
						moves.append((x, y-2))
			elif y > 0: #Any other pawn position
				if not state.pieces[x, y-1]:
					moves.append((x, y-1))

			#Possible pawn captures
			if y > 0:
				if x > 0:
					if state.pieces[x-1, y-1] and state.pieces[x-1, y-1][0] == 'b':
						moves.append((x-1, y-1))
				if x < 7:
					if state.pieces[x+1, y-1] and state.pieces[x+1, y-1][0] == 'b':
						moves.append((x+1, y-1))

			#Passant
			if y == 3:
				if x-1 >= 0:
					if (color, x-1) == state.special[special_dict['passant']]:
						moves.append((x-1, 2))
				if x+1 <= 7:
					if (color, x+1) == state.special[special_dict['passant']]:
						moves.append((x+1, 2))
		#Black pawn
		elif color == 'b':
			if y == 1: #Pawn initial position
				if not state.pieces[x, y+1]:
					moves.append((x, y+1))
					if not state.pieces[x, y+2]:
						moves.append((x, y+2))
			elif y < 7: #Any other pawn position
				if not state.pieces[x, y+1]:
					moves.append((x, y+1))

			#Possible pawn captures
			if y < 7:
				if x > 0:
					if state.pieces[x-1, y+1] and state.pieces[x-1, y+1][0] == 'w':
						moves.append((x-1, y+1))
				if x < 7:
					if state.pieces[x+1, y+1] and state.pieces[x+1, y+1][0] == 'w':
						moves.append((x+1, y+1))
			#Passant
			if y == 4:
				if x-1 >= 0:
					if (color, x-1) == state.special[special_dict['passant']]:
						moves.append((x-1, 5))
				if x+1 <= 7:
					if (color, x+1) == state.special[special_dict['passant']]:
						moves.append((x+1, 5))
	#Bishop
	if piece == 'B':
		aux_x = x
		aux_y = y
		while aux_x > 0 and aux_y > 0:
			aux_x -= 1
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x > 0 and aux_y < 7:
			aux_x -= 1
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x < 7 and aux_y > 0:
			aux_x += 1
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x < 7 and aux_y < 7:
			aux_x += 1
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))
	#Rook
	if piece == 'R':
		aux_x = x
		aux_y = y
		while aux_x < 7:
			aux_x += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_y < 7:
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x > 0:
			aux_x -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_y > 0:
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

	#Queen
	if piece == 'Q':
		aux_x = x
		aux_y = y
		while aux_x > 0 and aux_y > 0:
			aux_x -= 1
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x > 0 and aux_y < 7:
			aux_x -= 1
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x < 7 and aux_y > 0:
			aux_x += 1
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x < 7 and aux_y < 7:
			aux_x += 1
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x < 7:
			aux_x += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_y < 7:
			aux_y += 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_x > 0:
			aux_x -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

		aux_x = x
		aux_y = y
		while aux_y > 0:
			aux_y -= 1
			if state.pieces[aux_x, aux_y]:
				if state.pieces[aux_x, aux_y][0] != color:
					moves.append((aux_x, aux_y))
				break
			moves.append((aux_x, aux_y))

	#Knight
	if piece == 'N':
		if x-1 >= 0 and y-2 >= 0:
			if not state.pieces[x-1, y-2] or state.pieces[x-1, y-2][0] != color:
				moves.append((x-1, y-2))
		if x+1 <= 7 and y-2 >= 0:	
			if not state.pieces[x+1, y-2] or state.pieces[x+1, y-2][0] != color:
				moves.append((x+1, y-2))
		if x-1 >= 0 and y+2 <= 7:
			if not state.pieces[x-1, y+2] or state.pieces[x-1, y+2][0] != color:
				moves.append((x-1, y+2))
		if x+1 <= 7 and y+2 <= 7:	
			if not state.pieces[x+1, y+2] or state.pieces[x+1, y+2][0] != color:
				moves.append((x+1, y+2))
		if x-2 >= 0 and y-1 >= 0:
			if not state.pieces[x-2, y-1] or state.pieces[x-2, y-1][0] != color:
				moves.append((x-2, y-1))
		if x+2 <= 7 and y-1 >= 0:	
			if not state.pieces[x+2, y-1] or state.pieces[x+2, y-1][0] != color:
				moves.append((x+2, y-1))
		if x-2 >= 0 and y+1 <= 7:
			if not state.pieces[x-2, y+1] or state.pieces[x-2, y+1][0] != color:
				moves.append((x-2, y+1))
		if x+2 <= 7 and y+1 <= 7:	
			if not state.pieces[x+2, y+1] or state.pieces[x+2, y+1][0] != color:
				moves.append((x+2, y+1))

	#King
	if piece == 'K':
		if x+1 <= 7:
			if not state.pieces[x+1, y] or state.pieces[x+1, y][0] != color:
				moves.append((x+1, y))
			if y+1 <= 7:
				if not state.pieces[x+1, y+1] or state.pieces[x+1, y+1][0] != color:
					moves.append((x+1, y+1))
			if y-1 >= 0:
				if not state.pieces[x+1, y-1] or state.pieces[x+1, y-1][0] != color:
					moves.append((x+1, y-1))
		if x-1 >= 0:
			if not state.pieces[x-1, y] or state.pieces[x-1, y][0] != color:
				moves.append((x-1, y))
			if y+1 <= 7:
				if not state.pieces[x-1, y+1] or state.pieces[x-1, y+1][0] != color:
					moves.append((x-1, y+1))
			if y-1 >= 0:
				if not state.pieces[x-1, y-1] or state.pieces[x-1, y-1][0] != color:
					moves.append((x-1, y-1))
		if y+1 <= 7:
			if not state.pieces[x, y+1] or state.pieces[x, y+1][0] != color:
				moves.append((x, y+1))
		if y-1 >= 0:
			if not state.pieces[x, y-1] or state.pieces[x, y-1][0] != color:
				moves.append((x, y-1))

		#Extra: Castling
		if color == 'w':
			if state.special[special_dict['w0-0']] and coord == (4, 7):
				if not state.pieces[x+1, y] and not state.pieces[x+2, y]:
					moves.append((x+2, y))
			if state.special[special_dict['w0-0-0']] and coord == (4, 7):
				if not state.pieces[x-1, y] and not state.pieces[x-2, y] and not state.pieces[x-3, y]:
					moves.append((x-2, y))
		if color == 'b':
			if state.special[special_dict['b0-0']] and coord == (4, 0):
				if not state.pieces[x+1, y] and not state.pieces[x+2, y]:
					moves.append((x+2, y))
			if state.special[special_dict['b0-0-0']] and coord == (4, 0):
				if not state.pieces[x-1, y] and not state.pieces[x-2, y] and not state.pieces[x-3, y]:
					moves.append((x-2, y))

	return moves

#Find if kings are in check in given state
def check_king(state):
	#Find kings
	for i in range(8):
		for j in range(8):
			if state.pieces[i,j] == 'wK':
				wK = (i,j)
			elif state.pieces[i,j] == 'bK':
				bK = (i,j)
	try:
		wK
		bK
	except:
		print("Missing king in the board")
		return -1
				

	#Check if any king is at enemy piece scope
	w_check = False
	b_check = False
	for i in range(8):
		for j in range(8):
			piece = state.pieces[i, j]
			if not piece:
				continue
			if piece[0] == 'b':
				if wK in piece_scope((i, j), state):
					w_check = True
			elif piece[0] == 'w':
				if bK in piece_scope((i, j), state):
					b_check = True
	
	return w_check, b_check

#Test if given move is legal. If it is, return child state
def legal_move_check(start, target, state, promotion_piece = None):
	start_x, start_y = start
	target_x, target_y = target

	#No piece selected, no move
	if not state.pieces[start]:
		return False 

	color, piece = state.pieces[start]
	turn = state.turn

	#If turn is not respected, move is invalid
	if turn != color:
		return False
	
	captured_piece = state.pieces[target]
	
	#If trying to capture own piece, move is invalid
	if captured_piece:
		if captured_piece[0] == turn:
			return False

	#Check if move is at piece scope
	if target not in piece_scope(start, state):
		return False

	#Mark if the move is a special move
	special_move = False
	if piece == 'K':
		if target_x - start_x == 2:
			special_move = '0-0'
		if target_x - start_x == -2:
			special_move = '0-0-0'
	
	if piece == 'p':
		if not state.pieces[target] and start_x != target_x:
			special_move = 'passant'

	
	child_state = state.copy()

	#Finally move the piece and make last checks to see if move is legal
	illegal_move = False
	if special_move == False:
		child_state.pieces[target] = child_state.pieces[start]
		child_state.pieces[start] = ''
		if piece == 'p':
			if target_y == 0 or target_y == 7:
				child_state.pieces[target] = color + 'Q'

		#Not ending in check
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True
			
	elif special_move == '0-0':

		#Not in check to castle
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

		#Not in check in the way to castling
		child_state.pieces[(start_x + target_x) // 2, start_y] = child_state.pieces[start]
		child_state.pieces[start] = ''
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

		#Not in check at the end of castling
		child_state.pieces[target] = child_state.pieces[(start_x + target_x) // 2, start_y]
		child_state.pieces[(start_x + target_x) // 2, start_y] = ''
		child_state.pieces[target_x -1, target_y] = child_state.pieces[7, target_y]
		child_state.pieces[7, target_y] = ''
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

	elif special_move == '0-0-0':

		#Not in check to castle
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

		#Not in check in the way to castling
		child_state.pieces[(start_x + target_x) // 2, start_y] = child_state.pieces[start]
		child_state.pieces[start] = ''
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

		#Not in check at the end of castling
		child_state.pieces[target] = child_state.pieces[(start_x + target_x) // 2, start_y]
		child_state.pieces[(start_x + target_x) // 2, start_y] = ''
		child_state.pieces[target_x + 1, target_y] = child_state.pieces[0, target_y]
		child_state.pieces[0, target_y] = ''
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

	elif special_move == 'passant':
		child_state.pieces[target] = child_state.pieces[start]
		child_state.pieces[start] = ''
		child_state.pieces[target_x, start_y] = ''
		w_check, b_check = check_king(child_state)
		check = w_check if turn == 'w' else b_check
		if check:
			illegal_move = True

	if illegal_move:
		return False

	#Update rest of informations of child_state

	child_state.turn = reverse_color(child_state.turn)

	#Lost castling rights due to king move
	if piece == 'K':
		if child_state.special[special_dict[color + '0-0']]:
			child_state.special[special_dict[color + '0-0']] = False
		if child_state.special[special_dict[color + '0-0-0']]:
			child_state.special[special_dict[color + '0-0-0']] = False

	#Lost castling rights due to rook move
	if piece == 'R':
		if color == 'w':
			if start == (7, 7) and child_state.special[special_dict[color + '0-0']]:
				child_state.special[special_dict[color + '0-0']] = False
			if start == (0, 7) and child_state.special[special_dict[color + '0-0-0']]:
				child_state.special[special_dict[color + '0-0-0']] = False
		if color == 'b':
			if start == (7, 0) and child_state.special[special_dict[color + '0-0']]:
				child_state.special[special_dict[color + '0-0']] = False
			if start == (0, 0) and child_state.special[special_dict[color + '0-0-0']]:
				child_state.special[special_dict[color + '0-0-0']] = False

	#Two mover pawn; possible passant available
	child_state.special[special_dict['passant']] = False
	if piece == 'p':
		if abs(target_y - start_y) == 2:
			child_state.special[special_dict['passant']] = (reverse_color(color), start_x)

	child_state.set_parent(state)

	return child_state

#Newer implementation, better for the algorithm
#From current state, return all next possible states
def new_child_states(state):
	coordinates = []
	for i in range(8):
		for j in range(8):
			coordinates.append((i, j))

	turn = state.turn
	children = []
	i = 0
	for coord in coordinates:
		if not state.pieces[coord]:
			continue
		elif state.pieces[coord][0] != turn:
			continue
		else:
			target_list = piece_scope(coord, state)
			for target in target_list:
				children_state = legal_move_check(coord, target, state)
				if children_state != False:
					i += 1
					if finished_game_check(children_state):
						children_state.special[special_dict['game_finished']] = finished_game_check(children_state)
					if turn == 'w':
						children.append((- search.evaluator(children_state), i, children_state))
					else:
						children.append((search.evaluator(children_state), i, children_state))
	heapq.heapify(children)

	while children:
		yield	heapq.heappop(children)[2]


	#yield heapq.heappop(children)[2]

#From current state, return all next possible states
def child_states(state):
	coordinates = []
	for i in range(8):
		for j in range(8):
			coordinates.append((i, j))

	turn = state.turn
	children = []
	for coord in coordinates:
		if not state.pieces[coord]:
			continue
		elif state.pieces[coord][0] != turn:
			continue
		else:
			target_list = piece_scope(coord, state)
			for target in target_list:
				children_state = legal_move_check(coord, target, state)
				if children_state != False:
					if finished_game_check(children_state):
						children_state.special[special_dict['game_finished']] = finished_game_check(children_state)
					children.append(children_state)

	return children

def finished_game_check(state):
	coordinates = []
	for i in range(8):
		for j in range(8):
			coordinates.append((i, j))

	turn = state.turn
	for coord in coordinates:
		if not state.pieces[coord]:
			continue
		elif state.pieces[coord][0] != turn:
			continue
		else:
			target_list = piece_scope(coord, state)
			for target in target_list:
				children_state = legal_move_check(coord, target, state)
				if children_state != False:
					return False

	w_check, b_check = check_king(state)
	if turn == 'w':
		check = w_check
	elif turn == 'b':
		check = b_check

	if check: #Checkmate
		return reverse_color(turn)
	else:	  #Stalemate
		return 'Draw'

