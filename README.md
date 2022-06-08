# ignition_assets

Colletion of AS2 Ignition Gazebo assets and scripts. 

Tested on **Ignition Gazebo Fortress**. Make sure to have it [installed](https://gazebosim.org/docs/fortress/install_ubuntu).

## INDEX
- [HOW TO RUN](#how-to-run-basic-usage)
- [OPTIONS](#options)
    - [ENV VARS](#env-vars)
    - [CONFIG FILE](#config-file)
- [MORE OPTIONS](#more-options)
- [EXAMPLES](#examples)
- [ADVANCED USAGE](#advanced-usage)
---

## HOW TO RUN: Basic usage

Previously setting AS2 environment, simply run:
```bash
${AEROSTACK2_PATH}/simulation/ignition/scripts/run_ign.sh 
```

or using a config file (see [config files](#config-file)) :

```bash
${AEROSTACK2_PATH/simulation/ignition/scripts/run_ign.sh <config-file>
```

This will run for you **ign gazebo server**, spawn an **quadrotor_base model** and open **ign gazebo client** (GUI).

## OPTIONS
Inital configuration aspects as world, drone model, drone pose or adding several drones can be done setting **environment variables** or using a **config file**.

- Run on start:
    ```bash
    export RUN_ON_START=1
    ```

- Verbose mode:
    ```bash
    export VERBOSE_SIM=1
    ```

### ENV VARS
Previously set needed environment variables before launching the script.

- World
    ```bash
    export UAV_WORLD=<path-to-world>
    ```
- Drone model
    ```bash
    export UAV_MODEL=<model-name>
    ```
- Drone pose
    ```bash
    export UAV_X=<float>  # meters
    export UAV_Y=<float>  # meters
    export UAV_Z=<float>  # meters
    export UAV_YAW=<float>  # radians
    ```

Using environment variables is though when using only one drone.

### CONFIG FILE
Using a config file lets you to set the simulation environment. You can select a world (or none) and attach to it a number of desired drones with desired model, position and set of sensors. Please pay atention to the format file, otherwise it may fail.

Config file template:
```
{
    "world": "<world-name>",                // optional: deafult world if empty
    "drones": [                             // optional: no drones if empty
    {
        "model": "<model-name>",            // optional: default model if empty
        "pose": [<x>, <y>, <z>, <yaw>],     // optional: [0, 0, 0, 0] if empty
        "sensors": {                        // optional: no sensors if none
            "<sensor-name>": {              // REQUIRED if sensor is used
                "sensor": "<sensor-type>",  // REQUIRED if sensor is used
                "position": [<x>, <y>, <z>], // optional: [0, 0, 0] if empty
                "rotation": [<yaw>, <pitch>, <roll>], // optional: [0, 0, 0] if empty
            },
            "<sensor-name-2>": {
                // Second sensor...
            }
        }
    },
    {
        // Second drone...
    }
    ]
}
```
Notice that comments are not available in JSON format and fields between "<" and ">" should be replaced with each value or removed (along with the field) if is not wanted or required.

Example of a valid config file:
```json
{
    "world": "empty",
    "drones": [
    {
        "model": "quadrotor_base",
        "pose": [ 0.0, 0.0, 0.2, 1.57 ],
        "sensors": {
            "front_camera": {
                "sensor": "hd_camera",
                "rotation": [ 0.0, 0.0, 1.57 ]
            },
            "lidar_0": {
                "sensor": "3d_lidar",
                "position": [ 0.0, 0.0, -0.5 ]
            }
        }
    },
    {
        "model": "hexrotor_base",
        "pose": [ 3.0, 0.0, 0.2, 1.57 ]
    }
    ]
}
```

## MORE OPTIONS
- Use custom models in world/drone:
    ```bash
    export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:<custom-model-path>
    ```
- Run simulation on start:
    ```bash
    export RUN_ON_START=1
    ```

## EXAMPLES
Several examples can be found on [test](/tests) folder.
