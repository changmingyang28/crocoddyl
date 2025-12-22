// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from wbot_msgs:msg/WbotControl.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "wbot_msgs/msg/detail/wbot_control__rosidl_typesupport_introspection_c.h"
#include "wbot_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "wbot_msgs/msg/detail/wbot_control__functions.h"
#include "wbot_msgs/msg/detail/wbot_control__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `control`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  wbot_msgs__msg__WbotControl__init(message_memory);
}

void wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_fini_function(void * message_memory)
{
  wbot_msgs__msg__WbotControl__fini(message_memory);
}

size_t wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__size_function__WbotControl__control(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_const_function__WbotControl__control(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_function__WbotControl__control(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__fetch_function__WbotControl__control(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_const_function__WbotControl__control(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__assign_function__WbotControl__control(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_function__WbotControl__control(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__resize_function__WbotControl__control(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_member_array[4] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__WbotControl, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__WbotControl, time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "control",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__WbotControl, control),  // bytes offset in struct
    NULL,  // default value
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__size_function__WbotControl__control,  // size() function pointer
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_const_function__WbotControl__control,  // get_const(index) function pointer
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__get_function__WbotControl__control,  // get(index) function pointer
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__fetch_function__WbotControl__control,  // fetch(index, &value) function pointer
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__assign_function__WbotControl__control,  // assign(index, value) function pointer
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__resize_function__WbotControl__control  // resize(index) function pointer
  },
  {
    "valid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wbot_msgs__msg__WbotControl, valid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_members = {
  "wbot_msgs__msg",  // message namespace
  "WbotControl",  // message name
  4,  // number of fields
  sizeof(wbot_msgs__msg__WbotControl),
  wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_member_array,  // message members
  wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_init_function,  // function to initialize message memory (memory has to be allocated)
  wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_type_support_handle = {
  0,
  &wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_wbot_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wbot_msgs, msg, WbotControl)() {
  wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_type_support_handle.typesupport_identifier) {
    wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &wbot_msgs__msg__WbotControl__rosidl_typesupport_introspection_c__WbotControl_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
