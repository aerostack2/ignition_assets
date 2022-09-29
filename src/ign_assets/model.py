# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import codecs
import os
import subprocess

from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import PackageNotFoundError

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

import ign_assets.bridges
import pathlib
import shutil

import yaml
import json


UAVS = [
    'hexrotor',
    'quadrotor'
]

def camera_models():
    models = ['vga_camera',
              'hd_camera',
              'semantic_camera']
    return models


def rgbd_models():
    models = ['rgbd_camera']
    return models


def lidar_models():
    models = ['planar_lidar',
              '3d_lidar',
              'point_lidar']
    return models


def gps_models():
    models = ['gps']
    return models


def suction_gripper_models():
    models = ['suction_gripper']
    return models


class Model:

    def __init__(self, model_name, model_type, position):
        self.model_name = model_name
        self.model_type = model_type
        self.position = position
        self.battery_capacity = 0
        self.payload = {}

    def __repr__(self) -> str:
        return f"{self.model_name}[{self.model_type}]"

    # def is_UAV(self):
    #     return self.model_type in UAVS

    def bridges(self, world_name):
        bridges = [
            # IMU
            ign_assets.bridges.imu(world_name, self.model_name),
            # Magnetometer
            ign_assets.bridges.magnetometer(world_name, self.model_name),
            # Air Pressure
            ign_assets.bridges.air_pressure(world_name, self.model_name),
            # pose
            ign_assets.bridges.pose(self.model_name),
            # pose static
            ign_assets.bridges.pose_static(self.model_name),
            # twist
            ign_assets.bridges.cmd_vel(self.model_name),
            # arm
            ign_assets.bridges.arm(self.model_name)
        ]

        bridges.extend(self.payload_bridges(world_name))

        return bridges

    def payload_bridges(self, world_name, payloads=None):
        if not payloads:
            payloads = self.payload
        
        bridges = []
        for k in payloads.keys():
            p = payloads[k]
            if not p['sensor'] or p['sensor'] == 'None' or p['sensor'] == '':
                continue

            sensor_name = k
            sensor_type = p['sensor']
            model_prefix = sensor_name

            bridges.extend(
                self.sensor_bridges(
                    world_name, self.model_name, sensor_type, sensor_name, model_prefix))
        return bridges

    @staticmethod
    def sensor_bridges(world_name, model_name, payload, sensor_name, model_prefix=''):
        bridges = []
        if payload in camera_models():
            bridges = [
                ign_assets.bridges.image(world_name, model_name, sensor_name, model_prefix),
                ign_assets.bridges.camera_info(world_name, model_name, sensor_name, model_prefix)
            ]
        elif payload in lidar_models():
            bridges = [
                ign_assets.bridges.lidar_scan(world_name, model_name, sensor_name, model_prefix),
                ign_assets.bridges.lidar_points(world_name, model_name, sensor_name, model_prefix)
            ]
        elif payload in rgbd_models():
            bridges = [
                ign_assets.bridges.image(world_name, model_name, sensor_name, model_prefix),
                ign_assets.bridges.camera_info(world_name, model_name, sensor_name, model_prefix),
                ign_assets.bridges.depth_image(world_name, model_name, sensor_name, model_prefix),
                ign_assets.bridges.camera_points(world_name, model_name, sensor_name, model_prefix)
            ]
        elif payload in gps_models():
            bridges = [
                ign_assets.bridges.navsat(world_name, model_name, sensor_name, model_prefix)
            ]
        elif payload in suction_gripper_models():
            bridges = [
                ign_assets.bridges.gripper_suction_control(model_name),
                ign_assets.bridges.gripper_contact(model_name, 'center'),
                ign_assets.bridges.gripper_contact(model_name, 'left'),
                ign_assets.bridges.gripper_contact(model_name, 'right'),
                ign_assets.bridges.gripper_contact(model_name, 'top'),
                ign_assets.bridges.gripper_contact(model_name, 'bottom')
            ]
        return bridges

    # def set_flight_time(self, flight_time):
    #     # UAV specific, sets flight time

    #     # calculate battery capacity from time
    #     # capacity (Ah) = flight time (in hours) * load (watts) / voltage
    #     # assume constant voltage for battery to keep things simple for now.
    #     self.battery_capacity = (float(flight_time) / 60) * 6.6 / 12.694

    def set_payload(self, payload):
        self.payload = payload

    # def generate(self):
    #     # Generate SDF by executing ERB and populating templates
    #     template_file = os.path.join(
    #         get_package_share_directory('mbzirc_ign'),
    #         'models', self.model_type, 'model.sdf.erb')

    #     model_dir = os.path.join(get_package_share_directory('mbzirc_ign'), 'models')
    #     model_tmp_dir = os.path.join(model_dir, 'tmp')

    #     command = ['erb']
    #     command.append(f'name={self.model_name}')

    #     for (slot, payload) in self.payload.items():
    #         if payload['sensor'] and payload['sensor'] != 'None':
    #             command.append(f"{slot}={payload['sensor']}")
    #         if 'rpy' in payload:
    #             if type(payload['rpy']) is str:
    #                 r, p, y = payload['rpy'].split(' ')
    #             else:
    #                 r, p, y = payload['rpy']
    #             command.append(f'{slot}_pos={r} {p} {y}')

    #     if self.model_type in UAVS:
    #         if self.battery_capacity == 0:
    #             raise RuntimeError('Battery Capacity is zero, was flight_time set?')
    #         command.append(f'capacity={self.battery_capacity}')
    #         if self.has_valid_gripper():
    #             command.append(f'gripper={self.gripper}_{self.model_name}')

    #     if self.model_type in USVS or self.model_type == 'static_arm':
    #         command.append(f'wavefieldSize={self.wavefield_size}')

    #         # run erb for arm to attach the user specified gripper
    #         # and also for arm and gripper to generate unique topic names
    #         if self.has_valid_arm() or self.is_custom_model(self.arm):
    #             command.append(f'arm={self.arm}')
    #             command.append(f'arm_slot={self.arm_slot}')
    #             arm_package = 'mbzirc_ign'
    #             if self.is_custom_model(self.arm):
    #                 arm_package = self.arm
    #             arm_model_file = os.path.join(
    #                 get_package_share_directory(arm_package), 'models',
    #                 self.arm, 'model.sdf.erb')
    #             arm_model_output_file = os.path.join(
    #                 get_package_share_directory(arm_package), 'models',
    #                 self.arm, 'model.sdf')
    #             arm_command = ['erb']

    #             if self.gripper:
    #                 arm_command.append(f'gripper={self.gripper}_{self.model_name}')

    #             # arm payloads
    #             for (slot, payload) in self.arm_payload.items():
    #                 if payload['sensor'] and payload['sensor'] != 'None':
    #                     arm_command.append(f"arm_{slot}={payload['sensor']}")
    #                 if 'rpy' in payload:
    #                     if type(payload['rpy']) is str:
    #                         r, p, y = payload['rpy'].split(' ')
    #                     else:
    #                         r, p, y = payload['rpy']
    #                     arm_command.append(f'arm_{slot}_pos={r} {p} {y}')

    #             arm_command.append(f'topic_prefix={self.model_name}')
    #             arm_command.append(arm_model_file)
    #             process = subprocess.Popen(arm_command, stdout=subprocess.PIPE)
    #             stdout = process.communicate()[0]
    #             str_output = codecs.getdecoder('unicode_escape')(stdout)[0]
    #             with open(arm_model_output_file, 'w') as f:
    #                 f.write(str_output)
    #             # print(arm_command, str_output)

    #     if self.has_valid_gripper():
    #         gripper_model_file = os.path.join(model_dir, self.gripper, 'model.sdf.erb')
    #         gripper_model_output_file = os.path.join(model_tmp_dir,
    #                                                  self.gripper + "_" + self.model_name,
    #                                                  'model.sdf')
    #         gripper_command = ['erb']
    #         topic_prefix = f'{self.model_name}'
    #         if (self.is_USV()):
    #             topic_prefix += '/arm'
    #         gripper_command.append(f'topic_prefix={topic_prefix}')
    #         gripper_command.append(gripper_model_file)

    #         # create unique gripper model in mbzic_ign/models/tmp
    #         # and symlink original model contents to new dir
    #         output_dir = os.path.dirname(gripper_model_output_file)
    #         if not os.path.exists(model_tmp_dir):
    #             pathlib.Path(model_tmp_dir).mkdir(parents=True, exist_ok=True)
    #         if os.path.exists(output_dir):
    #             shutil.rmtree(output_dir)
    #         pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    #         meshes_dir = os.path.join(model_dir, self.gripper, 'meshes')
    #         if os.path.exists(meshes_dir):
    #             os.symlink(meshes_dir, os.path.join(output_dir, 'meshes'))
    #         model_config = os.path.join(model_dir, self.gripper, 'model.config')
    #         os.symlink(model_config, os.path.join(output_dir, 'model.config'))

    #         # Ru erb to generate new model.sdf file
    #         process = subprocess.Popen(gripper_command, stdout=subprocess.PIPE)
    #         stdout = process.communicate()[0]
    #         str_output = codecs.getdecoder('unicode_escape')(stdout)[0]
    #         with open(gripper_model_output_file, 'w') as f:
    #             f.write(str_output)
    #         # print(gripper_command, str_output)

    #     command.append(template_file)
    #     process = subprocess.Popen(command,
    #                                stdout=subprocess.PIPE,
    #                                stderr=subprocess.PIPE)

    #     # evaluate error output to see if there were undefined variables
    #     # for the ERB process
    #     stderr = process.communicate()[1]
    #     err_output = codecs.getdecoder('unicode_escape')(stderr)[0]
    #     for line in err_output.splitlines():
    #         if line.find('undefined local') > 0:
    #             raise RuntimeError(line)

    #     stdout = process.communicate()[0]
    #     model_sdf = codecs.getdecoder('unicode_escape')(stdout)[0]
    #     print(command)

    #     return command, model_sdf

    # def spawn_args(self, model_sdf=None):
        # if not model_sdf:
        #     [command, model_sdf] = self.generate()

        # return ['-string', model_sdf,
        #         '-name', self.model_name,
        #         '-allow_renaming', 'false',
        #         '-x', str(self.position[0]),
        #         '-y', str(self.position[1]),
        #         '-z', str(self.position[2]),
        #         '-R', str(self.position[3]),
        #         '-P', str(self.position[4]),
        #         '-Y', str(self.position[5])]

    @classmethod
    def FromConfig(cls, stream):
        # Generate a Model instance (or multiple instances) from a stream
        # Stream can be either a file input or string
        file_extension = stream.name.split('.')[-1]
        if file_extension in ['yaml', 'yml']:
            config = yaml.safe_load(stream)

            if type(config) == list:
                return cls._FromConfigList(config)
            elif type(config) == dict:
                return cls._FromConfigDict(config)
        elif file_extension in ['json']:
            config = json.load(stream)
            return cls._FromConfigListJson(config)

    @classmethod
    def _FromConfigList(cls, entries):
        # Parse an array of configurations
        ret = []
        for entry in entries:
            ret.append(cls._FromConfigDict(entry))
        return ret

    @classmethod
    def _FromConfigListJson(cls, config):
        ret = []
        for entry in config['drones']:
            ret.append(cls._FromConfigDictJson(entry))
        return ret

    @classmethod
    def _FromConfigDict(cls, config):
        # Parse a single configuration
        if 'model_name' not in config:
            raise RuntimeError('Cannot construct model without model_name in config')
        if 'model_type' not in config:
            raise RuntimeError('Cannot construct model without model_type in config')

        xyz = [0, 0, 0]
        rpy = [0, 0, 0]
        if 'position' not in config:
            print('Position not found in config, defaulting to (0, 0, 0), (0, 0, 0)')
        else:
            if 'xyz' in config['position']:
                xyz = config['position']['xyz']
            if 'rpy' in config['position']:
                rpy = config['position']['rpy']
        model = cls(config['model_name'], config['model_type'], [*xyz, *rpy])

        if 'flight_time' in config:
            model.set_flight_time(config['flight_time'])

        if 'payload' in config:
            model.set_payload(config['payload'])

        if 'gripper' in config:
            model.set_gripper(config['gripper'])

        return model

    @classmethod
    def _FromConfigDictJson(cls, config):
        if 'model' not in config:
            raise RuntimeError('Cannot construct model without model in config')
        if 'name' not in config:
            raise RuntimeError('Cannot construct model without name in config')

        xyz = [0, 0, 0]
        rpy = [0, 0, 0]
        if 'xyz' in config:
            xyz = config['xyz']
        if 'rpy' in config:
            rpy = config['rpy']
        model = cls(config['name'], config['model'], [*xyz, *rpy])

        if 'flight_time' in config:
            model.set_flight_time(config['flight_time'])

        if 'payload' in config:
            model.set_payload(config['payload'])

        return model