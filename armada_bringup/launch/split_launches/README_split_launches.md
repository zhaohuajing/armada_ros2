# Split Launch Files for Armada Bringup

This folder contains a modularized version of the original monolithic launch flow.  
Instead of launching the full robot + simulation + perception + FlexBE stack at once, these launch files let you bring up only the modules you need.

This is useful for:
- lighter startup
- easier debugging
- launching only simulation, only MoveIt, or only perception
- avoiding unnecessary heavy nodes when testing individual components

## Launch Files Overview

### `sim_world.launch.py`
Launches the Gazebo simulation world and related Gazebo service bridges.

Main functions:
- starts Gazebo using the robot world SDF
- spawns the scene from `mnet_scenes_gazebo`
- provides Gazebo create/remove/set_pose service bridges

Typical use:
- when you want the world and scene objects
- when testing Gazebo services or object spawning
- when preparing to later spawn the robot and camera

---

### `sim_robot.launch.py`
Launches the robot-related simulation components.

Main functions:
- publishes `robot_description`
- spawns the robot into Gazebo
- launches the main ROS-Gazebo topic bridge
- launches `robot_state_publisher`
- spawns arm and hand controllers

Typical use:
- when you want the robot in simulation
- when using Gazebo together with MoveIt
- when other modules depend on robot TF and controllers

---

### `sim_camera.launch.py`
Launches the simulated RGB-D camera and its static TF.

Main functions:
- spawns the RGB-D camera model into Gazebo
- publishes static transform for the camera
- supports different camera pose presets through `camera_pose`

Supported camera presets:
- `tabletop`
- `topdown`
- `angled45`

Typical use:
- when testing perception pipelines
- when needing RGB, depth, or point cloud topics
- when adjusting simulated camera placement

---

### `moveit_core.launch.py`
Launches MoveIt and motion-related utility services.

Main functions:
- starts `move_group`
- optionally launches RViz
- starts motion service nodes:
  - `cartesian_move_to_pose_service`
  - `move_to_pose_service`
  - `move_to_named_pose_service`
  - `reach_to_grasp_service`

Typical use:
- when testing planning and execution
- when using MoveIt without launching all perception modules
- when launching RViz for motion planning

---

### `perception_classic.launch.py`
Launches classical point-cloud and grasp-related service nodes.

Main functions:
- point cloud retrieval/filtering
- Euclidean clustering
- point cloud filtering by indices
- classical GPD-based grasp detection
- grasp pose computation

Typical use:
- when testing traditional point-cloud perception
- when using GPD instead of learned grasping

---

### `perception_learned.launch.py`
Launches learned segmentation and grasping services.

Main functions:
- Contact-GraspNet cloud service
- Contact-GraspNet RGB-D service
- Unseen Object Clustering cloud service
- Unseen Object Clustering RGB-D service
- GraspSAM service

Launch toggles are available for enabling/disabling specific learned modules.

Typical use:
- when running learned segmentation/grasping pipelines
- when testing UOC, CGN, or GraspSAM independently

---

### `flexbe.launch.py`
Launches FlexBE.

Main functions:
- starts FlexBE onboard and web UI flow

Typical use:
- when running behavior-based demos
- when integrating with FlexBE behaviors and states

---

### `full_system.launch.py`
Convenience launcher that includes multiple split modules together.

Typical use:
- when you want a single command to launch the full stack
- when you want a nearly equivalent alternative to the original monolithic launch

---

### `launch_common.py`
Shared helper module used by the split launch files.

Main functions:
- common launch arguments
- loading URDF/SRDF/YAML files
- building shared robot/MoveIt configuration context
- setting Gazebo environment variables for YCB models

This is not meant to be launched directly.

---

## Common Launch Arguments

Many launch files share the following arguments:

- `robot_make`
- `robot_model`
- `robot_source`
- `workstation`

Current default workstation may be set to:
- `pedestal_workstation`

