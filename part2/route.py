#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Aashay Gondalia (aagond), Harsh K Atha (hatha)
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021
#


# !/usr/bin/env python3
import sys
from queue import PriorityQueue
import numpy as np
import pandas as pd


def read_datasets():
    '''
    The read_dataset function makes use of the pandas library to 
    get the 'road-segments.txt' and 'city-gps.txt' datasets in to the dataframe object.
    Usage of these libraries is to foster the development process and quick querying. 
    Additionally, numpy is used instead of the math package in the get_haversine_distance function. 

    ARGS : [None]
    RETURNS : segments_df[pd.DataFrame], coordinate_df[pd.DataFrame], max_speed[FLOAT]

    '''
    segment_df = pd.read_csv('road-segments.txt', sep=' ',
                             names=['start', 'destination', 'distance', 'speed', 'highway_name'])
    coordinate_df = pd.read_csv(
        'city-gps.txt', sep=' ', names=['city', 'latitude', 'longitude'])
    max_speed = segment_df['speed'].max()
    avg_distance =  0.25 * segment_df['distance'].max() +  0.75 * segment_df['distance'].mean()
    return segment_df, coordinate_df, max_speed, avg_distance


def get_haversine_distance(src_latitude, src_longitude, dest_latitude, dest_longitude):
    '''
    The get_haversine_distance function makes use of the source co-ordinates and 
    destination co-ordinates to get the displacement between the two points
    along the surface/curvarture of the earth. 
    NOTE -> Reference : https://www.movable-type.co.uk/scripts/latlong.html
         -> Referred the JS Code in the mentioned source and implemented an equivalent python function.

    ARGS : src_latitude[FLOAT], src_longitude[FLOAT], dest_latitude[FLOAT], dest_longitude[FLOAT]
    RETURNS : haversine_distance_distance[FLOAT]
    '''
    phi_1 = src_latitude * (np.pi / 180)
    phi_2 = dest_latitude * (np.pi / 180)
    delta_phi = (dest_latitude - src_latitude) * (np.pi / 180)
    delta_lambda = (dest_longitude - src_longitude) * (np.pi / 180)
    a = (np.sin(delta_phi / 2) ** 2) + (np.cos(phi_1) * np.cos(phi_2) * ((np.sin(delta_lambda / 2) ** 2)))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    haversine_distance = ((6371 * c) / 1.60934)
    return haversine_distance


def calculate_cost(cost_function, city, to_distance, avg_distance, to_speed, max_speed, highway_name, latitude, longitude, dest_latitude, dest_longitude, previous_cost, previous_distance, previous_time, previous_delivery_time, steps):
    '''
    The calculate_cost function calculates the cost function of the path to be explored. 
    Essentially this function is the engine of the program. As it drives the exploring head of the 
    path towards the destination with the least 'distance', least 'segments', least 'time', and 
    least 'delivery' time. 

    ARGS            : cost_function[STRING], to_distance[INT], to_speed[INT], max_speed[INT], src_latitude[FLOAT], 
    ARGS(contd.)    : src_longitude[FLOAT], dest_latitude[FLOAT], dest_longitude[FLOAT], previous_distance[INT], 
    ARGS(contd.)    : previous_time[FLOAT], previous_delivery_time[FLOAT], steps[INT]

    RETURNS : cost[FLOAT], total_distance[INT], total_time[FLOAT], total_delivery_time[FLOAT]
    '''
    haversine_distance = get_haversine_distance(latitude, longitude, dest_latitude, dest_longitude,)
    time = to_distance / to_speed

    delivery_time = time
    if to_speed >= 50:
        delivery_time = time + (np.tanh(to_distance / 1000)) * 2 * (time + previous_delivery_time)
        
    total_delivery_time = delivery_time + previous_delivery_time
    total_time = previous_time + time
    total_distance = to_distance + previous_distance

    if cost_function == 'segments':
        #cost = np.log(1 + haversine_distance) + np.log(steps + 1)
        #cost =  np.log((1 + (haversine_distance * steps)) / (haversine_distance + steps))
        #cost = np.log(haversine_distance * steps) / (np.log(haversine_distance) + np.log(steps))
        #cost =  (haversine_distance * steps) / (haversine_distance + steps)
        #cost =  np.log(haversine_distance + (10 ** -15)) *  np.log(steps + (10 ** -15))
        cost = (haversine_distance / avg_distance) + (steps + 1)
        #cost = haversine_distance * steps / (haversine_distance + steps)
        #cost = (np.log(1+ haversine_distance) * np.log(steps + 1)) / (np.log(1+ haversine_distance) + np.log(steps + 1)) # -- works
    elif cost_function == 'distance':
        cost = haversine_distance + total_distance
    elif cost_function == 'time':
        #cost = np.log(1+haversine_distance) + np.log(1 + total_time)
        cost = (haversine_distance / max_speed) + total_time
    elif cost_function == 'delivery':
        #cost = np.log(1 + haversine_distance) + np.log(1 + total_delivery_time)
        cost = (haversine_distance / max_speed)  + total_delivery_time

    return cost, total_distance, total_time, total_delivery_time


