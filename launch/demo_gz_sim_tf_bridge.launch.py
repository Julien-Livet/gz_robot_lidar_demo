import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    pkg_calib_profilo = get_package_share_directory('calib_profilo')
    return LaunchDescription([
        # Launch gazebo
        ExecuteProcess(
            cmd=[
                'gz', 'sim -r',
                os.path.join(
                    pkg_calib_profilo,
                    'urdf',
                    'gz_ma2010.sdf'
                )
            ],
            additional_env={
                'GZ_SIM_RESOURCE_PATH': "/home/julien/ros2_ws/src"
            },
            output='screen',
            shell=True,
        ),
        # Launch a bridge to forward tf and joint states to ros2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/world/default/model/gz_ma2010/joint_state@'
                'sensor_msgs/msg/JointState[gz.msgs.Model',
                '/model/gz_ma2010/pose@'
                'tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
            ],
            remappings=[
                ('/model/gz_ma2010/pose', '/tf'),
                ('/world/default/model/gz_ma2010/joint_state', '/joint_states')
            ]
        ),
        # Launch rviz
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_calib_profilo, 'rviz', 'gz_ma2010_tf_bridge.rviz')]
        )
    ])
