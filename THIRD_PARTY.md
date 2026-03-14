# Third-Party Dependencies

This document describes third-party and proprietary dependencies required by
`arena_camera_ros2` that are not distributed with this repository.

## LUCID Arena SDK

- **Vendor:** LUCID Vision Labs, Inc.
- **Version tested:** v0.1.54 (Linux x64)
- **License:** Proprietary — see LUCID's [End User License Agreement](https://thinklucid.com/eula/)
- **Download:** https://thinklucid.com/downloads-hub/
- **Purpose:** Hardware SDK required at runtime to communicate with LUCID cameras.
  The Python package `arena_api` wraps this SDK.

This SDK is **not** redistributed with this package and must be obtained directly
from LUCID Vision Labs. Refer to README.md for installation instructions.

## arena_api (Python)

- **Vendor:** LUCID Vision Labs, Inc.
- **License:** Proprietary — distributed by LUCID
- **Install:** `pip3 install arena_api`
- **Purpose:** Python bindings for the Arena SDK.

## camera_control_msgs

- **Source:** https://github.com/rios-ai/camera_control_msgs
- **License:** Apache-2.0
- **Purpose:** ROS message and service definitions used by this driver for
  camera control actions (GrabImages, SetExposure, SetGain, SetGamma, etc.).
