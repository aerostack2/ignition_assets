#!/usr/bin/python3

import json
import argparse

def get_drone(drone):
    try:
        model = drone['model']
    except KeyError as ex:
        if ex.args[0] != 'model':
            raise KeyError
        model = 'none'

    try:
        x, y, z, yaw = drone['pose']
    except KeyError as ex:
        if ex.args[0] != 'pose':
            raise KeyError
        x, y, z, yaw = 0, 0, 0, 0

    sensors = ""
    try:
        for sensor_name, sensor in drone['sensors'].items():
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
        if (ex.args[0] != 'sensors'):
            raise KeyError
        
    return f"{model}:{x}:{y}:{z}:{yaw}{sensors}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tool to parse simluation configuration file'
    )

    parser.add_argument('filepath', type=str, help='Filepath to config file')
    args = parser.parse_args()
    
    try:
        json_data = open(args.filepath)
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

    print(world)

    try:
        drones = data['drones']
    except KeyError as ex:
        if ex.args[0] != 'drones':
            raise KeyError
        print("none:0:0:0:0")
        exit(0)

    for drone in drones:
        drone_ = get_drone(drone)
        print(drone_)

