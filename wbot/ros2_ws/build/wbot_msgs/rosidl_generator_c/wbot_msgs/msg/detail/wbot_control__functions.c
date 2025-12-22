// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wbot_msgs:msg/WbotControl.idl
// generated code does not contain a copyright notice
#include "wbot_msgs/msg/detail/wbot_control__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `control`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
wbot_msgs__msg__WbotControl__init(wbot_msgs__msg__WbotControl * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    wbot_msgs__msg__WbotControl__fini(msg);
    return false;
  }
  // time
  // control
  if (!rosidl_runtime_c__double__Sequence__init(&msg->control, 0)) {
    wbot_msgs__msg__WbotControl__fini(msg);
    return false;
  }
  // valid
  return true;
}

void
wbot_msgs__msg__WbotControl__fini(wbot_msgs__msg__WbotControl * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // time
  // control
  rosidl_runtime_c__double__Sequence__fini(&msg->control);
  // valid
}

bool
wbot_msgs__msg__WbotControl__are_equal(const wbot_msgs__msg__WbotControl * lhs, const wbot_msgs__msg__WbotControl * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // time
  if (lhs->time != rhs->time) {
    return false;
  }
  // control
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->control), &(rhs->control)))
  {
    return false;
  }
  // valid
  if (lhs->valid != rhs->valid) {
    return false;
  }
  return true;
}

bool
wbot_msgs__msg__WbotControl__copy(
  const wbot_msgs__msg__WbotControl * input,
  wbot_msgs__msg__WbotControl * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // time
  output->time = input->time;
  // control
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->control), &(output->control)))
  {
    return false;
  }
  // valid
  output->valid = input->valid;
  return true;
}

wbot_msgs__msg__WbotControl *
wbot_msgs__msg__WbotControl__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__WbotControl * msg = (wbot_msgs__msg__WbotControl *)allocator.allocate(sizeof(wbot_msgs__msg__WbotControl), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wbot_msgs__msg__WbotControl));
  bool success = wbot_msgs__msg__WbotControl__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wbot_msgs__msg__WbotControl__destroy(wbot_msgs__msg__WbotControl * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wbot_msgs__msg__WbotControl__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wbot_msgs__msg__WbotControl__Sequence__init(wbot_msgs__msg__WbotControl__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__WbotControl * data = NULL;

  if (size) {
    data = (wbot_msgs__msg__WbotControl *)allocator.zero_allocate(size, sizeof(wbot_msgs__msg__WbotControl), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wbot_msgs__msg__WbotControl__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wbot_msgs__msg__WbotControl__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
wbot_msgs__msg__WbotControl__Sequence__fini(wbot_msgs__msg__WbotControl__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      wbot_msgs__msg__WbotControl__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

wbot_msgs__msg__WbotControl__Sequence *
wbot_msgs__msg__WbotControl__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__WbotControl__Sequence * array = (wbot_msgs__msg__WbotControl__Sequence *)allocator.allocate(sizeof(wbot_msgs__msg__WbotControl__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wbot_msgs__msg__WbotControl__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wbot_msgs__msg__WbotControl__Sequence__destroy(wbot_msgs__msg__WbotControl__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wbot_msgs__msg__WbotControl__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wbot_msgs__msg__WbotControl__Sequence__are_equal(const wbot_msgs__msg__WbotControl__Sequence * lhs, const wbot_msgs__msg__WbotControl__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wbot_msgs__msg__WbotControl__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wbot_msgs__msg__WbotControl__Sequence__copy(
  const wbot_msgs__msg__WbotControl__Sequence * input,
  wbot_msgs__msg__WbotControl__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wbot_msgs__msg__WbotControl);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wbot_msgs__msg__WbotControl * data =
      (wbot_msgs__msg__WbotControl *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wbot_msgs__msg__WbotControl__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wbot_msgs__msg__WbotControl__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wbot_msgs__msg__WbotControl__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
