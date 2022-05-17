#!/usr/bin/python3

import json
import argparse

def get_drone(drone):
    model = drone['model']
    x, y, z, yaw = drone['pose']

    sensors = ""
    for sensor_name, sensor in drone['sensors'].items():
        roll, pitch, yaw = sensor['rotation']
        sensors += f":{sensor_name}:{sensor['sensor']}:{roll}:{pitch}:{yaw}"

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
    except KeyError:
        world = "none"

    print(world)

    for drone in data['drones']:
        try:
            drone_ = get_drone(drone)
            print(drone_)
        except KeyError:
            break
