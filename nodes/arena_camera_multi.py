#!/usr/bin/env python
# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

import yaml
import rospy
import roslaunch


def create_arena_node_multi():
    # Initialze ROS node
    rospy.init_node("ArenaCameraNodeMulti", log_level=rospy.INFO)

    # Load the config file
    try:
        with open(rospy.get_param("~config")) as fp:
            cam_config = yaml.load(fp, Loader=yaml.SafeLoader)
    except FileNotFoundError as e:
        rospy.logerr(e)
        return

    # Get node name prefix for each camera
    name_prefix = rospy.get_param("~name_prefix")
    launch_file = rospy.get_param("~launch_path") + "/arena_camera_node.launch"
    is_debug_active = str(rospy.get_param("~debug"))

    # Create camera nodes
    cam_list = []
    for k, v in cam_config.items():
        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        cam = roslaunch.parent.ROSLaunchParent(uuid, [
            (launch_file, (
                "node_name:=" + name_prefix + "_" + k,
                "cam_name:=" + k,
                "cam_serial:=" + v["serial_no"],
                "cam_config:=" + v["config"],
                "image_resize:=" + v["resize"]["apply"],
                "image_res_x:=" + v["resize"]["res_x"],
                "image_res_y:=" + v["resize"]["res_y"],
                "stream:=" + v["stream"],
                "debug:=" + is_debug_active
            )
        )])
        cam_list.append(cam)

    # Start camera nodes
    for cam in cam_list:
        cam.start()

    # Wait for node to shutdown
    rospy.spin()

    # Finalize camera processes
    for cam in cam_list:
        cam.shutdown()

    # Delete cameras
    cam_list.clear()


if __name__ == "__main__":
    create_arena_node_multi()
