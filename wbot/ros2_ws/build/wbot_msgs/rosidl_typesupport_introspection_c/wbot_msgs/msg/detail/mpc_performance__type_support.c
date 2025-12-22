// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "wbot_msgs/msg/detail/mpc_performance__rosidl_typesupport_introspection_c.h"
#include "wbot_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "wbot_msgs/msg/detail/mpc_performance__functions.h"
#include "wbot_msgs/msg/detail/mpc_performance__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  wbot_msgs__msg__MpcPerformance__init(message_memory);
}

void wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_fini_function(void * message_memory)
{
  wbot_msgs__msg__MpcPerformance__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_member_array[6] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "solve_time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, solve_time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "iterations",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, iterations),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "converged",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, converged),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "cost",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, cost),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mpc_frequency",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__MpcPerformance, mpc_frequency),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_members = {
  "wbot_msgs__msg",  // message namespace
  "MpcPerformance",  // message name
  6,  // number of fields
  sizeof(wbot_msgs__msg__MpcPerformance),
  wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_member_array,  // message members
  wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_init_function,  // function to initialize message memory (memory has to be allocated)
  wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_type_support_handle = {
  0,
  &wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_wbot_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wbot_msgs, msg, MpcPerformance)() {
  wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_type_support_handle.typesupport_identifier) {
    wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &wbot_msgs__msg__MpcPerformance__rosidl_typesupport_introspection_c__MpcPerformance_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