def estimate_coordinates(city_name, carried_latitude, carried_longitude, segment_dataset, coordinate_dataset):
    '''
    The estimate_coordinates function estimates the coordinates of the points with no co-ordinates present in the 
    city-gps.txt. A version of triangulation -> (mean of the coordinates of the neighboring points) is used here.
    I implemented the application of weighted mean (based on distance) as well, which is a better estimate,
    but I noticed its damping effect on the overall performance

    ARGS    : city_name[STRING], carried_latitude[FLOAT], carried_longitude[FLOAT], segment_dataset[pd.DataFrame], coordinate_dataset[pd.DataFrame]
    
    RETURNS : [estimated_latitude, estimated_longitude]  [[FLOAT, FLOAT]] 
    '''
    citiesA = set(segment_dataset.loc[(segment_dataset['start'] == city_name)]['destination'])
    citiesB = set(segment_dataset.loc[(segment_dataset['destination'] == city_name)]['start'])
    cities = list(set.union(citiesA, citiesB))
    if city_name in cities:
        cities.remove(city_name)
    coord_latitude, coord_longitude = carried_latitude, carried_longitude
    city_with_coords = 1
    if (carried_latitude == 0) and (coord_longitude == 0):
        city_with_coords = 0
    for city in cities:
        if list(np.array(coordinate_dataset[coordinate_dataset['city'] == city])):
            coords = np.array(coordinate_dataset[coordinate_dataset['city'] == city])[0]
            coord_latitude += coords[1]
            coord_longitude += coords[2]
            #print('Neighbourhood City : ', city, ' located at ', coords)
            city_with_coords += 1
    return [coord_latitude / city_with_coords, coord_longitude / city_with_coords]


def find_paths(cost_function, prev_cost, prev_total_distance, prev_time, prev_delivery_time, city, path, coordinates,  end_city, segment_dataset, coordinate_dataset, max_speed, avg_distance):
    '''
    The find_paths function finds the possible path that can be added to the fringe (priority queue). 
    It calls estimate_coordinates and calculate_cost functions to get the cost values as well 
    updated distance, time, delivery time and segments(path length)

    ARGS         : cost_function[STRING], prev_cost[FLOAT], prev_total_distance[FLOAT], 
    ARGS(contd.) : prev_time[FLOAT], prev_delivery_time[FLOAT], city[STRING], path[LIST], coordinates[LIST],  
    ARGS(contd.) : end_city[STRING], segment_dataset[pd.DataFrame], coordinate_dataset[pd.DataFrame], max_speed[FLOAT]

    RETURNS      : option_cities_master_list[LIST]
    '''
    (latitude, longitude) = coordinates
    next_options = np.array(segment_dataset[segment_dataset['start'] == city]).tolist()
    co_ordinates_start_city = np.array(coordinate_dataset[coordinate_dataset['city'] == city])
    co_ordinates_end_city = np.array(coordinate_dataset[coordinate_dataset['city'] == end_city])
    more_next_options = np.array(segment_dataset[segment_dataset['destination'] == city]).tolist()
    for more_option_city in more_next_options:
        placeholder = more_option_city
        src = more_option_city[1]
        dest = more_option_city[0]
        placeholder[0] = src
        placeholder[1] = dest
        next_options.append(placeholder)

    option_cities_master_list = []
    for option_city in next_options:
        n_path = path.copy()
        next_city = option_city[1]
        to_distance = option_city[2]
        to_speed = option_city[3]
        highway_name = option_city[4]

        if list(np.array(coordinate_dataset[coordinate_dataset['city'] == next_city])):
            co_ordinate = np.array(coordinate_dataset[coordinate_dataset['city'] == next_city])[0]
            newlatitude = co_ordinate[1]
            newlongitude = co_ordinate[2]
        else:
            newlatitude, newlongitude = estimate_coordinates(next_city, latitude, longitude, segment_dataset, coordinate_dataset) #Estimate Coordinates
            # newlatitude, newlongitude = latitude, longitude # Assuming co-ordinate of the last city from the path.    #Take Coordinates of the city it came from

        cost, total_distance, total_time, delivery_time = calculate_cost(cost_function, next_city, to_distance, avg_distance, to_speed, max_speed, highway_name, newlatitude,
                                                                         newlongitude, co_ordinates_end_city[0][1], co_ordinates_end_city[0][2], prev_cost, prev_total_distance, prev_time, prev_delivery_time, len(path)+1)
        n_path.append(next_city)
        option_cities_master_list.append((cost, next_city, n_path, newlatitude, newlongitude, total_distance, total_time, delivery_time))  # append to list : option_cities_master_list

    return option_cities_master_list


