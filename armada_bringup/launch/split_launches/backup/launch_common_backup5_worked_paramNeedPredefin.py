import os, sys
import xacro
import yaml

from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable

# GEN3/real-robot addition: allow this shared launch helper to build a Kinova
# MoveIt config when robot_source:=kortex / robot_model:=gen3 is requested.
# Original Panda/Armada behavior is kept below as the default path.
try:
    from moveit_configs_utils import MoveItConfigsBuilder
except Exception:
    MoveItConfigsBuilder = None


def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except OSError:
        return None



def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except OSError:
        return None



def common_launch_arguments(include_flexbe=False, include_rviz=False, include_camera_pose=False, include_perception_toggles=False):
    args = [
        DeclareLaunchArgument(
            'robot_make',
            default_value='panda',
            description='Robot make used to derive controller/planning names.'
        ),
        DeclareLaunchArgument(
            'robot_model',
            default_value='panda',
            description='Robot model used to locate xacro, MoveIt, and Gazebo config.'
        ),
        DeclareLaunchArgument(
            'robot_source',
            default_value='armada',
            description='Package prefix for description/bringup/gazebo packages. Use robot_source:=kortex for the Kinova Gen3 path.'
        ),
        DeclareLaunchArgument(
            'workstation',
            # default_value='simple_pedestal',
            default_value='pedestal_workstation',
            description='Workstation or pedestal suffix used by the xacro file.'
        ),

        # GEN3/real-robot additions. These are harmless for the original Panda path,
        # but make the split launch files usable when robot.launch.py already brings up
        # the Kinova robot and move_group.
        DeclareLaunchArgument(
            'planning_group',
            default_value='',
            description='Override MoveIt planning group. Leave empty to use the original derived value.'
        ),
        DeclareLaunchArgument(
            'base_frame',
            default_value='',
            description='Override base/planning frame for debug markers and grasp transforms. Leave empty for default.'
        ),
        DeclareLaunchArgument(
            'ee_link',
            default_value='',
            description='Optional end-effector link override for MoveGroupInterface.'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulated time. Set False for the real Gen3.'
        ),
        DeclareLaunchArgument(
            'launch_move_group',
            default_value='True',
            description='Start move_group from moveit_core.launch.py. Set False if Kinova robot.launch.py already started move_group.'
        ),
        DeclareLaunchArgument(
            'moveit_config_package',
            default_value='',
            description='Optional MoveIt config package override. For Gen3 default is kinova_gen3_7dof_robotiq_2f_85_moveit_config.'
        ),
        DeclareLaunchArgument(
            'robot_ip',
            default_value='10.10.10.43',
            description='Kinova robot IP used only if this helper needs to build a Kinova robot_description.'
        ),
        DeclareLaunchArgument(
            'use_fake_hardware',
            default_value='true',
            description='Kinova fake hardware flag used only if this helper needs to build a Kinova robot_description.'
        ),

        DeclareLaunchArgument(
            'gripper_group',
            default_value='gripper',
            description='MoveIt gripper group for Gen3/Robotiq reach_to_grasp service.'
        ),
        DeclareLaunchArgument(
            'use_gripper_action',
            default_value='True',
            description='If true, reach_to_grasp commands Robotiq through GripperCommand action instead of MoveIt gripper group.'
        ),
        DeclareLaunchArgument(
            'gripper_action_name',
            default_value='/robotiq_gripper_controller/gripper_cmd',
            description='Robotiq GripperCommand action name.'
        ),
        DeclareLaunchArgument(
            'open_gripper_position',
            default_value='0.0',
            description='Open position for Robotiq gripper action.'
        ),
        DeclareLaunchArgument(
            'close_gripper_position',
            default_value='0.8',
            description='Close position for Robotiq gripper action.'
        ),
        DeclareLaunchArgument(
            'gripper_max_effort',
            default_value='100.0',
            description='Max effort for Robotiq gripper action.'
        ),

        DeclareLaunchArgument(
            'gripper_action_timeout',
            default_value='10.0',
            description='Timeout in seconds for Robotiq gripper action goal/result.'
        ),
        DeclareLaunchArgument(
            'open_before_grasp',
            default_value='True',
            description='If true, reach_to_grasp opens the gripper before closing/lifting.'
        ),
        DeclareLaunchArgument(
            'move_to_grasp_pose_first',
            default_value='False',
            description='If true, reach_to_grasp moves to the grasp pose again. Usually False because MoveOMPL already did this.'
        ),
        DeclareLaunchArgument(
            'pregrasp_base_z_offset',
            default_value='0.0',
            description='Optional base-frame Z offset for an intermediate pregrasp pose.'
        ),
        DeclareLaunchArgument(
            'approach_ee_z_distance',
            default_value='0.10',
            description='Optional approach motion along end-effector Z. Nonzero values can also change X/Y depending on orientation.'
        ),
        DeclareLaunchArgument(
            'lift_base_z_distance',
            default_value='0.10',
            description='Base-frame Z lift after gripper close.'
        ),
        DeclareLaunchArgument(
            'reopen_after_lift',
            default_value='True',
            description='If true, reopen gripper after lift for drop tests.'
        ),
    ]

    if include_flexbe:
        args.extend([
            DeclareLaunchArgument(
                'headless',
                default_value='False',
                description='Run FlexBE OCS without the web UI frontend.'
            ),
        ])

    if include_rviz:
        args.extend([
            DeclareLaunchArgument(
                'launch_rviz',
                default_value='False',
                description='If true, launch RViz.'
            ),
        ])

    if include_camera_pose:
        args.extend([
            DeclareLaunchArgument(
                'camera_pose',
                default_value='tabletop',
                description='Camera pose preset: tabletop, topdown, or angled45.'
            ),
        ])

    if include_perception_toggles:
        args.extend([
            DeclareLaunchArgument('launch_cgn_cloud', default_value='False'),
            DeclareLaunchArgument('launch_cgn_rgbd', default_value='True'),
            DeclareLaunchArgument('launch_uoc_cloud', default_value='False'),
            DeclareLaunchArgument('launch_uoc_rgbd', default_value='True'),
            DeclareLaunchArgument('launch_graspsam', default_value='True'),
        ])

    return args



