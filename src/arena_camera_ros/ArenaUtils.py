# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

import rospy
from arena_api.system import system


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
    system = PySpin.System.GetInstance()
    cams = system.GetCameras()

    # Check if there are any cameras found
    if cams.GetSize() > 0:
        # Initialize cameras
        for i, cam in enumerate(cams):
            # Initialize camera
            cam.Init()

            # Retrieve TL device nodemap
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Initialize variables
            serial_number = -1
            user_id = ""
            cam_info = {}

            # Get the serial number of the camera
            node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                cam_info["serial"] = node_device_serial_number.GetValue()

            node_device_user_id = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceUserID'))
            if PySpin.IsAvailable(node_device_user_id) and PySpin.IsReadable(node_device_user_id):
                cam_info["userid"] = node_device_user_id.GetValue()

            # Add cam information to the return list
            ret.append(cam_info)

            # Deinitialize camera
            cam.DeInit()

        # Delete camera pointer
        del cam

    # Delete cameras
    cams.Clear()
    system.ReleaseInstance()

    return ret


def cycle_cameras():
    """ A utility function to run a complete image acquisition cycle on the detected cameras.

    This function is helpful to fix camera allocation and dangling pointer errors which may be
    encountered while using Spinnaker Python API.

    :returns: True if cameras are detected. False, otherwise.
    """
    # Get cameras
    system = PySpin.System.GetInstance()
    cams = system.GetCameras()

    # Check if there are any cameras found
    if cams.GetSize() == 0:
        return False
    else:
        # Initialize cameras
        for i, cam in enumerate(cams):
            # Initialize camera
            cam.Init()

            # Begin image acquisition
            cam.BeginAcquisition()

            # End image acquisition
            cam.EndAcquisition()

            # Deinitialize camera
            cam.DeInit()

        # Delete camera pointer
        del cam

    # Delete cameras
    cams.Clear()
    system.ReleaseInstance()

    return True
