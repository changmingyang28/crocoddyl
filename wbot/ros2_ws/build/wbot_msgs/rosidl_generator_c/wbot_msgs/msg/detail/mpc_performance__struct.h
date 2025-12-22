// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_H_
#define WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_H_

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

/// Struct defined in msg/MpcPerformance in the package wbot_msgs.
/**
  * MPC performance metrics message
  * Published by MPC node for monitoring
 */
typedef struct wbot_msgs__msg__MpcPerformance
{
  std_msgs__msg__Header header;
  /// OCP solve time (seconds)
  double solve_time;
  /// Number of DDP iterations
  int32_t iterations;
  /// Whether solver converged
  bool converged;
  /// Final cost value
  double cost;
  /// MPC computation frequency (Hz)
  double mpc_frequency;
} wbot_msgs__msg__MpcPerformance;

// Struct for a sequence of wbot_msgs__msg__MpcPerformance.
typedef struct wbot_msgs__msg__MpcPerformance__Sequence
{
  wbot_msgs__msg__MpcPerformance * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wbot_msgs__msg__MpcPerformance__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_H_
