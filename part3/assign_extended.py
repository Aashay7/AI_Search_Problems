#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: name IU ID
#
# Based on skeleton code by D. Crandall and B551 Staff, September 2021
#

import sys
import time
import pandas as pd
from queue import PriorityQueue

def read_dataset(input_file):
    '''
    The read_dataset function reads the input file into a 
    pandas dataframe. The dataframe is used by the main program
    as a lookup table to achieve the best solution.

    ARGS    : input_file [STRING]
    RETURNS : dataset [pd.DataFrame]
    '''

    dataset = pd.read_csv(input_file, header = None,  sep=' ')
    dataset.columns = ['node', 'desired_team', 'enemy']
    dataset['desired_team'] =  dataset['desired_team'].str.split('-') 
    dataset['enemy'] =  dataset['enemy'].str.split('-')
    return dataset

def calculate_cost(group_combn_list, dataset):
    '''
    The calculate_cost function takes the group_combn_list[LIST] and the dataset[pd.DataFrame]
    as the input parameters. This function calculates the total cost (time (in minutes)) of a 
    given group_combn_list (group combination) and returns the total_cost[INT] to the solver.

    The total_cost is calculated based on the given conditions in the problem question. 
    The function also creates a summary_table for a given group_combn_list for visual help.
    NOTE: Here, the term 'enemy' resembles the person that the subject does not want to be 
    paired with in the same group.

    ARGS    : group_combn_list[LIST], dataset[pd.DataFrame]
    RETURNS : total_cost[INT]
    
    '''
    # 5 minutes to grade each assignment. 5 * num_teams
    # Student assigned a different group size. 2 * such_students
    # Student not assigned to someone they requested * 60 * 0.05 - also multiple cases possible for same student
    # Each student is assigned to someone they requested not to work with. 10 * all such cases.

    summary_table = pd.DataFrame(columns= [
        'node', 
        'desired_team', 
        'enemy',
        'assigned_team', 
        'num_people_not_in_same_group',
        'no_of_desired_teammates_not_in_assigned_group',
        'no_of_enemy_assigned'
    ])

    num_teams = len(group_combn_list)
    total_cost = (num_teams * 5)
    for i, row in dataset.iterrows():
        for j, assigned_team in enumerate(group_combn_list):
            assigned_team_list = group_combn_list[j].split('-')
            if dataset.iloc[i,0] in assigned_team_list:

                # Checking Condition 1 : The desired team is not the same size as the assigned team for a given node(person).
                summary_table.loc[i] = [dataset.loc[i,'node'], dataset.loc[i,'desired_team'], dataset.loc[i, 'enemy'], assigned_team_list, 0, 0, 0]
                #num_people_not_in_same_group = abs(len(summary_table.loc[i,'desired_team']) - len(summary_table.loc[i,'assigned_team']))
                num_people_not_in_same_group = len(summary_table.loc[i,'desired_team']) != len(summary_table.loc[i,'assigned_team'])
                summary_table.loc[i,'num_people_not_in_same_group'] = int(num_people_not_in_same_group)
                
                # Checking Condition 2 : A desired teammate is not in the assigned team. 
                # Two seperate meetings if both students request each other.
                d_counter = 0
                for d_teammate in summary_table.loc[i,'desired_team']:
                    if (d_teammate not in summary_table.loc[i,'assigned_team'] and d_teammate != 'xxx' and d_teammate != 'zzz'):
                        d_counter += 1
                summary_table.loc[i,'no_of_desired_teammates_not_in_assigned_group'] = d_counter

                # Checking Condition 3 : The case where the person that was requested by the 
                # given node to not include in their group, is infact, assigned to the same group
                # as the give node. 
                e_counter= 0
                for e_teammate in summary_table.loc[i,'enemy']:
                    e_counter = sum([enemy in assigned_team_list for enemy in  e_teammate.split(',')])
                summary_table.loc[i,'no_of_enemy_assigned']  = e_counter 

                total_cost += (num_people_not_in_same_group * 2)  + (d_counter * 3) + (e_counter * 10)
    return total_cost
  
