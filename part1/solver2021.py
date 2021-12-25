#!/usr/local/bin/python3
# solver2021.py : 2021 Sliding tile puzzle solver
#
# Code by: Harsh K Atha (hatha), Aashay Gondalia (aagond)
#
# Based on skeleton code by D. Crandall & B551 Staff, September 2021
#
#References used are as follows:
    #1. https://www.quora.com/How-do-I-create-a-nested-list-from-a-flat-one-in-Python to create list of lists in compact manner
    #2. a) Test code given by CSCI B551 team for Left,right, up, down, Icc, Ic, Occ, Oc moves.
    #2. b) for tweaking given code using a different approach.
    #3. To find coordinates of elements in a nested list, I referred https://stackoverflow.com/questions/53319487/finding-the-index-of-elements-in-nested-list?rq=1

import sys
import numpy as np
import copy
from queue import PriorityQueue

ROWS=5
COLS=5

def printable_board(board):
    return [ ('%3d ')*COLS  % board[j:(j+COLS)] for j in range(0, ROWS*COLS, COLS) ]


def heuristic_used(board):
    
    #Split the board and took corners, vertices of inner ring and the center most element.
    
    groups=[1,5,21,25,13,8,12,18,14]
    """
    groups is a combination of following 3 subgroups
    
    
    1 _ _ _ 5                         _ _ _ _ _                             _ _ _ _ _
    _ _ _ _ _                         _ _ _ _ _                             _ _  8 _ _ 
    _ _ _ _ _                         _ _ 13 _ _                            _ 12 _14 _
    _ _ _ _ _                         _ _ _ _ _                             _ _ 18 _ _
    21 _ _ _ 25                       _ _ _ _ _                             _ _ _ _ _
    
    Corners of the goal state       Center most element of goal state       Vertices of Inner ring
    Subgroup 1                      Subgroup 2                              Subgroup 3
    """
    # Tupled coordinates of selected groups of goal state
    goal_coord=[(0,0),(0,4),(4,0),(4,4),(2,2),(1,2),(2,1),(3,2),(2,3)]   
    coordinates=[]
    
    #Below section stores coordinates of selected group from current state in a list: coordinates
    for tile in groups:
        for ind, row in enumerate(board):
            if tile in row:
                coordinates.append((ind,row.index(tile)))
    
    min_dist_list=[]
    #Below part finds the shortest Manhattan distance to it's goal state
    for i in range(len(goal_coord)):
        dist1= abs(goal_coord[i][0]-coordinates[i][0])+abs(goal_coord[i][1]-coordinates[i][1])
        dist2= ROWS-abs(goal_coord[i][0]-coordinates[i][0])+abs(goal_coord[i][1]-coordinates[i][1])
        dist3= abs(goal_coord[i][0]-coordinates[i][0])+COLS-abs(goal_coord[i][1]-coordinates[i][1])
        dist4= ROWS-abs(goal_coord[i][0]-coordinates[i][0]) +COLS-abs(goal_coord[1][0]-coordinates[i][1])
        min_dist_list.append(min(dist1,dist2,dist3,dist4))
    
    #Returns Max of manhattan of subgroup1 + Middle element + Max of manhattan of subgroup3
    return max(min_dist_list[:3])+ min_dist_list[4]+ max(min_dist_list[5:])




def move_right(board, row):
    
      boardR=copy.deepcopy(board)
      boardR[row] = boardR[row][-1:] + boardR[row][:-1]
      return boardR

def move_left(board, row):
    #"""Move the given row to one position left"""
      #print('Row : ', row, '\nBoard L :', board[row])
      boardL=copy.deepcopy(board)
      boardL[row] = boardL[row][1:] + boardL[row][:1]
      return boardL

def rotate_right(board,row,residual):
    board[row] = [board[row][0]] +[residual] + board[row][1:]
    #print(' Rotate\n:' ,(board))
    residual=board[row].pop()
    return residual

def rotate_left(board,row,residual):
    
    board[row] = board[row][:-1] + [residual] + [board[row][-1]]
    residual=board[row].pop(0)
    return residual

