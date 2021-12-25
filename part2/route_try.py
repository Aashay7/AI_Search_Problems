#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: name IU ID
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
    return segment_df, coordinate_df, max_speed


def get_haversine_distance(src_latitude, src_longitude, dest_latitude, dest_longitude):
    '''
    The get_haversine_distance function makes use of the source co-ordinates and 
    destination co-ordinates to get the displacement between the two points
    along the surface/curvarture of the earth. 
    Reference : https://www.movable-type.co.uk/scripts/latlong.html
    Referred the JS Code and coded an equivalent python function.

    ARGS : src_latitude[FLOAT], src_longitude[FLOAT], dest_latitude[FLOAT], dest_longitude[FLOAT]
    RETURNS : haversine_distance_distance[FLOAT]
    '''
    radius = 6371
    phi_1 = src_latitude * (np.pi / 180)
    phi_2 = dest_latitude * (np.pi / 180)
    delta_phi = (dest_latitude - src_latitude) * (np.pi / 180)
    delta_lambda = (dest_longitude - src_longitude) * (np.pi / 180)
    a = (np.sin(delta_phi / 2) ** 2) + (np.cos(phi_1) *
                                        np.cos(phi_2) * ((np.sin(delta_lambda / 2) ** 2)))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    haversine_distance = ((radius * c) / 1.60934)
    return haversine_distance


def calculate_cost(cost_function, city, to_distance, to_speed, max_speed, highway_name, latitude, longitude, dest_latitude, dest_longitude, previous_cost, previous_distance, previous_time, previous_delivery_time, steps):
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
    eucl_dist = get_haversine_distance(
        latitude, longitude, dest_latitude, dest_longitude,)
    time = to_distance / to_speed

    delivery_time = 0
    if to_speed >= 50:
        delivery_time = time + (np.tanh(to_distance / 1000)) * \
            2 * (time + previous_delivery_time)
    else:
        delivery_time = time

    total_delivery_time = delivery_time + previous_delivery_time
    total_time = previous_time + time
    total_distance = to_distance + previous_distance

    if cost_function == 'segments':
        cost = np.log(1 + eucl_dist) + np.log(steps + 1)
        #cost =  np.log((1 + (eucl_dist * steps)) / (eucl_dist + steps))
        #cost = np.log(eucl_dist * steps) / (np.log(eucl_dist) + np.log(steps))
        #cost =  (eucl_dist * steps) / (eucl_dist + steps)
        cost = eucl_dist * steps / (eucl_dist + steps)
        # cost = (np.log(1+ eucl_dist) * np.log(steps + 1)) / (np.log(1+ eucl_dist) + np.log(steps + 1)) # -- works
    elif cost_function == 'distance':
        cost = eucl_dist + total_distance
    elif cost_function == 'time':
        #cost = np.log(1+eucl_dist) + np.log(1 + total_time)
        cost = (eucl_dist / max_speed) + total_time
    elif cost_function == 'delivery':
        cost = np.log(1 + eucl_dist) + np.log(1 + total_delivery_time)
        #cost =(eucl_dist / max_speed)  + total_delivery_time

    return cost, total_distance, total_time, total_delivery_time


def estimate_coordinates(city_name, carried_latitude, carried_longitude, segment_dataset, coordinate_dataset):
    print('Next City : ', city_name, '\tCarried Coords : ',
          (carried_latitude, carried_longitude))
    #print(segment_dataset.loc[(segment_dataset['start'] == city_name)]['destination'])
    #print(segment_dataset.loc[(segment_dataset['destination'] == city_name)]['start'])

    citiesA = set(segment_dataset.loc[(
        segment_dataset['start'] == city_name)]['destination'])
    citiesB = set(segment_dataset.loc[(
        segment_dataset['destination'] == city_name)]['start'])
    cities = list(set.union(citiesA, citiesB))
    if city_name in cities:
        cities.remove(city_name)
    #print('Cities A :', citiesA,'\nCities B : ', citiesB)
    #print('Neighbourhood of ', city_name, ' is : ', cities)
    coord_latitude = carried_latitude
    coord_longitude = carried_longitude
    city_with_coords = 1
    for city in cities:
        if list(np.array(coordinate_dataset[coordinate_dataset['city'] == city])):
            coords = np.array(
                coordinate_dataset[coordinate_dataset['city'] == city])[0]
            coord_latitude += coords[1]
            coord_longitude += coords[2]
            #print('Neighbourhood City : ', city, ' located at ', coords)
            city_with_coords += 1
    return [coord_latitude / city_with_coords, coord_longitude / city_with_coords]