def matrix_approach(dataset):
    '''
    Alternate approach to the problem. 
    
    '''
    # Try - n*n entries approach. Maintain a matrix? Confusion Matrix...
    confusion_matrix = pd.DataFrame(-1.67, columns=dataset['node'], index=dataset['node'], )
    team_size_preference = {val[0] : len(val) for val in dataset['desired_team']}
    print('Team size preference : ', team_size_preference)
    #  for name in dataset['node']:
    # n_row = name on row index, n_col = name of col index.
    print(confusion_matrix)
    for n_row, row in dataset.iterrows():
        #print(row['node'],' :: ',row['desired_team'], ' :: ', row['enemy'])
        for n_col in row['desired_team']:
            if ((n_col != 'xxx') and (n_col != 'zzz') and (row['node'] != n_col)): 
                #print('Friend ::: n_col ', n_col)
                confusion_matrix.loc[row['node'], n_col] = -5.0
    
    for n_row, row in dataset.iterrows():
        print(row['node'],' :: ',row['desired_team'], ' :: ', row['enemy'])
        for n_col_list_raw in row['enemy']:
            if ((n_col_list_raw != 'xxx') and (n_col_list_raw != 'zzz') and (n_col_list_raw != '_') and (row['node'] != n_col_list_raw)): 
                for n_col in n_col_list_raw.split(','):
                    confusion_matrix.loc[row['node'], n_col] = -10.0

    
    confusion_matrix['total'] = confusion_matrix.sum(axis=1)
    print(confusion_matrix)
    list_of_students = dataset['node'].values
    #group_combn_list = []
    print(list_of_students)
    

def form_groups_bottom_up(groups, dataset):
    '''
    The form_groups_bottom_up function creates new combination
    of groups based on a given group(arg: groups). 

    Suppose : 
    >   form_groups_bottoms_up(['A','B','C'], dataset)
    >   ['A-B', 'C'], ['A-C', 'B'], ['B-C', 'A']

    The function handles the repitition of combinations of groups. 
    From the above mentioned example, the function does not include
    the combinations ['B-A', 'C'], ['C-A', 'B'], ['C-B', 'A'] in the 
    output list.

    The given example describes the combinations that will be returned
    by the form_groups_bottom_up for a given input group.

    ARGS    : groups[LIST], dataset[pd.DataFrame]
    RETURNS : output_list[LIST of LIST]
   
    '''
    combinations = []
    list_of_groups = [group.split('-') for group in groups]
    for group_a in list_of_groups:
        for group_b in list_of_groups:
            new_set = list(set(group_a).union(set(group_b)))
            if ((set(group_a) != set(group_b)) and (set(new_set) not in [combo for combo in combinations]) and (0  < len(new_set) <= 3 )):
                real_set = list_of_groups.copy()
                real_set.remove(group_a)
                real_set.remove(group_b)
                real_set.append(new_set)
                if real_set not in combinations:
                    combinations.append(real_set)
    
    # Creating desired output format 
    output_list = []
    for i, combo in enumerate(combinations):
        temp_list = []
        for j, group in enumerate(combo):
            if(len(group) > 1):
                val = '-'.join(group)
            else:
                val = group[0]
            temp_list.append(val)
        cost = calculate_cost(temp_list, dataset)
        output_list.append((cost, temp_list))
    return output_list



def solver(input_file):
    """
    1. This function should take the name of a .txt input file in the format indicated in the assignment.
    2. It should return a dictionary with the following keys:
        - "assigned-groups" : a list of groups assigned by the program, each consisting of usernames separated by hyphens
        - "total-cost" : total cost (time spent by instructors in minutes) in the group assignment
    3. Do not add any extra parameters to the solver() function, or it will break our grading and testing code.
    4. Please do not use any global variables, as it may cause the testing code to fail.
    5. To handle the fact that some problems may take longer than others, and you don't know ahead of time how
       much time it will take to find the best solution, you can compute a series of solutions and then
       call "yield" to return that preliminary solution. Your program can continue yielding multiple times;
       our test program will take the last answer you 'yielded' once time expired.
    """
    
    dataset = read_dataset(input_file)
    list_of_students = dataset['node'].values
    # Initial Assignment : BOTTOMS UP APPROACH   ## GREEDY 
    all_groups = list_of_students.copy()
    globalcost = float('inf')
    pQueue = PriorityQueue()
    visited = []
    # Loading Initial State i.e. considering the state where every student is 
    # assigned an individual group. 
    # Example for test1.txt  -> ['djcran', 'sahmaini', 'sulagaop', 'fanjun', 'nthakurd', 'vkvats']
    pQueue.put(((calculate_cost(all_groups, dataset), list(all_groups))))   

    while len(pQueue.queue) != 0:
        cost, list_of_groups = pQueue.get()
        if cost < globalcost:
            globalcost = cost
            yield({"assigned-groups": list_of_groups, "total-cost" : cost})
        next_groups_list = form_groups_bottom_up(list_of_groups, dataset)
        for next_groups in next_groups_list:
            if (next_groups not in visited and len(next_groups) > 0):
                pQueue.put((next_groups[0], next_groups[1]))
                visited.append(next_groups[1])

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
    
