from setuptools import find_packages, setup

package_name = 'gz_robot_lidar_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/demo_gz_sim_joint_states.launch.py',
             'launch/demo_gz_sim_tf_bridge.launch.py',]),
        ('share/' + package_name + '/rviz',
            ['rviz/gz_ma2010_joint_states.rviz',
             'rviz/gz_ma2010_tf_bridge.rviz',]),
        ('share/' + package_name + '/urdf',
            ['urdf/gz_ma2010.xacro',
             'urdf/gz_ma2010.sdf',]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gz_joint_state_publisher_gui = calib_profilo.gz_joint_state_publisher_gui:main'
        ],
    },
)
