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

    # Parameters only used by reach_to_grasp_service. They are kept separate so the
    # other motion-service nodes do not receive unused gripper parameters.
    reach_to_grasp_params = common_params + [
        {'gripper_group': LaunchConfiguration('gripper_group')},
        {'use_gripper_action': LaunchConfiguration('use_gripper_action')},
        {'gripper_action_name': LaunchConfiguration('gripper_action_name')},
        {'open_gripper_position': LaunchConfiguration('open_gripper_position')},
        {'close_gripper_position': LaunchConfiguration('close_gripper_position')},
        {'gripper_max_effort': LaunchConfiguration('gripper_max_effort')},
        {'gripper_action_timeout': LaunchConfiguration('gripper_action_timeout')},
        {'open_before_grasp': LaunchConfiguration('open_before_grasp')},
        {'move_to_grasp_pose_first': LaunchConfiguration('move_to_grasp_pose_first')},
        {'pregrasp_base_z_offset': LaunchConfiguration('pregrasp_base_z_offset')},
        {'approach_ee_z_distance': LaunchConfiguration('approach_ee_z_distance')},
        {'lift_base_z_distance': LaunchConfiguration('lift_base_z_distance')},
        {'reopen_after_lift': LaunchConfiguration('reopen_after_lift')},
    ]

    # move_cartesian = Node(
    #     package='compare_flexbe_utilities',
    #     executable='cartesian_move_to_pose_service',
    #     name='cartesian_move_to_pose_service',
    #     output='screen',
    #     parameters=common_params,
    # )

    move_pose = Node(
        package='cgn_flexbe_utilities',
        executable='move_to_pose_service',
        name='move_to_pose_service',
        output='screen',
        parameters=common_params,
    )

    # move_named = Node(
    #     package='compare_flexbe_utilities',
    #     executable='move_to_named_pose_service',
    #     name='move_to_named_pose_service',
    #     output='screen',
    #     parameters=common_params,
    # )

    reach_to_grasp = Node(
        package='cgn_flexbe_utilities',
        executable='reach_to_grasp_service',
        name='reach_to_grasp_service',
        output='screen',
        parameters=reach_to_grasp_params,
    )


    return [
        run_move_group_node,
        rviz_node,
        # move_cartesian,
        move_pose,
        # move_named,
        reach_to_grasp,
    ]



def generate_launch_description():
    return LaunchDescription([
        *common_launch_arguments(include_rviz=True),
        OpaqueFunction(function=launch_setup),
    ])
