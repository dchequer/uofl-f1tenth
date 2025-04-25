from setuptools import setup
import os
from glob import glob

package_name = "pure_pursuit_controller"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/pure_pursuit.launch.py"]),
        ("share/" + package_name + "/waypoints", ["waypoints/waypoints.csv"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="uofl_tenth",
    maintainer_email="uofl_tenth@todo.todo",
    description="Pure Pursuit path tracking algorithm for F1Tenth/Roboracer",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pure_pursuit = pure_pursuit_controller.pure_pursuit:main",
            "waypoint_recorder = pure_pursuit_controller.waypoint_recorder:main",
            "waypoint_viz = pure_pursuit_controller.waypoint_viz:main",
        ],
    },
)
