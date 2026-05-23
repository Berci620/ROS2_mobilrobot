import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction # <-- IMPORT ADDED HERE
from launch.launch_description_sources import PythonLaunchDescriptionSource

def find_path(package_name: str, launch_file_name: str) -> str:
    """
    Helper function to construct the absolute path to a launch file.
    Returns the path as a string.
    """
    pkg_dir = get_package_share_directory(package_name)
    return os.path.join(pkg_dir, 'launch', launch_file_name)


def generate_launch_description():
    # Create an empty list to hold all launch actions.
    # This makes it easy to add as many files or nodes as needed.
    launch_actions = []
    
    # Setup turtlebot4_sim launch file (Starts Immediately)
    turtlebot4sim_launch_path = find_path('turtlebot4_ignition_bringup', 'turtlebot4_ignition.launch.py')
    turtlebot4sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(turtlebot4sim_launch_path)
    )
    launch_actions.append(turtlebot4sim_launch)

    # Setup slam launch file (Waits 3 seconds)
    slam_launch_path = find_path('turtlebot4_navigation', 'slam.launch.py')
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch_path)
    )
    
    # Wrap the SLAM launch in a TimerAction
    delayed_slam = TimerAction(
        period=10.0,
        actions=[slam_launch]
    )
    launch_actions.append(delayed_slam)

    # Setup rviz slam visualization (Waits 6 seconds total)
    rviz_launch_path = find_path('turtlebot4_viz', 'view_robot.launch.py')
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rviz_launch_path)
    )
    
    # Wrap the RViz launch in a TimerAction
    delayed_rviz = TimerAction(
        period=15.0,
        actions=[rviz_launch]
    )
    launch_actions.append(delayed_rviz)
    

    #Return the populated list wrapped in a LaunchDescription
    return LaunchDescription(launch_actions)