def move_clockwise(board):
    """Move the outer ring clockwise"""
    boardC=copy.deepcopy(board)
    boardC[0]=[boardC[1][0]]+boardC[0]
    #print(boardC)
    residual=boardC[0].pop()
    #print(residual)
    boardC=transpose_board(boardC)
    #print(np.array(boardC))
    residual=rotate_right(boardC,-1,residual)
    #print(residual)
    boardC=transpose_board(boardC)
    residual=rotate_left(boardC,-1,residual)
    boardC=transpose_board(boardC)
    residual=rotate_left(boardC,0,residual)
    boardC=transpose_board(boardC)
    return boardC

def move_cclockwise(board):
    """Move the outer ring counter-clockwise"""
    boardCC=copy.deepcopy(board)
    boardCC[0]=boardCC[0]+[boardCC[1][-1]]
    residual=boardCC[0].pop(0)
    boardCC=transpose_board(boardCC)
    residual=rotate_right(boardCC,0,residual)
    boardCC=transpose_board(boardCC)
    residual=rotate_right(boardCC,-1,residual)
    boardCC=transpose_board(boardCC)
    residual=rotate_left(boardCC,-1,residual)
    boardCC=transpose_board(boardCC)
    return boardCC

def transpose_board(board):
  """Transpose the board --> change row to column"""
  boardT=copy.deepcopy(board)
  return [list(col) for col in zip(*boardT)]


# return a list of possible successor states
def successors(current_state):
    
    next_state = []
    for i in range(ROWS):
        boardL = move_left(current_state,i)
        boardR = move_right(current_state,i)
        boardU = transpose_board(move_left(transpose_board(current_state), i))
        boardD = transpose_board(move_right(transpose_board(current_state), i))
        next_state.append([boardL, "L"+ str(i+1)])
        next_state.append([boardR, "R"+ str(i+1)])
        next_state.append([boardU, "U"+str(i+1)])
        next_state.append([boardD, "D"+str(i+1)])

    boardOC = move_clockwise(current_state)
    next_state.append([boardOC, "Oc"])
    boardOCC = move_cclockwise(current_state)
    next_state.append([boardOCC, "Occ"])
    
    boardIC=np.array(current_state)
    inner_board=boardIC[1:-1,1:-1].tolist()
    inner_board = move_clockwise(inner_board)
    boardIC[1:-1,1:-1]=np.array(inner_board)
    boardIC=boardIC.tolist()
    next_state.append([boardIC, "Ic"])
    
    boardICC=np.array(current_state)
    inner_board=boardICC[1:-1,1:-1].tolist()
    inner_board = move_cclockwise(inner_board)
    boardICC[1:-1,1:-1]=np.array(inner_board)
    boardICC=boardICC.tolist()
    next_state.append([boardICC, "Icc"])
    
    return next_state
    

# check if we've reached the goal
def is_goal(current_state):
    goal_state= [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20], [21, 22, 23, 24, 25]]
    return current_state == goal_state

def solve(initial_board):
    
    initial_board_list= list(initial_board)
    #Referred below to find non-clunky way of creating nested list from list
    #https://www.quora.com/How-do-I-create-a-nested-list-from-a-flat-one-in-Python
    original_board = [initial_board_list[i:i + ROWS] for i in range(0, len(initial_board_list), ROWS)]
    fringe = PriorityQueue()
    fringe.put((0,original_board,'',0))
    already_visited=[]
    already_visited.append(original_board)
    
    while fringe :       
        cost_heuristic , current_state, route_taken, count_steps =fringe.get()
        steps = count_steps+1 #Increase the cost after every move
        
        if is_goal(current_state):
            route_taken=route_taken.split(",")
            route_taken.pop() #Remove last comma
            return route_taken
        
        for state_move in successors(current_state):
            next_state, moves =  state_move[0], state_move[1]
            if next_state not in already_visited:
                already_visited.append(next_state)
                fringe.put((heuristic_used(next_state)+steps,next_state, route_taken+moves+",", steps))
    return [] #In case no steps needed/fringe empty

#Please don't modify anything below this line

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected a board filename"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != ROWS*COLS:
        raise(Exception("Error: couldn't parse start state file"))

    print("Start state: \n" +"\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    route = solve(tuple(start_state))
    
    print("Solution found in " + str(len(route)) + " moves:" + "\n" + " ".join(route))