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
${AEROSTACK2_STACK}/simulation/ignition/scripts/run_ign.sh 
```

or using a config file (see [config files](#config-file)) :

```bash
${AEROSTACK2_STACK}/simulation/ignition/scripts/run_ign.sh <config-file>
```

This will run for you **ign gazebo server**, spawn an **quadrotor_base model** and open **ign gazebo client** (GUI).

## OPTIONS
Inital configuration aspects as world, drone model, drone pose or adding several drones can be done setting **environment variables** or using a **config file**.

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
Using a config file lets you to set the simulation environment. You can select a world (or none) and attach to it a number of desired drones with desired model and position. Please pay atention to teh format file, otherwise it may fail.

Example of a config file:
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
                "rotation": [ 0.0, 0.0, 0.0 ]
            },
            "lidar_0": {
                "sensor": "3d_lidar",
                "rotation": [ 0.0, 0.0, 0.0 ]
            }
        }
    },
    {
        "model": "quadrotor_base",
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