def _empty_optional_paths():
    """GEN3 helper: return safe empty path entries when Gazebo-only packages are not used."""
    return {
        'gazebo_package_path': '',
        'ros_gz_sim_path': '',
        'mnet_pkg_path': '',
        'flexbe_webui_path': '',
        'ycb_root': '',
    }



def build_context(robot_make, robot_model, robot_source, workstation,
                  planning_group_override='', base_frame_override='', ee_link_override='',
                  use_sim_time='False', launch_move_group='True',
                  moveit_config_package_override='', robot_ip='10.10.10.43',
                  use_fake_hardware='true'):
    # GEN3/real-robot addition: special Kinova/Kortex path.
    # Original code below assumed packages like armada_description, armada_gazebo,
    # and panda_moveit_config. The Kinova MoveIt config you use is generated through
    # MoveItConfigsBuilder, matching robot.launch.py.
    is_kortex_gen3 = (
        robot_source.lower() in ['kortex', 'kinova']
        or robot_model.lower() in ['gen3', 'kinova_gen3_7dof_robotiq_2f_85']
        or robot_make.lower() in ['gen3', 'kinova']
    )

    if is_kortex_gen3:
        if MoveItConfigsBuilder is None:
            raise RuntimeError('moveit_configs_utils is required for the Kinova Gen3 launch_common path.')

        # Original derived package line, not valid for the Kinova generated package:
        # moveit_config_package = f"{robot_model}_moveit_config"
        moveit_config_package = moveit_config_package_override or 'kinova_gen3_7dof_robotiq_2f_85_moveit_config'
        description_package = 'kortex_description'
        bringup_package = 'kortex_bringup'
        gazebo_package = ''

        launch_arguments = {
            'robot_ip': robot_ip,
            'use_fake_hardware': use_fake_hardware,
            'gripper': 'robotiq_2f_85',
            'gripper_joint_name': 'robotiq_85_left_knuckle_joint',
            'dof': '7',
            'gripper_max_velocity': '100.0',
            'gripper_max_force': '100.0',
            'use_internal_bus_gripper_comm': 'true',
            'vision': 'true',
        }

        moveit_config = (
            MoveItConfigsBuilder('gen3', package_name=moveit_config_package)
            .robot_description(mappings=launch_arguments)
            .trajectory_execution(file_path='config/moveit_controllers.yaml')
            .planning_scene_monitor(
                publish_robot_description=True,
                publish_robot_description_semantic=True,
            )
            .planning_pipelines(pipelines=['ompl'])
            .to_moveit_configs()
        )
        moveit_config.moveit_cpp.update({'use_sim_time': str(use_sim_time).lower() == 'true'})

        # Keep these names explicit for the real robot. Verify them with the SRDF/MoveIt logs.
        planning_group = planning_group_override or 'manipulator'
        base_frame = base_frame_override or 'base_link'
        ee_link = ee_link_override or 'end_effector_link'

        moveit_config_path = get_package_share_directory(moveit_config_package)
        robot_description_pkg = get_package_share_directory(description_package)
        try:
            bringup_package_path = get_package_share_directory(bringup_package)
        except Exception:
            bringup_package_path = ''

        # Prefer the MoveItConfigsBuilder dictionaries. This matches the attached robot.launch.py.
        mdict = moveit_config.to_dict()
        robot_description = moveit_config.robot_description
        robot_description_semantic = moveit_config.robot_description_semantic
        robot_description_kinematics = moveit_config.robot_description_kinematics

        # These keys may already be inside mdict; keep separate variables to preserve the
        # original moveit_core.launch.py structure.
        ompl_planning_pipeline_config = moveit_config.planning_pipelines
        joint_limits_yaml = moveit_config.joint_limits
        moveit_controllers = {
            'moveit_simple_controller_manager': load_yaml(moveit_config_package, 'config/moveit_controllers.yaml'),
            'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager',
        }
        trajectory_execution = {
            # Original simulation value:
            # 'moveit_manage_controllers': True,
            # GEN3/real robot: robot.launch.py already spawns controllers.
            'moveit_manage_controllers': False,
            'trajectory_execution.allowed_execution_duration_scaling': 1.2,
            'trajectory_execution.allowed_goal_duration_margin': 0.5,
            'trajectory_execution.allowed_start_tolerance': 0.01,
        }
        planning_scene_monitor_parameters = {
            'publish_planning_scene': True,
            'publish_geometry_updates': True,
            'publish_state_updates': True,
            'publish_transforms_updates': True,
        }

        out = {
            'robot_make': robot_make,
            'robot_model': robot_model,
            'robot_source': robot_source,
            'workstation': workstation,
            'description_package': description_package,
            'bringup_package': bringup_package,
            'moveit_config_package': moveit_config_package,
            'gazebo_package': gazebo_package,
            'robot_description_pkg': robot_description_pkg,
            'bringup_package_path': bringup_package_path,
            'moveit_config_path': moveit_config_path,
            'robot_description': robot_description,
            'robot_description_semantic': robot_description_semantic,
            'robot_description_kinematics': robot_description_kinematics,
            'ompl_planning_pipeline_config': ompl_planning_pipeline_config,
            'moveit_controllers': moveit_controllers,
            'joint_limits_yaml': joint_limits_yaml,
            'trajectory_execution': trajectory_execution,
            'planning_scene_monitor_parameters': planning_scene_monitor_parameters,
            'planning_group': planning_group,
            'base_frame': base_frame,
            'ee_link': ee_link,
            'use_sim_time': str(use_sim_time),
            'launch_move_group': str(launch_move_group),
            'moveit_config': moveit_config,
        }
        out.update(_empty_optional_paths())
        return out

    # -----------------------------
    # Original Panda/Armada path
    # -----------------------------
    description_package = f"{robot_source}_description"
    bringup_package = f"{robot_source}_bringup"
    moveit_config_package = f"{robot_model}_moveit_config"
    gazebo_package = f"{robot_source}_gazebo"

    robot_description_pkg = get_package_share_directory(description_package)
    bringup_package_path = get_package_share_directory(bringup_package)
    moveit_config_path = get_package_share_directory(moveit_config_package)
    gazebo_package_path = get_package_share_directory(gazebo_package)
    ros_gz_sim_path = get_package_share_directory('ros_gz_sim')
    mnet_pkg_path = get_package_share_directory('mnet_scenes_gazebo')
    flexbe_webui_path = get_package_share_directory('flexbe_webui')

    ycb_root = os.path.join(mnet_pkg_path, 'models', 'ycb')

    xacro_path = os.path.join(
        robot_description_pkg,
        robot_model,
        'xacro',
        f"{robot_model}{'_' + workstation if workstation else ''}.urdf.xacro",
    )
    robot_description_config = xacro.process_file(xacro_path)
    robot_description = {'robot_description': robot_description_config.toxml()}

    robot_description_semantic = {
        'robot_description_semantic': load_file(moveit_config_package, f'config/{robot_model}.srdf')
    }
    robot_description_kinematics = {
        'robot_description_kinematics': load_yaml(moveit_config_package, 'config/kinematics.yaml')
    }

    ompl_planning_pipeline_config = {
        'planning_pipelines': ['ompl'],
        'ompl': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': (
                'default_planner_request_adapters/AddTimeOptimalParameterization '
                'default_planner_request_adapters/FixWorkspaceBounds '
                'default_planner_request_adapters/FixStartStateBounds '
                'default_planner_request_adapters/FixStartStateCollision '
                'default_planner_request_adapters/FixStartStatePathConstraints'
            ),
            'start_state_max_bounds_error': 0.5,
        },
    }
    ompl_planning_yaml = load_yaml(moveit_config_package, 'config/ompl_planning.yaml') or {}
    ompl_planning_pipeline_config['ompl'].update(ompl_planning_yaml)

    controllers_yaml = load_yaml(moveit_config_package, 'config/controllers.yaml')
    moveit_controllers = {
        'moveit_simple_controller_manager': controllers_yaml,
        'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager',
    }

    joint_limits_yaml = {
        'robot_description_planning': load_yaml(moveit_config_package, 'config/joint_limits.yaml')
    }

    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.1,
    }

    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
    }

    return {
        'robot_make': robot_make,
        'robot_model': robot_model,
        'robot_source': robot_source,
        'workstation': workstation,
        'description_package': description_package,
        'bringup_package': bringup_package,
        'moveit_config_package': moveit_config_package,
        'gazebo_package': gazebo_package,
        'robot_description_pkg': robot_description_pkg,
        'bringup_package_path': bringup_package_path,
        'moveit_config_path': moveit_config_path,
        'gazebo_package_path': gazebo_package_path,
        'ros_gz_sim_path': ros_gz_sim_path,
        'mnet_pkg_path': mnet_pkg_path,
        'flexbe_webui_path': flexbe_webui_path,
        'ycb_root': ycb_root,
        'robot_description': robot_description,
        'robot_description_semantic': robot_description_semantic,
        'robot_description_kinematics': robot_description_kinematics,
        'ompl_planning_pipeline_config': ompl_planning_pipeline_config,
        'moveit_controllers': moveit_controllers,
        'joint_limits_yaml': joint_limits_yaml,
        'trajectory_execution': trajectory_execution,
        'planning_scene_monitor_parameters': planning_scene_monitor_parameters,
        # Original line:
        # 'planning_group': f'{robot_make}_arm',
        # GEN3-safe: allow explicit override while preserving original derived value.
        'planning_group': planning_group_override or f'{robot_make}_arm',
        'base_frame': base_frame_override or ('panda_link0' if robot_make == 'panda' else f'{robot_make}_link0'),
        'ee_link': ee_link_override or '',
        'use_sim_time': str(use_sim_time),
        'launch_move_group': str(launch_move_group),
    }



def ycb_env_actions(ycb_root):
    return [
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=ycb_root),
        SetEnvironmentVariable(name='GZ_SIM_MODEL_PATH', value=ycb_root),
    ]
