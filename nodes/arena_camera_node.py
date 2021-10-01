#!/usr/bin/env python
# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

import rospy
from arena_camera_ros.ArenaCamera import ArenaCamera


def create_arena_node():
    # Initialze ROS node
    rospy.init_node("ArenaCameraNode", log_level=rospy.INFO, anonymous=True)

    # Create camera
    cam = ArenaCamera(
        cam_serial=rospy.get_param("~cam_serial"),
        cam_name=rospy.get_param("~cam_name"),
        config=rospy.get_param("~cam_config"),
        resize=rospy.get_param("~image_resize"),
        resize_res=(rospy.get_param("~image_res_x"), rospy.get_param("~image_res_y"))
    )

    # Init camera
    cam.init()

    # Start camera and wait for shutdown
    cam.start()

if __name__ == "__main__":
    create_arena_node()
