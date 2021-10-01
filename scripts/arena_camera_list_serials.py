#!/usr/bin/env python
# arena_camera_list_serials.py -- Lists camera serials
# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

from arena_camera_ros.ArenaUtils import list_cameras


if __name__ == "__main__":
    cams = list_cameras()
    for i, c in enumerate(cams):
        print("[{}] Serial #: {}, User ID: {}".format(i + 1, c["serial"], c["userid"] if c["userid"] else "{no user id}"))
