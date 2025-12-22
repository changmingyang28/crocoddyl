// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wbot_msgs:msg/VelocityCommand.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_H_
#define WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'target_joint_angles'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/VelocityCommand in the package wbot_msgs.
/**
  * High-level velocity command for wbot
  * User specifies desired base velocities
 */
typedef struct wbot_msgs__msg__VelocityCommand
{
  std_msgs__msg__Header header;
  /// Desired forward velocity (m/s)
  double vx;
  /// Desired yaw angular velocity (rad/s)
  double omega_z;
  /// Target arm joint angles (optional, empty means use current)
  rosidl_runtime_c__double__Sequence target_joint_angles;
} wbot_msgs__msg__VelocityCommand;

// Struct for a sequence of wbot_msgs__msg__VelocityCommand.
typedef struct wbot_msgs__msg__VelocityCommand__Sequence
{
  wbot_msgs__msg__VelocityCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wbot_msgs__msg__VelocityCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_H_
