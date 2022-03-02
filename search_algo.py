import numpy as np
import chess_rules as rules

piece_value = dict()
piece_value['wp'] = 1.0
piece_value['bp'] = -1.0
piece_value['wN'] = 3.0
piece_value['bN'] = -3.0
piece_value['wB'] = 3.1
piece_value['bB'] = -3.1
piece_value['wR'] = 5.0
piece_value['bR'] = -5.0
piece_value['wQ'] = 9.0
piece_value['bQ'] = -9.0
piece_value['wK'] = 0.0
piece_value['bK'] = 0.0
piece_value['']   = 0.0

def basic_evaluator(state):
	status = state.special[rules.special_dict['game_finished']]
	if status == 'w':
		return float('inf')
	elif status == 'b':
		return float('-inf')
	elif status == 'Draw':
		return 0.0

	coordinates = []
	for i in range(8):
		for j in range(8):
			coordinates.append((i, j))

	#Material count
	material = 0.0
	for coord in coordinates:
		material += piece_value[state.pieces[coord]]

	return material


def evaluator(state):
	status = state.special[rules.special_dict['game_finished']]
	if status == 'w':
		return float('inf')
	elif status == 'b':
		return float('-inf')
	elif status == 'Draw':
		return 0.0

	coordinates = []
	for i in range(8):
		for j in range(8):
			coordinates.append((i, j))

	#Material count
	material = 0.0
	for coord in coordinates:
		material += piece_value[state.pieces[coord]]

	#Scope count
	scope = 0
	for coord in coordinates:
		piece = state.pieces[coord]
		if piece:
			if piece[0] == 'w':
				scope += len(rules.piece_scope(coord, state))
			if piece[0] == 'b':
				scope -= len(rules.piece_scope(coord, state))

	return 4 * material + scope

def minimax_algo(state, maximizing_player, depth = 5, alpha = float('-inf'), beta = float('inf')):
	def minimax(state, maximizing_player, depth, alpha, beta):
		status = state.special[rules.special_dict['game_finished']]
		if depth == 0 or status:
			return evaluator(state), False
	
		if maximizing_player:
			max_eval = float('-inf')
			best_children = False
			for child in rules.new_child_states(state):
				eval, __ = minimax(child, False, depth - 1, alpha, beta)
				if max_eval != max(max_eval, eval) or max_eval == float('-inf'):
					max_eval = max(max_eval, eval)
					best_children = child
				alpha = max(alpha, eval)
				if beta <= alpha:
					break
			return max_eval, best_children
	
		else:
			min_eval = float('inf')
			best_children = False
			for child in rules.new_child_states(state):
				eval, __ = minimax(child, True, depth - 1, alpha, beta)
				if min_eval != min(min_eval, eval) or min_eval == float('inf'):
					min_eval = min(min_eval, eval)
					best_children = child
				beta = min(beta, eval)
				if beta <= alpha:
					break
			return min_eval, best_children

	valuation, best_state = minimax(state, maximizing_player, depth, alpha, beta)
	return best_state

def basic_minimax(state, maximizing_player, depth = 5, alpha = float('-inf'), beta = float('inf')):
	status = state.special[rules.special_dict['game_finished']]
	if depth == 0 or status:
		return basic_evaluator(state), False

	if maximizing_player:
		max_eval = float('-inf')
		best_children = False
		for child in rules.child_states(state):
			eval, __ = basic_minimax(child, False, depth - 1, alpha, beta)
			if max_eval != max(max_eval, eval):
				max_eval = max(max_eval, eval)
				best_children = child
			alpha = max(alpha, eval)
			if beta <= alpha:
				break
		return max_eval, best_children

	else:
		min_eval = float('inf')
		best_children = False
		for child in rules.child_states(state):
			eval, __ = basic_minimax(child, True, depth - 1, alpha, beta)
			if min_eval != min(min_eval, eval):
				min_eval = min(min_eval, eval)
				best_children = child
			beta = min(beta, eval)
			if beta <= alpha:
				break
		return min_eval, best_children

def random_move(state):
	possible_states = rules.child_states(state)
	number_states = len(possible_states)
	if number_states:
		rdm = np.random.randint(0, number_states)
		return possible_states[rdm]

	return False

def first_instinct_move(state):
	turn = state.turn
	possible_states = rules.child_states(state)
	number_states = len(possible_states)
	scores = [[0, i] for i in range(number_states)]
	if number_states:
		for i in range(number_states):
			scores[i][0] = evaluator(possible_states[i])
		scores.sort()
		if turn == 'w':
			return possible_states[scores[-1][1]]
		if turn == 'b':
			return possible_states[scores[0][1]]

	return False

