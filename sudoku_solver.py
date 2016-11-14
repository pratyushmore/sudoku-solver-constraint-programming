"""
This piece of software takes in, as input, a sudoku board, and checks if it is solvable. 
If it is, it outputs a setting of spots which would solve the problem. 
If it is not, it says so.

Author: Pratyush More
"""

import numpy as np
from z3 import *

SIDE_LENGTH = 9

BOX_LENGTH = 3


"""
Sample board layout
"""
board_layout = np.array([[5, 3, None, None, 7, None, None, None, None],\
[6, None, None, 1, 9, 5, None, None, None],\
[None, 9, 8, None, None, None, None, 6, None],\
[8, None, None, None, 6, None, None, None, 3],\
[4, None, None, 8, None, 3, None, None, 1],\
[7, None, None, None, 2, None, None, None, 6],\
[None, 6, None, None, None, None, 2, 8, None],\
[None, None, None, 4, 1, 9, None, None, 5],\
[None, None, None, None, 8, None, None, 7, 9]])


def sudoku_solver(board):
    """
    Checks if a sudoku instance is solvable. If it is, return the setting of
    spots which would be a solution to this particular instance.

    Arguments:
        board (numpy int array): A 9x9 numpy array. Spots set to a certain number should contain
        this number. Other spots should be set to None.

    Returns:
        numpy int array: Returns a new numpy array with the solution to the sudoku
        if one exists. IF NO SOLUTION EXISTS, None IS RETURNED.

    """
    s = Solver()
    s.add(get_formula_all_parts(board))
    #s.print_formula()
    ans = np.zeros((SIDE_LENGTH, SIDE_LENGTH))
    if s.check() == sat:
        m = s.model()
        counter = 0
        for d in m.decls():
            if m[d] == True:
                counter += 1
                s = d.name()
                parts = s.split("_")[1:]
                num = int(parts[0])
                x = int(parts[1])
                y = int(parts[2])
                ans[x, y] = num
        if counter != SIDE_LENGTH * SIDE_LENGTH:
            print "Error: More settings than available spots."
        else:
            print "Here is the solution to your sudoku:\n"
            print ans
            return ans
    else:
        print "Unsolvable Sudoku."
        return None

def spot_entry(num, x, y):
	return Bool('_'+str(num)+'_' + str(x) + '_' + str(y))


def get_formula_all_parts(board):
    formula_for_all_spots = get_formula_for_all_spots(board)
    initialisation = initialize(board)
    atleast_one = get_formula_for_fill_all()
    return And([formula_for_all_spots, initialisation, atleast_one])


def get_formula_for_fill_all():
    main_list = []
    for i in range(SIDE_LENGTH):
        for j in range(SIDE_LENGTH):
            sublist = []
            for num in range(1, SIDE_LENGTH + 1):
                sublist.append(spot_entry(num, i, j))
            main_list.append(Or(sublist))
    return And(main_list)

def initialize(board):
	list1 = []
	for i in range(SIDE_LENGTH):
		for j in range(SIDE_LENGTH):
			num = board[i, j]
			if num is not None:
				list1.append(spot_entry(num, i, j))
	return And(list1)

def get_formula_for_all_spots(board):
	formula_for_all_boxes = []
	for i in range(SIDE_LENGTH):
		for j in range(SIDE_LENGTH):
			entry = board[i, j]
			if entry is not None:
				part = get_formula_for_entry(i, j, entry)
			else:
				part = get_formula_for_blank(i, j)
			formula_for_all_boxes.append(part)
	return And(formula_for_all_boxes)

def get_formula_for_entry(x, y, entry):
	list1 = []
	for i in range(SIDE_LENGTH):
		if i != y:
			list1.append(Implies(spot_entry(entry, x, y), Not(spot_entry(entry, x, i))))
		if i != x:
			list1.append(Implies(spot_entry(entry, x, y), Not(spot_entry(entry, i, y))))
	box_x_min = x/BOX_LENGTH * BOX_LENGTH
	box_x_max = (x/BOX_LENGTH + 1) * BOX_LENGTH
	box_y_min = y/BOX_LENGTH * BOX_LENGTH
	box_y_max = (y/BOX_LENGTH + 1) * BOX_LENGTH
	for i in range(box_x_min, box_x_max):
		for j in range(box_y_min, box_y_max):
			if i != x and j != y:
				 list1.append(Implies(spot_entry(entry, x, y), Not(spot_entry(entry, i, j))))
	for i in range(1, SIDE_LENGTH):
		if i != entry:
			list1.append(Implies(spot_entry(entry, x, y), Not(spot_entry(i, x, y))))
	return And(list1)

def get_formula_for_blank(x, y):
	list1 = [get_formula_for_entry(x, y, i) for i in range(1, SIDE_LENGTH + 1)]
	#list2 = [item for sublist in list1 for item in sublist]
	return And(list1)

sudoku_solver(board_layout)