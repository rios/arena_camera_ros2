# Copyright RIOS AI, Inc. Licensed under the Apache License, Version 2.0.

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup


data = generate_distutils_setup(
    packages=["arena_camera_ros"],
    package_dir={"": "src"}
)

setup(**data)
