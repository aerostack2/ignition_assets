#!/usr/bin/python3

import json
import argparse


def get_battery_capacity(flight_time):
    # UAV specific, sets flight time

    # calculate battery capacity from time
    # capacity (Ah) = flight time (in hours) * load (watts) / voltage
    # assume constant voltage for battery to keep things simple for now.
    battery_capacity = (float(flight_time) / 60) * 6.6 / 12.694
    return battery_capacity


def get_drone(drone):
    try:
        model = drone['model']
    except KeyError as ex:
        if ex.args[0] != 'model':
            raise KeyError
        model = 'none'

    try:
        name = drone['name']
    except KeyError as ex:
        if ex.args[0] != 'name':
            raise KeyError
        name = 'none'    

    try:
        x, y, z, yaw = drone['pose']
    except KeyError as ex:
        if ex.args[0] != 'pose':
            raise KeyError
        x, y, z, yaw = 0, 0, 0, 0

    capacity = 0
    if "flight_time" in drone:
        flight_time = drone['flight_time']
        capacity = get_battery_capacity(flight_time)

    sensors = ""
    try:
        for sensor_name, sensor in drone['payload'].items():
            try:
                sensor_type = sensor['sensor']
            except KeyError as ex:
                if ex.args[0] != 'sensor':
                    raise KeyError
                continue

            try:
                x_s, y_s, z_s = sensor['position']
            except KeyError as ex:
                if ex.args[0] != 'position':
                    raise KeyError
                x_s, y_s, z_s = 0, 0, 0

            try:
                roll_s, pitch_s, yaw_s = sensor['rotation']
            except KeyError as ex:
                if ex.args[0] != 'rotation':
                    raise KeyError
                roll_s, pitch_s, yaw_s = 0, 0, 0

            sensors += f":{sensor_name}:{sensor_type}:{x_s}:{y_s}:{z_s}:{roll_s}:{pitch_s}:{yaw_s}"
    except KeyError as ex:
        if (ex.args[0] != 'payload'):
            raise KeyError
        
    return f"{model}:{name}:{x}:{y}:{z}:{yaw}:{capacity}{sensors}"

def main(filepath):
    try:
        json_data = open(filepath)
        data = json.load(json_data)
        json_data.close()
    except FileNotFoundError:
        print("File not found.")
        exit(-1)

    try:
        world = data['world']
    except KeyError as ex:
        if ex.args[0] != 'world':
            raise KeyError
        world = "none"

    try:
        drones = data['drones']
    except KeyError as ex:
        if ex.args[0] != 'drones':
            raise KeyError
        return world, "none:none:0:0:0:0"

    drone_ = []
    for drone in drones:
        drone_ += [get_drone(drone)]
    
    return world, drone_

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to parse simluation configuration file'
    )

    parser.add_argument('filepath', type=str, help='Filepath to config file')
    args = parser.parse_args()

    world, drones = main(args.filepath)
    print(world)
    for drone in drones:
        print(drone)
