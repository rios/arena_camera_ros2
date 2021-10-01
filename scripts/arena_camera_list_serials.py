#!/usr/bin/env python
# arena_camera_list_serials.py -- Lists camera serials
# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

from arena_camera_ros.ArenaUtils import list_cameras


if __name__ == "__main__":
    cams = list_cameras()
    for i, c in enumerate(cams):
        serial = c["serial"] if "serial" in c.keys() else "{no serial no}"
        userid = c["userid"] if "userid" in c.keys() else "{no user id}"

        print("[{}] Serial #: {}, User ID: {}".format(i + 1, serial, userid))
