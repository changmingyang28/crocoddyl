// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wbot_msgs:msg/WbotState.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_H_
#define WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_H_

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
// Member 'state'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/WbotState in the package wbot_msgs.
/**
  * Wbot robot state message
  * Contains full state vector for MPC
 */
typedef struct wbot_msgs__msg__WbotState
{
  std_msgs__msg__Header header;
  /// Current simulation time
  double time;
  /// Full state vector [q0, q1, q2, ..., v0, v1, v2, ...]
  /// For wbot: [base_x, base_y, base_theta, joint_angles..., base_vx, base_vy, base_omega, joint_velocities...]
  rosidl_runtime_c__double__Sequence state;
  /// Current contact mode (for future extension)
  int8_t mode;
} wbot_msgs__msg__WbotState;

// Struct for a sequence of wbot_msgs__msg__WbotState.
typedef struct wbot_msgs__msg__WbotState__Sequence
{
  wbot_msgs__msg__WbotState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wbot_msgs__msg__WbotState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_H_
