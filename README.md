# arena_camera_ros2

Python ROS (Noetic/ROS1) driver for [LUCID Vision Labs](https://thinklucid.com/) GigE and USB3 cameras using the [Arena SDK](https://thinklucid.com/downloads-hub/).

> **Note:** Despite the repository name, this package targets **ROS Noetic (ROS1)** with the catkin build system,
> not ROS2. The `ros2` in the name reflects its lineage as a successor to an earlier driver.

## License

Apache-2.0. See [LICENSE](LICENSE).

## Requirements

- ROS Noetic (Ubuntu 20.04)
- Python 3 (`apt install python-is-python3`)
- [LUCID Arena SDK](https://thinklucid.com/downloads-hub/) (v0.1.54 or compatible)
- LUCID Arena Python API (`arena_api`) — install from PyPI or LUCID's distribution
- [`camera_control_msgs`](https://github.com/rios/camera_control_msgs) ROS package

## Installation

### 1. Install Arena SDK

Download and install the Arena SDK from the [LUCID downloads hub](https://thinklucid.com/downloads-hub/).
After installation, ensure the shared libraries are on `LD_LIBRARY_PATH`:

```bash
echo "/opt/ArenaSDK/lib64" | sudo tee /etc/ld.so.conf.d/Arena_SDK.conf
echo "/opt/ArenaSDK/GenICam/library/lib/Linux64_x64" >> /etc/ld.so.conf.d/Arena_SDK.conf
echo "/opt/ArenaSDK/ffmpeg" >> /etc/ld.so.conf.d/Arena_SDK.conf
sudo ldconfig
```

### 2. Install Arena Python API

```bash
pip3 install arena_api
```

### 3. Verify installation

```bash
python3 -c "from arena_api.system import system; print(system.device_infos)"
```

### 4. Build the ROS package

Clone this repository into your catkin workspace and build:

```bash
cd ~/catkin_ws/src
git clone https://github.com/rios/arena_camera_ros2.git arena_camera_ros
cd ~/catkin_ws
catkin build
source devel/setup.bash
```

## Usage

### List connected cameras

```bash
rosrun arena_camera_ros arena_camera_list_serials.py
```

### Launch a single camera node

```bash
roslaunch arena_camera_ros arena_camera_node.launch cam_serial:=<serial_number>
```

### Launch with custom resolution

```bash
roslaunch arena_camera_ros arena_camera_node.launch \
    cam_serial:=<serial_number> \
    image_resize:=true \
    image_res_x:=640 \
    image_res_y:=480
```

### Launch multiple camera nodes

Provide a YAML configuration file (see `config/namespace.yaml` for an example):

```bash
roslaunch arena_camera_ros arena_camera_multi.launch config:=<path/to/config.yaml>
```

## ROS Topics and Services

Each camera node publishes on a namespace derived from `node_name` and `cam_name`
(default: `/arena_camera_node/camera`):

| Topic / Service | Type | Description |
|---|---|---|
| `.../image_raw` | `sensor_msgs/Image` | Raw camera image |
| `.../image_color` | `sensor_msgs/Image` | Resized image (if resize enabled) |
| `.../camera_info` | `sensor_msgs/CameraInfo` | Camera metadata |
| `.../get_cam_properties` | `camera_control_msgs/GetCamProperties` | Read camera settings |
| `.../set_exposure` | `camera_control_msgs/SetExposure` | Set exposure time |
| `.../set_gain` | `camera_control_msgs/SetGain` | Set gain |
| `.../set_gamma` | `camera_control_msgs/SetGamma` | Set gamma |
| `.../grab_images` (action) | `camera_control_msgs/GrabImages` | Triggered image capture |

## Helper Scripts

- `arena_camera_list_serials.py` — Lists serial numbers of discovered cameras
- `arena_camera_cycle.py` — Runs a complete acquisition cycle; useful for fixing pointer errors

## Camera Configuration

Camera parameters can be loaded from a JSON file at startup. See `config/no_config.json`
for the file format. Pass the path via the `cam_config` launch argument.

## Known Limitations

- `camera_control_msgs` is a companion ROS package required at build and runtime.
  See that package's repository for installation instructions.
- The CI workflow (`docker/Earthfile`) references internal infrastructure and will not
  work outside the original build environment. It is retained for reference only.
- This package targets ROS Noetic (ROS1) only. A native ROS2 port does not exist in
  this repository.
