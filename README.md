# CSCI-B551 FA2021 Assignment 1

### Group Members: Aashay Gondalia (aagond), Harsh Atha (hatha)


## Part 1: The 2021 Puzzle

### 1.1 Problem Statement

The puzzle is a 5x5 board with each tile containing numbers from 1 to 25 arranged randomly on it. The objective is to reach the goal state as shown in image below:

![image](https://media.github.iu.edu/user/18130/files/1aa03d80-27d1-11ec-8136-a1ab93e2b043)

Output returns a list containing all the necessary moves for reaching the goal state.
Possible list of moves is R, L, U, D, Icc, Ic, Occ, Oc.

1. For sliding rows, R(right) or L(left), followed by the row number indicating the row to move left or right. The row numbers range from 1-5.

2. For sliding columns, U(up) or D(down), followed by the column number indicating the column to moveup or down. The column numbers range from 1-5.

3. For rotations, I(inner) or O(outer), followed by whether the rotation is clockwise (c) or counterclock-wise (cc).


### Given skeletal code requires a successor function, solve function and a function to check if we have reached goal state.

### 1.2 Search Abstraction:

1. Set of States S: It can be defined as a set of all possible board states that can be reached.
2. Successor function: It returns a board that has undergone Right/Left or Up/Down or Icc/Ic/Occ/Oc moves on it. There are 24 different possible combinations here. (Based on: R1-R5, L1-L5, U1-U5, D1-D5, Icc, Ic, Occ, Oc.)
3. Initial State: The initial State is the randomized board that we are supposed to solve.
4. Goal State: To get the board to look like image attached above.
5. Cost = 1 for each move we make towards goal state.

### 1.3 Questions asked:

1. In this problem, what is the branching factor of the search tree?
Ans: The current problem has 24 possible moves it can make (Based on: R1-R5, L1-L5, U1-U5, D1-D5, Icc, Ic, Occ, Oc). The branching of this search tree hence is 24.

2. If  the  solution  can  be  reached  in  7  moves,  about  how  many  states  would  we  need  to  explore  before  we found it if we used BFS instead of A* search?  A rough answer is fine.
Ans: If BFS is used then the algorithm would explore each state at that depth (moves in this case) of the tree. The value of states visited (assuming the goal state is present in last node of that branch and depth) can be given by (b^(d+1)-1)/(b-1). In our case since d=depth of tree(moves used) = 7 and b=branching factor = 24, the number of states visited is ((24^8)-1)/23 which can be computed to approximately 4,785,883,225 states. This is in order of 4.79x10^9 states.

### 1.4 Approaches used:
#### Manhattan Distance mentioned in lines below indicates the minimum Manhattan Distance. As rows/columns can roll over to the other side after a move, normal formula for Manhattan distance is ineffective. We need to consider moves where it can reach goal in 1 move rather than 4. (Ex: 1 Up > 4 Down)


A) The first approach we went with was trying to solve the board like n-Puzzle using Manhattan Distance or Misplaced Tile count. As 1 move in our puzzle affects multiple tiles this heuristic was inadmissible. 

B) We tried a wide variety of heuristics by taking logarithmic of Manhattan Distance and Misplaced tile count, Count of tiles that are in same row/column as goal state, Count of tiles that are in same column/row but in inverted positions, Weighted average combination of Manhattan + Misplaced tile count. One approach we used was to empirically use weights for no. of moves required for tile to reach goal location. Ex: Current state has 10 correctly placed tiles, 12 tiles requiring 1 move, 1 tile with 2 moves and so on. By using weights that increased with increasing order of moves, we could estimate a heuristic closer to optimal solution. But all seemed inadmissible.

C) Final heuristic we used seems admissible but is weak. We split the board into 3 given subgroups and find maximum number of moves required for that tile to reach goal state. The 3 groups selected were Corners, Middle element and midpoints of inner ring.

They can be seen as below:

