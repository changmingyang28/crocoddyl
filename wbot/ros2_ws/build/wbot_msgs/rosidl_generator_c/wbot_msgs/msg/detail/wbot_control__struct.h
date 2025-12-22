// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wbot_msgs:msg/WbotControl.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_H_
#define WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_H_

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
// Member 'control'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/WbotControl in the package wbot_msgs.
/**
  * Wbot control input message
  * Contains control vector computed by MPC
 */
typedef struct wbot_msgs__msg__WbotControl
{
  std_msgs__msg__Header header;
  /// Time for which this control is valid
  double time;
  /// Control vector [wheel_left_vel, wheel_right_vel, arm_joint_torques...]
  rosidl_runtime_c__double__Sequence control;
  /// Flag indicating if this is a valid control (solver converged)
  bool valid;
} wbot_msgs__msg__WbotControl;

// Struct for a sequence of wbot_msgs__msg__WbotControl.
typedef struct wbot_msgs__msg__WbotControl__Sequence
{
  wbot_msgs__msg__WbotControl * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wbot_msgs__msg__WbotControl__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_H_