def getInformation(path, segment_dataset,):
    '''
    The getInformation function returns the required information for the output.

    ARGS    : path[LIST], segment_dataset[pd.DataFrame]
    RETURNS : distance[FLOAT], time[FLOAT], expected_time[FLOAT], routes[LIST]
    '''

    distance = 0
    time = 0
    expected_time = 0
    routes = []

    for i in range(len(path) - 1):
        dist = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].distance)
        spd = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].speed)
        highway = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].highway_name)
        tme = dist / spd

        routes.append((path[i+1], str(highway[0]) +' for ' + str(dist[0]) + ' miles'))
        if spd >= 50:
            expected_tm = tme + (np.tanh(dist/1000)) * 2 * (tme + time)
        else:
            expected_tm = tme

        distance += dist
        time += tme
        expected_time += expected_tm

    return distance[0], time[0], expected_time[0], routes


def get_optimal_route(start_city, end_city, cost_function):
    '''
    The get_optimal_route is the runner function that manages the core logic and returns the
    output in the required format. The best path is popped from the priority queue (i.e. based on least cost.)

    ARGS    : start_city[STRING], end_city[STRING], cost[FLOAT]
    '''
    segment_dataset, coordinate_dataset, max_speed, avg_distance = read_datasets()
    pQueue = PriorityQueue()
    try:
        latitude, longitude = tuple(np.array(coordinate_dataset[coordinate_dataset['city'] == start_city])[0][1:])
    except Exception as e:
        # Handling the condition where the start_city has no coordinates (i.e. a highway). 
        latitude, longitude = estimate_coordinates(start_city, 0, 0, segment_dataset, coordinate_dataset)
    
    pQueue.put((0, (start_city, [start_city], (latitude, longitude), 0, 0, 0)))
    already_visited = []
    while not pQueue.empty():
        cost, (city, path, (latitude, longitude), total_distance,total_time, total_delivery_time) = pQueue.get()
        if city == end_city:
            t_distance, t_time, t_d_time, routes = getInformation(path, segment_dataset)
            return t_distance, t_time, t_d_time, routes
        already_visited.append(city)
        option_cities_list = find_paths(cost_function, cost, total_distance, total_time, total_delivery_time, city, path, (latitude, longitude), end_city, segment_dataset, coordinate_dataset, max_speed, avg_distance)  # returns list of potential cities with cost, city, path
        for op_city in option_cities_list:
            latitude = op_city[3]
            longitude = op_city[4]
            total_distance = op_city[5]
            total_time = op_city[6]
            total_delivery_time = op_city[7]
            if op_city[1] not in already_visited:
                pQueue.put((op_city[0], (op_city[1], op_city[2], (latitude,longitude), total_distance, total_time, total_delivery_time)))

def get_route(start, end, cost):
    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-delivery-hours": a float indicating the expected (average) time 
                                   it will take a delivery driver who may need to return to get a new package
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """

    total_miles, total_hours, total_delivery_hours, route_taken = get_optimal_route(start, end, cost)
    
    return {"total-segments": len(route_taken),
            "total-miles": float(total_miles),
            "total-hours": float(total_hours),
            "total-delivery-hours": float(total_delivery_hours),
            "route-taken": route_taken}


# Please don't modify anything below this line
#
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])