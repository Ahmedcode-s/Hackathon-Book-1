---
sidebar_position: 2
---

# ROS 2 Nodes, Topics, Services, and Actions

## Overview

This chapter explores the core communication mechanisms in ROS 2: nodes, topics, services, and actions. These components form the foundation of ROS 2's distributed computing architecture, enabling complex robotic systems to communicate effectively.

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the concept of ROS 2 nodes and their role in system architecture
- Explain how topics enable message passing between nodes
- Describe services and request-response communication patterns
- Understand actions for long-running tasks with feedback
- Identify appropriate use cases for each communication pattern

## Nodes: The Building Blocks of ROS 2

In ROS 2, a node is an executable that uses ROS 2 client library to communicate with other nodes. Nodes are the fundamental building blocks of a ROS 2 system.

Each node typically performs a specific function, such as:
- Processing sensor data
- Controlling actuators
- Performing high-level planning
- Providing user interfaces

Nodes are designed to be lightweight and modular, promoting a distributed architecture where complex behaviors emerge from simple, specialized components working together.

### Node Implementation Example
A node is created using a client library like rclpy (Python) or rclcpp (C++), and contains:
- Publishers and subscribers for topic communication
- Service clients and servers for request-response communication
- Action clients and servers for long-running tasks
- Timers and callbacks for event handling

## Topics and Message Passing

Topics are named buses over which nodes exchange messages. Topic-based communication is asynchronous and follows a publish-subscribe pattern.

### Publisher-Subscriber Pattern
- Publishers send messages to a topic without knowledge of subscribers
- Subscribers receive messages from topics they are subscribed to
- Multiple publishers and subscribers can exist for the same topic
- Communication is decoupled: publishers and subscribers don't need to run simultaneously

### Message Types
Messages sent over topics have defined data structures called message types (msg files). Common message types include:
- std_msgs: Basic data types (integers, floats, strings)
- sensor_msgs: Sensor data (images, laser scans, IMU data)
- geometry_msgs: Spatial information (positions, orientations, velocities)

### Quality of Service (QoS)
ROS 2 provides Quality of Service settings that allow fine-tuning of communication behavior:
- Reliability: Best effort vs. reliable delivery
- Durability: Volatile vs. transient local (replay last message to new subscribers)
- History: Keep all messages vs. keep last N messages

## Services: Request-Response Communication

Services provide a request-response communication pattern in ROS 2. A service client sends a request to a service server, which processes the request and returns a response.

### Service Characteristics
- Synchronous communication (client waits for response)
- Point-to-point: one client communicates with one server
- Request and response have defined message types
- Useful for operations that have a clear start and end

### Service Use Cases
- Configuration changes
- Triggering specific actions
- Querying system status
- Calibration procedures

## Actions: Long-Running Tasks with Feedback

Actions are used for long-running tasks that require feedback and the ability to cancel the task. They extend the service concept with additional capabilities.

### Action Components
An action includes three message types:
- Goal: Defines the action to be performed
- Result: Contains the outcome of the action
- Feedback: Provides periodic updates during execution

### Action Characteristics
- Asynchronous execution
- Support for preemption/cancellation
- Continuous feedback during execution
- Useful for tasks like navigation, manipulation, or complex control

### Action Use Cases
- Navigation to a goal location
- Arm trajectory execution
- Complex manipulation tasks
- Any task requiring progress monitoring

## Conceptual Diagram: Communication Patterns

```
Node A                    Node B
  |                         |
  |----[Topic Publish]------->|[Topic Subscribe]
  |                         |
  |<-----[Topic Publish]-----|[Topic Subscribe]
  |                         |
  |---[Service Request]----->|[Service Server]
  |<---[Service Response]----|
  |                         |
  |---[Action Goal]--------->|[Action Server]
  |<---[Feedback]------------|
  |<---[Result]--------------|
```

## Practical Examples in Humanoid Robotics

### Example 1: Sensor Data Distribution
A sensor node publishes joint positions to `/joint_states` topic, which multiple other nodes (control, monitoring, visualization) subscribe to.

### Example 2: Command Execution
A high-level planner sends a service request to a trajectory execution node to move the robot's arm to a specific position.

### Example 3: Navigation Task
A navigation action is sent to move the humanoid to a specific location, with continuous feedback about progress and the ability to cancel if obstacles are detected.

## Comparison of Communication Patterns

| Pattern | Type | Use Case | Characteristics |
|---------|------|----------|-----------------|
| Topics | Publish-Subscribe | Data distribution | Asynchronous, decoupled |
| Services | Request-Response | Simple queries | Synchronous, point-to-point |
| Actions | Goal-Based | Long-running tasks | Asynchronous with feedback/cancel |

## Summary

This chapter covered the fundamental communication patterns in ROS 2. We explored nodes as the building blocks of ROS 2 systems, topics for asynchronous data distribution, services for request-response interactions, and actions for long-running tasks with feedback. These patterns provide the flexibility needed to build complex robotic systems. The next chapter will explore how Python AI agents interface with these communication mechanisms.

## Next Steps

- [Chapter 1: Introduction to ROS 2 and Physical AI](./intro-to-ros2-and-physical-ai.md) - Review middleware concepts
- [Chapter 3: Bridging Python Agents to ROS 2 with rclpy](./bridging-python-agents-ros2-rclpy.md) - Learn how to implement these patterns in Python
- [Chapter 4: Understanding URDF for Humanoid Robots](./understanding-urdf-humanoid-robots.md) - Understand robot structure definition
- [Chapter 5: Designing ROS 2 Control Architecture](./intro-to-ros2-control-architecture.md) - Design complete control systems
- [Module Summary](./summary.md) - Consolidate all concepts

## Review Questions

1. What is the role of a node in ROS 2 architecture?
2. How do topics enable communication between nodes?
3. What is the difference between services and actions?
4. When would you use actions instead of services?
5. Explain the Quality of Service (QoS) settings in ROS 2 topics.
6. Provide examples of when you would use each communication pattern in humanoid robotics.