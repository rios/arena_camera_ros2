# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

import time
import json
import rospy
from arena_api.system import system


def check_and_set(cam, key, value):
    """ Setter implementation for Arena API.

    :param cam: camera pointer
    :param key: node name in the camera nodemap dictionary
    :returns: value of the node
    """
    # Get the camera node and its type
    inode_type = cam.nodemap[key].interface_type.value

    # Node interface type
    if inode_type == 2:
        # Integer node
        cam.nodemap[key].value = int(value)
    elif inode_type == 3:
        # Boolean node
        cam.nodemap[key].value = bool(value)
    elif inode_type == 5:
        # Float node
        cam.nodemap[key].value = float(value)
    elif inode_type == 6:
        # String node
        cam.nodemap[key].value = str(value)
    elif inode_type == 9:
        # Enumeration node
        cam.nodemap[key].value = str(value)
    else:
        pass


def check_and_get(cam, key):
    """ Getter implementation for Arena API.

    :param cam: camera pointer
    :param key: node name in the camera nodemap dictionary
    :returns: value of the node
    """
    # Get the camera node and its type
    inode_type = cam.nodemap[key].interface_type.value

    # Node interface type
    if inode_type == 2:
        # Integer node
        return int(cam.nodemap[key].value)
    elif inode_type == 3:
        # Boolean node
        return bool(cam.nodemap[key].value)
    elif inode_type == 5:
        # Float node
        return float(cam.nodemap[key].value)
    elif inode_type == 6:
        # String node
        return str(cam.nodemap[key].value)
    elif inode_type == 9:
        # Enumeration node
        return str(cam.nodemap[key].value)
    else:
        pass


def validate_goal(goal):
    """ Validates the goal received by an action server

    :param goal: goal received from an action client
    """
    num_images = max(len(goal.exposure_times), len(goal.gain_values), len(goal.brightness_values), len(goal.gamma_values))
    if goal.exposure_given and len(goal.exposure_times) != num_images:
        rospy.logerr("exposure_times size mismatch")
        return False, 0
    if goal.gain_given and len(goal.gain_values) != num_images:
        rospy.logerr("gain_values size mismatch")
        return False, 0
    if goal.brightness_given and len(goal.brightness_values) != num_images:
        rospy.logerr("brightness_values size mismatch")
        return False, 0
    if goal.gamma_given and len(goal.gamma_values) != num_images:
        rospy.logerr("gamma_values size mismatch")
        return False, 0
    if goal.brightness_given and not (goal.exposure_auto or goal.gain_auto):
        rospy.logerr("exposure_auto and gain_auto should be True when brightness_given is True")
        return False, 0
    return True, num_images


def list_cameras():
    """ A utility function to get information about the detected cameras.

    :returns: a list of dicts containing camera information
    """
    # Initialize return list
    ret = []

    # Get cameras
    cam_infos = system.device_infos

    # Check if there are any cameras found
    if cam_infos:
        # Initialize cameras
        for ci in cam_infos:
            # Initialize variables
            cam_info = {
                "serial": ci["serial"],
                "userid": ci["name"]
            }

            # Add cam information to the return list
            ret.append(cam_info)

    return ret


def cycle_cameras():
    """ A utility function to run a complete image acquisition cycle on the detected cameras.

    This function is helpful to fix camera allocation and dangling pointer errors which may be
    encountered while using Spinnaker Python API.

    :returns: True if cameras are detected. False, otherwise.
    """
    num_buffers = 1
    timeout = 200  # milliseconds

    # Init devices
    cams = system.create_device()

    for cam in cams:
        # Print device serial number
        print("Device serial number:", cam.nodemap["DeviceSerialNumber"].value)

        # Enable trigger mode
        cam.nodemap["TriggerMode"].value = "On"

        # Select trigger mode
        cam.nodemap["TriggerSelector"].value = "FrameStart"

        # Set trigger source to Software
        cam.nodemap["TriggerSource"].value = "Software"

        # Start stream
        with cam.start_stream(num_buffers):
            for _ in range(num_buffers):
                # Wait for trigger to get armed
                while not cam.nodemap["TriggerArmed"].value:
                    continue

                system_time = time.time()
                print("System Time:", system_time)

                # Trigger!
                cam.nodemap["TriggerSoftware"].execute()

                # Wait for the next image
                if num_buffers > 1:
                    cam.wait_for_next_leader(timeout)

            # Get buffer
            buff = cam.get_buffer()

            image_time = buff.timestamp_ns / 1e9
            print("Image Time:", image_time)
            diff_time = (image_time - system_time)
            print("Diff Time:", diff_time, "\n")

            # Requeue the image buffer
            cam.requeue_buffer(buff)

    # Disable trigger mode
    cam.nodemap["TriggerMode"].value = "Off"

    return True


def import_config(cam, cfg_file):
    """ Imports camera configuration from a JSON configuration file.

    :param cam: camera pointer
    :param cfg_file: configuration file name
    """
    # Load configuration from the json file
    with open(cfg_file, "r") as fp:
        cfg_json = json.load(fp)

    # Import configuration
    for k, v in cfg_json.items():
        check_and_set(cam, k, v)
