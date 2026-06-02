import os, sys
sys.path.append(os.path.dirname(__file__))

from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from launch_common import common_launch_arguments, build_context


def launch_setup(context, *args, **kwargs):
    cfg = build_context(
        LaunchConfiguration('robot_make').perform(context),
        LaunchConfiguration('robot_model').perform(context),
        LaunchConfiguration('robot_source').perform(context),
        LaunchConfiguration('workstation').perform(context),
        # GEN3/real-robot additions. Leave these empty for the original Panda path.
        planning_group_override=LaunchConfiguration('planning_group').perform(context),
        base_frame_override=LaunchConfiguration('base_frame').perform(context),
        ee_link_override=LaunchConfiguration('ee_link').perform(context),
        use_sim_time=LaunchConfiguration('use_sim_time').perform(context),
        launch_move_group=LaunchConfiguration('launch_move_group').perform(context),
        moveit_config_package_override=LaunchConfiguration('moveit_config_package').perform(context),
        robot_ip=LaunchConfiguration('robot_ip').perform(context),
        use_fake_hardware=LaunchConfiguration('use_fake_hardware').perform(context),
    )

    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        emulate_tty=True,
        parameters=[
            cfg['robot_description'],
            cfg['robot_description_semantic'],
            cfg['robot_description_kinematics'],
            cfg['ompl_planning_pipeline_config'],
            cfg['trajectory_execution'],
            cfg['moveit_controllers'],
            cfg['planning_scene_monitor_parameters'],
            cfg['joint_limits_yaml'],
            # Original simulation line:
            # {'use_sim_time': True},
            # GEN3/real robot: expose as launch arg. Use False when robot.launch.py is used.
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
        # GEN3/real robot: your Kinova robot.launch.py already starts move_group.
        # Run this node only when launch_move_group:=True.
        condition=IfCondition(LaunchConfiguration('launch_move_group')),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        emulate_tty=True,
        arguments=['-d', os.path.join(cfg['moveit_config_path'], 'config', 'moveit.rviz')],
        parameters=[
            cfg['robot_description'],
            cfg['robot_description_semantic'],
            cfg['ompl_planning_pipeline_config'],
            cfg['robot_description_kinematics'],
            cfg['joint_limits_yaml'],
        ],
        condition=IfCondition(LaunchConfiguration('launch_rviz')),
    )

    common_params = [
        {'planning_group': cfg['planning_group']},
        # GEN3/real-robot additions used by modified C++ service nodes.
        {'base_frame': cfg['base_frame']},
        {'ee_link': cfg['ee_link']},
        {'use_sim_time': LaunchConfiguration('use_sim_time')},
        cfg['robot_description'],
        cfg['robot_description_semantic'],
    ]

    move_cartesian = Node(
        package='compare_flexbe_utilities',
        executable='cartesian_move_to_pose_service',
        name='cartesian_move_to_pose_service',
        output='screen',
        parameters=common_params,
    )

    move_pose = Node(
        package='compare_flexbe_utilities',
        executable='move_to_pose_service',
        name='move_to_pose_service',
        output='screen',
        parameters=common_params,
    )

    move_named = Node(
        package='compare_flexbe_utilities',
        executable='move_to_named_pose_service',
        name='move_to_named_pose_service',
        output='screen',
        parameters=common_params,
    )

    reach_to_grasp = Node(
        package='compare_flexbe_utilities',
        executable='reach_to_grasp_service',
        name='reach_to_grasp_service',
        output='screen',
        parameters=common_params,
    )


    return [
        run_move_group_node,
        rviz_node,
        move_cartesian,
        move_pose,
        move_named,
        reach_to_grasp,
    ]



def generate_launch_description():
    return LaunchDescription([
        *common_launch_arguments(include_rviz=True),
        OpaqueFunction(function=launch_setup),
    ])