![image](https://media.github.iu.edu/user/18130/files/06f4d700-27d1-11ec-9392-c9c086fd72ff)

Heuristic returned was sum of Max Manhattan Dist of subgroup 1(marked in Indigo), Manhattan Dist of subgroup 2 (marked in red) and sum of Max Manhattan Dist of subgroup 3 (marked in brown).


The code solves given test cases and returns optimal solutions. Testing was done on additionally generated random cases of similar length as well


### 1.5 References used for part 1:
1. Skeletal code and Rotate/sliding code provided by Prof. David Crandall and B551 AI team.
2. https://www.quora.com/How-do-I-create-a-nested-list-from-a-flat-one-in-Python
3. https://stackoverflow.com/questions/53319487/finding-the-index-of-elements-in-nested-list?rq=1

## Part 2 Road Trip!

### 2.1 Problem Statement:

It’s not too early to start planning a post-pandemic road trip!  If you stop and think about it, finding theshortest driving route between two distant places — say, one on the east coast and one on the west coast ofthe U.S. — is extremely complicated.  There are over 4 million miles of roads in the U.S. alone, and trying all possible paths between two places would be nearly impossible.  So how can mapping software like Google Maps find routes nearly instantly?  The answer is A* search!

Task: To find good driving directions between pair of cities given by the user.
The optimal route will be based on different cost functions like Fewest segments (less number of nodes), Shortest Total Distance (Distance) , Fastest route (Time), Fastest route, in expectation for a delivery driver (Delivery).

The dataset has inconsistencies and where GPS file does not have coordinates of highway intersections. 

### 2.2 Search Abstraction


1. Set of States S: All possible cities or highway intersections that can be visited on the given map.
2. Successor function: It returns a city/intersection that is neighboring the current junction on our route.
3. Initial State: City of origin or highway intersection from where we begin the trip.
4. Goal State: Destination city or intersection, where we want to end our trip.
5. Cost:
    a. Segments: For every node we visit, cost is added by 1.
    b. Distance: Adds the distance we have travelled to reach that point.
    c. Time: Adds the time required to reach the given point.
    d. Delivery: Time required by driver from previous point (Subject to cost of fallen package). 

### 2.3 Approaches used:

In this problem, we try to find the optimal path based on different cost functions ['segments', 'distance', 'time', 'delivery']. There are two datasets provided 'road-segments.txt' and 'city-gps.txt' with the problem. The city-gps dataset is devoid of the co-ordinate information relating to the highways across the country.

#### 2.3.1 Handling missing co-ordinates

1. Approach 1: Triangulation (average of the co-ordinate values of the neighbouring cities)
The estimate_coordinates function in the code handles the estimation of the coordinates of a given node(city/highway) by assigning the mean of the coordinate values of the neighbouring nodes. 

2. Approach 2: Triangulation (weighted-average of the co-ordinate values of the neighbouring cities)
The estimate_coordinates function in the code handles the estimation of the coordinates of a given node(city/highway) by assigning the weighted mean of the coordinate values of the neighbouring nodes.

3. Approach 3: Carrying forward the value of the last city before the node in the route.
The highway node is assigned the coordinates of the last city in the path whose coordinates are present in the city-gps dataset. 

#### 2.3.2 Search methodology

The search starts from the 'start' (start city / start highway). A priority queue is maintained to explore the state with the best cost function value (i.e. the least value (high priority)). The priority queue sends the best state at any given time to be analyzed and returns a list of its neighbouring cities based on the costs given by the heuristic value and the actual cost (distance / time / delivery_time between A-B). The heuristic used in these cases is the Haversine distance between two points with given coordinates. The haversine is a good estimate to find the shortest point-to-point displacement on the surface of the earth. 

#### 2.3.3 Cost Functions used
##### 1. 'segments' :  cost = (haversine_distance / avg_distance) + (steps + 1)
##### 2. 'distance' :  cost = haversine_distance + total_distance
##### 3. 'time'     :  cost = (haversine_distance / max_speed) + total_time
##### 4. 'delivery' :  cost = (haversine_distance / max_speed)  + total_delivery_time

Using these cost function as a summation of admissible heuristics and parameter_value, finds the optimal path using the A* search for any given cost function (argument). The program exits with the best path for a given cost function once it reaches the destination node. 


### References used for part 2
1. https://www.movable-type.co.uk/scripts/latlong.html

## Part 3: Choosing teams

### 3.1 Problem Statement:

In a certain Computer Science course, students are assigned to groups according to preferences that they specify. Students can either prefer to work alone, groups of two or in groups of three. They can also choose to avoid working with some people or work with random people. Based on these preferences, the course staff assigns groups. Based on a wide variety of given conditions, the course staff has to spend a lot of time reading emails, discussing issues in assigned groups, grading assignments and holding meetings for Academic Integrity. The goal here is to minimize the work required by course staff. 


### 3.2 Search Abstraction

1. Set of States S: The set of states can be defined by all possible combinations that can be derived from the given input. 
2. Successor function: It returns a combination of groups based on the current state subject to the global constraints (In this case, length of group should be greater than 0 and should not exceed 3)
3. Initial State: Initial state in this case is subject to the approach used. It can start with a random shuffling of groups or groups that are assigned based on some preference to begin with. In our approach we have initialised the start state to be n groups of 1 person each, where n is the total number of people. 
4. Goal State: Ideally, the goal state is finding a combination of groups where the time required by the course staff to grade assignments, hold meetings is the least.
5. Cost: There is no cost involved technically. This is a minimization (optimization) problem and the switching from 1 group to another (State 1 to State 2) does not involve a cost in between.

### 3.3 Approach Used:

In this problem, we first split the given people into 'n' individual groups of 1 person each, where n is total number of people. We maintain a column of the people that the student has requested to work with (denoted by desired_team) and people he has specifically requested not to work with (denoted by enemy). The simplest way to first check if the student has gotten the desired group is to see if they have the same number of members they asked for. Based on number of groups, number of people not in desired group, number of "enemies" in the same group and number of desired people not in the group we compute the total cost of the group.

The "form_groups_bottom_up" function is our successor function that creates a combination of groups based on the current groupings we have. As the name suggests it starts from the bottom (all groups of solo individuals) and works its way up to find the next combination. It checks for the next "neighbor" and creates a possible combination of multiple groups that still satisfy our constraints. 

Once a group has been created we compute it's total cost and check if the given group is better than the previous one with respect to the total cost. If the successor of the current state gives a lower cost than the current state, then the successor becomes our current state and we try to find an optimized neighbour of the given successor. We also keep track of the groups that have been previously created to ensure we don't iterate over the same combination again and again. The algorithm returns a dictionary containing list of groups, total cost that is the least or most optimal in the time given for it to compute.

Figure representation the flow:

![image](https://media.github.iu.edu/user/18130/files/09573f80-286a-11ec-89b4-08920082dbbb)