For `sim_camera.launch.py`, you may override the workstation if desired for camera TF reference.

Additional useful arguments:
- `launch_rviz:=True` for `moveit_core.launch.py`
- `camera_pose:=tabletop|topdown|angled45` for `sim_camera.launch.py`
- `headless:=True/False` for FlexBE-related launch
- learned perception toggles such as:
  - `launch_cgn_cloud`
  - `launch_cgn_rgbd`
  - `launch_uoc_cloud`
  - `launch_uoc_rgbd`
  - `launch_graspsam`

---

## Typical Launch Scenarios

## 1. Launch simulation only

Start only the Gazebo world:

```bash
ros2 launch armada_bringup sim_world.launch.py
```

Launch world + robot:

```bash
ros2 launch armada_bringup sim_world.launch.py
ros2 launch armada_bringup sim_robot.launch.py
```

Launch world + robot + camera:

```bash
ros2 launch armada_bringup sim_world.launch.py
ros2 launch armada_bringup sim_robot.launch.py
ros2 launch armada_bringup sim_camera.launch.py
```

---

## 2. Launch MoveIt with RViz

Launch only MoveIt core with RViz:

```bash
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

This is mainly useful if the robot TF and robot state are already available elsewhere.

More commonly, use it together with simulation:

```bash
ros2 launch armada_bringup sim_world.launch.py
ros2 launch armada_bringup sim_robot.launch.py
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

---

## 3. Launch camera with a specific pose

Tabletop view:

```bash
ros2 launch armada_bringup sim_camera.launch.py camera_pose:=tabletop
```

Top-down view:

```bash
ros2 launch armada_bringup sim_camera.launch.py camera_pose:=topdown
```

45-degree view:

```bash
ros2 launch armada_bringup sim_camera.launch.py camera_pose:=angled45
```

If you want a specific workstation/frame setting just for the camera:

```bash
ros2 launch armada_bringup sim_camera.launch.py workstation:=simple_pedestal camera_pose:=tabletop
```

---

## 4. Launch learned perception only

Launch default learned perception modules:

```bash
ros2 launch armada_bringup perception_learned.launch.py
```

Launch only UOC RGB-D + CGN RGB-D:

```bash
ros2 launch armada_bringup perception_learned.launch.py \
  launch_cgn_cloud:=False \
  launch_cgn_rgbd:=True \
  launch_uoc_cloud:=False \
  launch_uoc_rgbd:=True \
  launch_graspsam:=False
```

Launch only UOC RGB-D + GraspSAM:

```bash
ros2 launch armada_bringup perception_learned.launch.py \
  launch_cgn_cloud:=False \
  launch_cgn_rgbd:=False \
  launch_uoc_cloud:=False \
  launch_uoc_rgbd:=True \
  launch_graspsam:=True
```

---

## 5. Launch classical perception only

```bash
ros2 launch armada_bringup perception_classic.launch.py
```

This is useful when testing:
- point cloud services
- Euclidean clustering
- GPD-based grasp detection

---

## 6. Launch FlexBE only

```bash
ros2 launch armada_bringup flexbe.launch.py
```

Headless example:

```bash
ros2 launch armada_bringup flexbe.launch.py headless:=True
```

---

## 7. Launch the full system with one command

```bash
ros2 launch armada_bringup full_system.launch.py
```

A lighter version without learned perception:

```bash
ros2 launch armada_bringup full_system.launch.py \
  launch_cgn_cloud:=False \
  launch_cgn_rgbd:=False \
  launch_uoc_cloud:=False \
  launch_uoc_rgbd:=False \
  launch_graspsam:=False
```

---

## Recommended Launch Order for Manual Bringup

When launching individual files in separate terminals, the following order is recommended.

### Basic simulation + MoveIt
Terminal 1:
```bash
ros2 launch armada_bringup sim_world.launch.py
```

Terminal 2:
```bash
ros2 launch armada_bringup sim_robot.launch.py
```

