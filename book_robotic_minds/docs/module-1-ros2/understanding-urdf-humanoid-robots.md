---
sidebar_position: 4
---

# Understanding URDF for Humanoid Robots

## Overview

This chapter explains how robot structure is defined using URDF (Unified Robot Description Format), particularly for humanoid robots. URDF is essential for modeling robot kinematics, dynamics, and visual representation in ROS 2 systems.

## Learning Objectives

By the end of this chapter, you will be able to:
- Explain URDF as the Unified Robot Description Format
- Describe links and joints as fundamental URDF components
- Understand visual, collision, and inertial properties in URDF
- Explain how URDF models humanoid robot structure
- Understand how URDF integrates with ROS 2 control systems
- Create basic URDF models for simple robot structures

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML format for representing a robot model. It defines the physical and visual properties of a robot, including:
- Kinematic structure (links and joints)
- Visual appearance (meshes, colors, materials)
- Collision properties (shapes for collision detection)
- Inertial properties (mass, center of mass, moments of inertia)

URDF files typically have the `.urdf` extension and are loaded into ROS 2 systems to provide robot models for simulation, visualization, and control.

## Links: The Rigid Bodies

Links are the fundamental building blocks of URDF that represent rigid bodies in the robot. Each link contains:

### Visual Elements
- Geometry: Shape (box, cylinder, sphere, mesh)
- Origin: Position and orientation relative to the link frame
- Material: Color and visual properties

### Collision Elements
- Geometry: Shape used for collision detection
- Origin: Position and orientation relative to the link frame

### Inertial Elements
- Mass: The mass of the link
- Inertia matrix: Moments of inertia about the center of mass

### Example Link Definition
```xml
<link name="base_link">
  <visual>
    <geometry>
      <cylinder radius="0.2" length="0.6"/>
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.2" length="0.6"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="10"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>
```

## Joints: Connecting Links

Joints connect links together and define the kinematic relationship between them. Each joint has:

### Joint Properties
- Type: revolute, continuous, prismatic, fixed, floating, planar
- Parent: The parent link in the kinematic chain
- Child: The child link in the kinematic chain
- Origin: Position and orientation of the joint relative to the parent link
- Axis: The axis of motion for the joint

### Joint Types
- Fixed: No motion between parent and child links
- Revolute: Single axis rotation with limits
- Continuous: Single axis rotation without limits
- Prismatic: Single axis translation with limits
- Floating: Six degrees of freedom
- Planar: Motion on a plane

### Example Joint Definition
```xml
<joint name="base_to_wheel" type="continuous">
  <parent link="base_link"/>
  <child link="wheel_link"/>
  <origin xyz="0.1 0.2 0.0" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
</joint>
```

## URDF for Humanoid Robots

Humanoid robots require special considerations in their URDF models due to their complex structure and degrees of freedom.

### Humanoid Robot Structure
A typical humanoid robot consists of:
- Torso: The central body structure
- Head: Contains sensors and possibly a display
- Arms: With shoulder, elbow, and wrist joints
- Legs: With hip, knee, and ankle joints
- Hands: With multiple joints for manipulation

### Key Considerations for Humanoid URDF
- **Kinematic Chains**: Each limb forms a kinematic chain from torso to end effector
- **Degrees of Freedom**: Humanoid robots typically have 20-30+ DOF
- **Balance**: Center of mass and stability considerations
- **Actuator Limits**: Joint angle and velocity constraints
- **Sensor Integration**: Mounting points for cameras, IMUs, etc.

### Example Humanoid Segment
```xml
<!-- Left Arm Segment -->
<link name="left_shoulder">
  <visual>
    <geometry>
      <box size="0.1 0.1 0.1"/>
    </geometry>
    <material name="gray">
      <color rgba="0.5 0.5 0.5 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.1 0.1 0.1"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="1"/>
    <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
  </inertial>
</link>

<joint name="left_shoulder_joint" type="revolute">
  <parent link="torso"/>
  <child link="left_shoulder"/>
  <origin xyz="0.0 0.2 0.1" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

## Visual and Collision Properties

URDF distinguishes between visual and collision properties to optimize performance:

### Visual Properties
- Used for rendering and visualization
- Can include complex meshes and materials
- May use simplified shapes for real-time rendering
- Does not affect physics simulation

### Collision Properties
- Used for collision detection
- Often use simplified shapes for performance
- Must accurately represent physical boundaries
- Critical for physics simulation and safety

### Inertial Properties
- Define mass distribution for physics simulation
- Affect robot dynamics and control
- Must be accurate for realistic simulation
- Include mass, center of mass, and inertia tensor

## Integration with ROS 2

URDF models integrate with ROS 2 systems in several ways:

### Robot State Publisher
- Reads URDF and joint positions
- Publishes TF transforms for visualization
- Enables coordinate frame transformations

### Simulation
- Used by Gazebo and other simulators
- Provides physics properties for realistic simulation
- Enables collision detection and response

### Control Systems
- Kinematic models for motion planning
- Inverse kinematics calculations
- Trajectory generation and execution

### Visualization
- Robot representation in RViz
- Joint state visualization
- Path planning visualization

## URDF Tools and Ecosystem

### xacro: XML Macros for URDF
xacro is a macro language that extends URDF with:
- Variables and constants
- Mathematical expressions
- Reusable macros
- Conditional statements

### Common URDF Packages
- `urdf`: Core URDF parsing and processing
- `joint_state_publisher`: Publishes joint states
- `robot_state_publisher`: Publishes TF transforms
- `rviz`: Visualization with robot models

## Conceptual Diagram: URDF in ROS 2 System

```
URDF File (.urdf)
       |
       v
Robot State Publisher
       |
       v
TF Tree (Transforms)
       |
       v
RViz Visualization
       |
       v
Simulation/Control Systems
```

## Best Practices for URDF Development

### Structure and Organization
- Use consistent naming conventions
- Organize complex robots into logical segments
- Use xacro for complex robots to reduce redundancy
- Include proper documentation in comments

### Physical Accuracy
- Ensure mass properties are realistic
- Verify joint limits match physical constraints
- Use appropriate collision geometries
- Validate center of mass calculations

### Performance Considerations
- Simplify collision geometries for performance
- Use appropriate mesh resolution
- Limit the number of small links
- Consider computational complexity for real-time systems

## Summary

This chapter covered the fundamentals of URDF for humanoid robot modeling. We explored links and joints as the basic building blocks, visual and collision properties, and how URDF integrates with ROS 2 systems. URDF is essential for robot simulation, visualization, and control in ROS 2 environments.

## Next Steps

- [Chapter 1: Introduction to ROS 2 and Physical AI](./intro-to-ros2-and-physical-ai.md) - Review middleware concepts
- [Chapter 2: ROS 2 Nodes, Topics, Services, and Actions](./ros2-nodes-topics-services-actions.md) - Review communication patterns
- [Chapter 3: Bridging Python Agents to ROS 2 with rclpy](./bridging-python-agents-ros2-rclpy.md) - Review Python integration
- [Chapter 5: Designing ROS 2 Control Architecture](./intro-to-ros2-control-architecture.md) - Design complete control systems
- [Module Summary](./summary.md) - Consolidate all concepts

## Review Questions

1. What is URDF and its role in robot modeling?
2. What are the fundamental components of URDF?
3. How do visual and collision properties differ in URDF?
4. How does URDF integrate with ROS 2 control systems?
5. What are the different joint types available in URDF?
6. Explain the importance of inertial properties in URDF for humanoid robots.
7. How does xacro enhance URDF development?