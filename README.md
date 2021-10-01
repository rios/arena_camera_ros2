# arena_camera_ros
http://github.com/rios-ai/arena_camera_ros

## Maintainers:
- Onur Bingol (onur.bingol@rios.ai)

ROS drivers for LUCID GigE and USB3 cameras.

## Requirements ##
 - ROS Noetic
 - Python 3 (`apt install python-is-python3`)
 - LUCID Arena SDK
 - LUCID Arena Python API

##  Build Instructions ##

Before building the package, please make sure that Arena SDK and Python API are installed.

### Checking Spinnaker installation

Arena Python API provides a module `arena_api` and you should be able to import it:

```bash
$ python3
Python 3.8.10 (default, Jun  2 2021, 10:49:15)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from arena_api.system import system
>>> system.device_infos
```

### Building ROS package

```bash
$ catkin build
```

## Usage Instructions

### Launching single camera node

```bash
$ roslaunch arena_camera_ros arena_camera_node.launch
```

### Launching single camera node with custom resolution

Example resolution: `640x480`

```bash
$ roslaunch arena_camera_ros arena_camera_node.launch image_resize:=true image_res_x:=640 image_res_y:=480
```

### Launching multi camera node

A configuration file is needed to launch multiple camera nodes. Please refer to `config/namepace.yaml` for an example configuration file.

```bash
$ roslaunch arena_camera_ros arena_camera_multi.launch config:={YAML config file}
```

## Helper Scripts

* `arena_camera_list_serials.py`: Lists serial numbers of the discovered cameras
* `arena_camera_cycle.py`: Runs a complete image acquisition cycle on the discovered cameras. Good for fixing pointer errors.
