// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice
#include "wbot_msgs/msg/detail/mpc_performance__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
wbot_msgs__msg__MpcPerformance__init(wbot_msgs__msg__MpcPerformance * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    wbot_msgs__msg__MpcPerformance__fini(msg);
    return false;
  }
  // solve_time
  // iterations
  // converged
  // cost
  // mpc_frequency
  return true;
}

void
wbot_msgs__msg__MpcPerformance__fini(wbot_msgs__msg__MpcPerformance * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // solve_time
  // iterations
  // converged
  // cost
  // mpc_frequency
}

bool
wbot_msgs__msg__MpcPerformance__are_equal(const wbot_msgs__msg__MpcPerformance * lhs, const wbot_msgs__msg__MpcPerformance * rhs)
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
  // solve_time
  if (lhs->solve_time != rhs->solve_time) {
    return false;
  }
  // iterations
  if (lhs->iterations != rhs->iterations) {
    return false;
  }
  // converged
  if (lhs->converged != rhs->converged) {
    return false;
  }
  // cost
  if (lhs->cost != rhs->cost) {
    return false;
  }
  // mpc_frequency
  if (lhs->mpc_frequency != rhs->mpc_frequency) {
    return false;
  }
  return true;
}

bool
wbot_msgs__msg__MpcPerformance__copy(
  const wbot_msgs__msg__MpcPerformance * input,
  wbot_msgs__msg__MpcPerformance * output)
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
  // solve_time
  output->solve_time = input->solve_time;
  // iterations
  output->iterations = input->iterations;
  // converged
  output->converged = input->converged;
  // cost
  output->cost = input->cost;
  // mpc_frequency
  output->mpc_frequency = input->mpc_frequency;
  return true;
}

wbot_msgs__msg__MpcPerformance *
wbot_msgs__msg__MpcPerformance__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__MpcPerformance * msg = (wbot_msgs__msg__MpcPerformance *)allocator.allocate(sizeof(wbot_msgs__msg__MpcPerformance), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wbot_msgs__msg__MpcPerformance));
  bool success = wbot_msgs__msg__MpcPerformance__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wbot_msgs__msg__MpcPerformance__destroy(wbot_msgs__msg__MpcPerformance * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wbot_msgs__msg__MpcPerformance__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wbot_msgs__msg__MpcPerformance__Sequence__init(wbot_msgs__msg__MpcPerformance__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__MpcPerformance * data = NULL;

  if (size) {
    data = (wbot_msgs__msg__MpcPerformance *)allocator.zero_allocate(size, sizeof(wbot_msgs__msg__MpcPerformance), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wbot_msgs__msg__MpcPerformance__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wbot_msgs__msg__MpcPerformance__fini(&data[i - 1]);
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
wbot_msgs__msg__MpcPerformance__Sequence__fini(wbot_msgs__msg__MpcPerformance__Sequence * array)
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
      wbot_msgs__msg__MpcPerformance__fini(&array->data[i]);
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

wbot_msgs__msg__MpcPerformance__Sequence *
wbot_msgs__msg__MpcPerformance__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wbot_msgs__msg__MpcPerformance__Sequence * array = (wbot_msgs__msg__MpcPerformance__Sequence *)allocator.allocate(sizeof(wbot_msgs__msg__MpcPerformance__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wbot_msgs__msg__MpcPerformance__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wbot_msgs__msg__MpcPerformance__Sequence__destroy(wbot_msgs__msg__MpcPerformance__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wbot_msgs__msg__MpcPerformance__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wbot_msgs__msg__MpcPerformance__Sequence__are_equal(const wbot_msgs__msg__MpcPerformance__Sequence * lhs, const wbot_msgs__msg__MpcPerformance__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wbot_msgs__msg__MpcPerformance__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wbot_msgs__msg__MpcPerformance__Sequence__copy(
  const wbot_msgs__msg__MpcPerformance__Sequence * input,
  wbot_msgs__msg__MpcPerformance__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wbot_msgs__msg__MpcPerformance);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wbot_msgs__msg__MpcPerformance * data =
      (wbot_msgs__msg__MpcPerformance *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wbot_msgs__msg__MpcPerformance__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wbot_msgs__msg__MpcPerformance__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wbot_msgs__msg__MpcPerformance__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
