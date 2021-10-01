#!/usr/bin/env python
# arena_camera_cycle.py -- Fixes camera access and pointer errors
# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

from arena_camera_ros.ArenaUtils import cycle_cameras


if __name__ == "__main__":
    ret = cycle_cameras()
    if not ret:
        print("No cameras detected")