Terminal 3:
```bash
ros2 launch armada_bringup sim_camera.launch.py
```

Terminal 4:
```bash
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

---

### Simulation + MoveIt + learned perception
Terminal 1:
```bash
ros2 launch armada_bringup sim_world.launch.py
```

Terminal 2:
```bash
ros2 launch armada_bringup sim_robot.launch.py
```

Terminal 3:
```bash
ros2 launch armada_bringup sim_camera.launch.py
```

Terminal 4:
```bash
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

Terminal 5:
```bash
ros2 launch armada_bringup perception_learned.launch.py
```

---

### Simulation + MoveIt + classical perception
Terminal 1:
```bash
ros2 launch armada_bringup sim_world.launch.py
```

Terminal 2:
```bash
ros2 launch armada_bringup sim_robot.launch.py
```

Terminal 3:
```bash
ros2 launch armada_bringup sim_camera.launch.py
```

Terminal 4:
```bash
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

Terminal 5:
```bash
ros2 launch armada_bringup perception_classic.launch.py
```

---

### Full behavior pipeline example
Terminal 1:
```bash
ros2 launch armada_bringup sim_world.launch.py
```

Terminal 2:
```bash
ros2 launch armada_bringup sim_robot.launch.py
```

Terminal 3:
```bash
ros2 launch armada_bringup sim_camera.launch.py
```

Terminal 4:
```bash
ros2 launch armada_bringup moveit_core.launch.py launch_rviz:=True
```

Terminal 5:
```bash
ros2 launch armada_bringup perception_learned.launch.py
```

Terminal 6:
```bash
ros2 launch armada_bringup flexbe.launch.py headless:=True
```

---

## Example Using a Specific Workstation

If you want all split launch files to use `pedestal_workstation`:

Terminal 1:
```bash
ros2 launch armada_bringup sim_world.launch.py workstation:=pedestal_workstation
```

Terminal 2:
```bash
ros2 launch armada_bringup sim_robot.launch.py workstation:=pedestal_workstation
```

Terminal 3:
```bash
ros2 launch armada_bringup sim_camera.launch.py workstation:=simple_pedestal
```

Terminal 4:
```bash
ros2 launch armada_bringup moveit_core.launch.py workstation:=pedestal_workstation launch_rviz:=True
```

Terminal 5:
```bash
ros2 launch armada_bringup perception_learned.launch.py workstation:=pedestal_workstation
```

---

## Notes and Troubleshooting

### 1. `ModuleNotFoundError: No module named 'launch_common'`
If this happens, make sure the launch file includes:

```python
import os, sys
sys.path.append(os.path.dirname(__file__))
```

before importing `launch_common`.

---

### 2. RViz warning: `Fixed Frame does not exist`
This usually means TF is not being published even though the robot model is loaded.  
Make sure `sim_robot.launch.py` is running so that `robot_state_publisher` and robot-related topics are available.

---

### 3. No Gazebo window appears when launching `moveit_core.launch.py`
This is expected.  
`moveit_core.launch.py` does not launch Gazebo. It only launches MoveIt and optional RViz.

---

### 4. RViz opens but repeatedly prints interactive marker initialization messages
This often happens when TF or the fixed frame is not fully ready.  
Make sure:
- `sim_robot.launch.py` is running
- the fixed frame exists in TF
- the robot model and TF tree are consistent

---

### 5. Scene objects differ from the original monolithic launch
Check the `workstation` argument.  
The split launch files may use a different default workstation than the original launch command.

---

## Suggested Practical Use

For most everyday testing:

- use `sim_world.launch.py`
- use `sim_robot.launch.py`
- use `sim_camera.launch.py`
- use `moveit_core.launch.py launch_rviz:=True`

Then add one of the following depending on the experiment:
- `perception_learned.launch.py`
- `perception_classic.launch.py`
- `flexbe.launch.py`

This gives a lightweight and flexible workflow compared with the original all-in-one launcher.
