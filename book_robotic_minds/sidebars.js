// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // Define sidebar explicitly to include our ROS 2 module
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1-ros2/intro-to-ros2-and-physical-ai',
        'module-1-ros2/ros2-nodes-topics-services-actions',
        'module-1-ros2/bridging-python-agents-ros2-rclpy',
        'module-1-ros2/understanding-urdf-humanoid-robots',
        'module-1-ros2/intro-to-ros2-control-architecture',
        'module-1-ros2/summary',
        'module-1-ros2/glossary',
        'module-1-ros2/resources'
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin Simulation',
      items: [
        'module-2-digital-twin/intro',
        'module-2-digital-twin/intro-to-digital-twins',
        'module-2-digital-twin/physics-simulation-gazebo',
        'module-2-digital-twin/high-fidelity-visualization-unity',
        'module-2-digital-twin/sensor-simulation',
        'module-2-digital-twin/summary',
        'module-2-digital-twin/glossary',
        'module-2-digital-twin/resources'
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'module-3-ai-brain/intro',
        'module-3-ai-brain/nvidia-isaac-sim',
        'module-3-ai-brain/isaac-ros',
        'module-3-ai-brain/nav2-humanoid-navigation',
        'module-3-ai-brain/summary',
        'module-3-ai-brain/glossary',
        'module-3-ai-brain/resources'
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module-4-vla/intro',
        'module-4-vla/voice-to-action-speech-recognition',
        'module-4-vla/llm-cognitive-planning',
        'module-4-vla/vision-guided-action',
        'module-4-vla/capstone-autonomous-humanoid',
        'module-4-vla/summary',
        'module-4-vla/glossary',
        'module-4-vla/resources'
      ],
    },
    {
      type: 'category',
      label: 'Tutorial',
      items: [
        'tutorial-basics/create-a-document',
        'tutorial-basics/create-a-page',
        'tutorial-basics/deploy-your-site',
      ],
    },
  ],
};

export default sidebars;
