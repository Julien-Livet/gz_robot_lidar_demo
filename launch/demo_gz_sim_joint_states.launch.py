import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_calib_profilo = get_package_share_directory('calib_profilo')
    
    # Launch gazebo
    gazebo = ExecuteProcess(
            cmd=[
                'gz', 'sim --verbose -r',
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
        )

    # Launch a bridge to forward tf and joint states to ros2
    bridge = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                'profilo@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
                '/profilo/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
                '/world/default/model/gz_ma2010/joint_state@'
                'sensor_msgs/msg/JointState[gz.msgs.Model',
                '/model/gz_ma2010/pose@'
                'tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
            ],
            remappings=[
                ('/model/gz_ma2010/pose', '/tf'),
                ('/world/default/model/gz_ma2010/joint_state', '/joint_states')
            ],
            output='screen'
        )
    
    # Launch rviz
    rviz = Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_calib_profilo, 'rviz', 'gz_ma2010_joint_states.rviz')]
        )

    # Parse robot description from xacro
    robot_description_file = os.path.join(pkg_calib_profilo, 'urdf', 'gz_ma2010.xacro')
    robot_description_config = xacro.process_file(
        robot_description_file
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    # Spawn
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[{'name': 'gz_ma2010',
                    'topic': 'robot_description'}],
        output='screen',
    )

    static_tf_pub = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_pub',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'gz_ma2010'],
            output='screen'
        )
        
    return LaunchDescription([
        gazebo,
        bridge,
        rviz,
        spawn,
        robot_state_publisher,
        static_tf_pub
    ])
