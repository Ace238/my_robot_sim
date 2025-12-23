import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # Package name
    pkg_name = 'my_robot_sim'
    
    # Paths
    pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot_gz.urdf.xacro')
    world_file = os.path.join(pkg_share, 'worlds', 'empty.sdf')
    
    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            urdf_file,
        ]
    )
    
    robot_description = {"robot_description": robot_description_content}

    # Start Gazebo Harmonic
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen'
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )
    
    # Spawn robot in Gazebo using ros_gz
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_robot',
            '-x', '0',
            '-y', '0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # Set camera position after spawn
    set_camera = Node(
        package='my_robot_sim',
        executable='set_camera.py',
        output='screen'
    )
    
    # Joint state publisher (optional, for manual joint control in RViz)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=LaunchConfiguration('gui', default='false')
    )
    
    # Bridge between ROS 2 and Gazebo (for cmd_vel, odom, etc.)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/my_robot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/my_robot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        ],
        output='screen',
        remappings=[
            ('/model/my_robot/cmd_vel', '/cmd_vel'),
            ('/model/my_robot/odometry', '/odom'),
        ]
    )

    # RViz
    rviz_config_file = os.path.join(pkg_share, 'config', 'robot.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else []
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='false', description='Start joint state publisher GUI'),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        set_camera,
        bridge,
        rviz,
    ])