def find_paths(cost_function, prev_cost, prev_total_distance, prev_time, prev_delivery_time, city, path, coordinates,  end_city, segment_dataset, coordinate_dataset, max_speed):
    print('FIND PATHS : Current City : ', city,
          ' with coordinates : ', coordinates)
    (latitude, longitude) = coordinates
    next_options = np.array(
        segment_dataset[segment_dataset['start'] == city]).tolist()
    co_ordinates_start_city = np.array(
        coordinate_dataset[coordinate_dataset['city'] == city])
    co_ordinates_end_city = np.array(
        coordinate_dataset[coordinate_dataset['city'] == end_city])
    more_next_options = np.array(
        segment_dataset[segment_dataset['destination'] == city]).tolist()
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
            co_ordinate = np.array(
                coordinate_dataset[coordinate_dataset['city'] == next_city])[0]
            newlatitude = co_ordinate[1]
            newlongitude = co_ordinate[2]
        else:
            newlatitude, newlongitude = estimate_coordinates(
                next_city, latitude, longitude, segment_dataset, coordinate_dataset)
            # newlatitude, newlongitude = latitude, longitude # Assuming co-ordinate of the last city from the path.

        cost, total_distance, total_time, delivery_time = calculate_cost(cost_function, next_city, to_distance, to_speed, max_speed, highway_name, newlatitude,
                                                                         newlongitude, co_ordinates_end_city[0][1], co_ordinates_end_city[0][2], prev_cost, prev_total_distance, prev_time, prev_delivery_time, len(path)+1)
        n_path.append(next_city)

        option_cities_master_list.append((cost, next_city, n_path, newlatitude, newlongitude,
                                         total_distance, total_time, delivery_time))  # append to list : option_cities_master_list

    return option_cities_master_list


def getInformation(path, segment_dataset, coordinate_dataset):
    distance = 0
    time = 0
    expected_time = 0
    highway_list = []
    routes = []

    for i in range(len(path) - 1):
        #print(segment_dataset.loc[ (segment_dataset['start'] == list_p[i]) and (segment_dataset['destination'] == list_p[i+1])])
        #print(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])])
        dst = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].distance)
        spd = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].speed)
        highway = np.array(segment_dataset.loc[(segment_dataset['start'] == path[i]) & (segment_dataset['destination'] == path[i+1]) | (
            segment_dataset['destination'] == path[i]) & (segment_dataset['start'] == path[i+1])].highway_name)
        tme = dst / spd

        routes.append((path[i+1], str(highway[0]) +
                      ' for ' + str(dst[0]) + ' miles'))
        if spd >= 50:
            expected_tm = tme + (np.tanh(dst/1000)) * 2 * (tme + time)
        else:
            expected_tm = tme
        distance += dst

        time += tme
        expected_time += expected_tm
        #print('Distance : ', dst, '\nSpeed : ', spd ,'Actual Time : ', tme ,'\nExpected Time : ', expected_tm)

    #print('total-segments : ', len(path) - 1 ,'TOTAL Distance : ', distance, '\nTime : ', time, '\nExpected Time : ', expected_time)
    return distance[0], time[0], expected_time[0], routes


def compute_path(start, end, cost):
    segment_dataset, coordinate_dataset, max_speed = read_datasets()
    pQueue = PriorityQueue()
    latitude, longitude = tuple(
        np.array(coordinate_dataset[coordinate_dataset['city'] == start_city])[0][1:])
    print('Start Coords : ', latitude, ' \t', longitude)
    # cost, (start_city, path, (latitude, longitude) total_distance, total_time)
    pQueue.put((0, (start_city, [start_city], (latitude, longitude), 0, 0, 0)))
    print(pQueue.queue, )
    cnt = 0
    already_visited = []
    while not pQueue.empty():
        cost, (city, path, (latitude, longitude), total_distance,
               total_time, total_delivery_time) = pQueue.get()
        if city == end_city:
            print(path)
            # Return Vital Information
            t_distance, t_time, t_d_time, routes = getInformation(
                path, segment_dataset, coordinate_dataset)
            return path, t_distance, t_time, t_d_time, routes
        already_visited.append(city)
        print('\n', city, ' popped from Pqueue \tCoord : ',
              (latitude, longitude), '\tPath : ', path)
        option_cities_list = find_paths(cost_function, cost, total_distance, total_time, total_delivery_time, city, path, (
            latitude, longitude), end_city, segment_dataset, coordinate_dataset, max_speed)  # returns list of potential cities with cost, city, path
        for op_city in option_cities_list:

            latitude = op_city[3]
            longitude = op_city[4]
            total_distance = op_city[5]
            total_time = op_city[6]
            total_delivery_time = op_city[7]
            if op_city[1] not in already_visited:
                pQueue.put((op_city[0], (op_city[1], op_city[2], (latitude,
                           longitude), total_distance, total_time, total_delivery_time)))
            else:
                #print('\n',op_city, ' already visited. Not adding to the pQueue.')
                pass


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

    # Create a priority Queue that maintains the city, last_step_cost, path_cost, path_cities.
    path, total_miles, total_hours, total_delivery_hours, route_taken = compute_path(
        start, end, cost)

    return {"total-segments": len(route_taken),
            "total-miles": total_miles,
            "total-hours": total_hours,
            "total-delivery-hours": total_delivery_hours,
            "route-taken": route_taken}


# Please don't modify anything below this line
#
if __name__ == "__main__":

    start_city = 'Bloomington,_Indiana'
    #start_city = 'Houston,_Texas'
    #start_city = 'Nashville,_Tennessee'
    #end_city = 'Indianapolis,_Indiana'
    end_city = 'Chicago,_Illinois'
    cost_function = 'delivery'
    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])
