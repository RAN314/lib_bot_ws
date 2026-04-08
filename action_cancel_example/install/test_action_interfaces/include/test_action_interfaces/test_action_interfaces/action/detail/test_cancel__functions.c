// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from test_action_interfaces:action/TestCancel.idl
// generated code does not contain a copyright notice
#include "test_action_interfaces/action/detail/test_cancel__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
test_action_interfaces__action__TestCancel_Goal__init(test_action_interfaces__action__TestCancel_Goal * msg)
{
  if (!msg) {
    return false;
  }
  // duration
  return true;
}

void
test_action_interfaces__action__TestCancel_Goal__fini(test_action_interfaces__action__TestCancel_Goal * msg)
{
  if (!msg) {
    return;
  }
  // duration
}

bool
test_action_interfaces__action__TestCancel_Goal__are_equal(const test_action_interfaces__action__TestCancel_Goal * lhs, const test_action_interfaces__action__TestCancel_Goal * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // duration
  if (lhs->duration != rhs->duration) {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Goal__copy(
  const test_action_interfaces__action__TestCancel_Goal * input,
  test_action_interfaces__action__TestCancel_Goal * output)
{
  if (!input || !output) {
    return false;
  }
  // duration
  output->duration = input->duration;
  return true;
}

test_action_interfaces__action__TestCancel_Goal *
test_action_interfaces__action__TestCancel_Goal__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Goal * msg = (test_action_interfaces__action__TestCancel_Goal *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Goal), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_Goal));
  bool success = test_action_interfaces__action__TestCancel_Goal__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_Goal__destroy(test_action_interfaces__action__TestCancel_Goal * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_Goal__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_Goal__Sequence__init(test_action_interfaces__action__TestCancel_Goal__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Goal * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_Goal *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_Goal), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_Goal__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_Goal__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_Goal__Sequence__fini(test_action_interfaces__action__TestCancel_Goal__Sequence * array)
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
      test_action_interfaces__action__TestCancel_Goal__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_Goal__Sequence *
test_action_interfaces__action__TestCancel_Goal__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Goal__Sequence * array = (test_action_interfaces__action__TestCancel_Goal__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Goal__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_Goal__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_Goal__Sequence__destroy(test_action_interfaces__action__TestCancel_Goal__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_Goal__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_Goal__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Goal__Sequence * lhs, const test_action_interfaces__action__TestCancel_Goal__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Goal__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Goal__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Goal__Sequence * input,
  test_action_interfaces__action__TestCancel_Goal__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_Goal);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_Goal * data =
      (test_action_interfaces__action__TestCancel_Goal *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_Goal__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_Goal__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Goal__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
test_action_interfaces__action__TestCancel_Result__init(test_action_interfaces__action__TestCancel_Result * msg)
{
  if (!msg) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    test_action_interfaces__action__TestCancel_Result__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_Result__fini(test_action_interfaces__action__TestCancel_Result * msg)
{
  if (!msg) {
    return;
  }
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
test_action_interfaces__action__TestCancel_Result__are_equal(const test_action_interfaces__action__TestCancel_Result * lhs, const test_action_interfaces__action__TestCancel_Result * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Result__copy(
  const test_action_interfaces__action__TestCancel_Result * input,
  test_action_interfaces__action__TestCancel_Result * output)
{
  if (!input || !output) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_Result *
test_action_interfaces__action__TestCancel_Result__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Result * msg = (test_action_interfaces__action__TestCancel_Result *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Result), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_Result));
  bool success = test_action_interfaces__action__TestCancel_Result__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_Result__destroy(test_action_interfaces__action__TestCancel_Result * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_Result__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_Result__Sequence__init(test_action_interfaces__action__TestCancel_Result__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Result * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_Result *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_Result), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_Result__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_Result__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_Result__Sequence__fini(test_action_interfaces__action__TestCancel_Result__Sequence * array)
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
      test_action_interfaces__action__TestCancel_Result__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_Result__Sequence *
test_action_interfaces__action__TestCancel_Result__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Result__Sequence * array = (test_action_interfaces__action__TestCancel_Result__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Result__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_Result__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_Result__Sequence__destroy(test_action_interfaces__action__TestCancel_Result__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_Result__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_Result__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Result__Sequence * lhs, const test_action_interfaces__action__TestCancel_Result__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Result__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Result__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Result__Sequence * input,
  test_action_interfaces__action__TestCancel_Result__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_Result);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_Result * data =
      (test_action_interfaces__action__TestCancel_Result *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_Result__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_Result__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Result__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `progress`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
test_action_interfaces__action__TestCancel_Feedback__init(test_action_interfaces__action__TestCancel_Feedback * msg)
{
  if (!msg) {
    return false;
  }
  // progress
  if (!rosidl_runtime_c__String__init(&msg->progress)) {
    test_action_interfaces__action__TestCancel_Feedback__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_Feedback__fini(test_action_interfaces__action__TestCancel_Feedback * msg)
{
  if (!msg) {
    return;
  }
  // progress
  rosidl_runtime_c__String__fini(&msg->progress);
}

bool
test_action_interfaces__action__TestCancel_Feedback__are_equal(const test_action_interfaces__action__TestCancel_Feedback * lhs, const test_action_interfaces__action__TestCancel_Feedback * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // progress
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->progress), &(rhs->progress)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Feedback__copy(
  const test_action_interfaces__action__TestCancel_Feedback * input,
  test_action_interfaces__action__TestCancel_Feedback * output)
{
  if (!input || !output) {
    return false;
  }
  // progress
  if (!rosidl_runtime_c__String__copy(
      &(input->progress), &(output->progress)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_Feedback *
test_action_interfaces__action__TestCancel_Feedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Feedback * msg = (test_action_interfaces__action__TestCancel_Feedback *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Feedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_Feedback));
  bool success = test_action_interfaces__action__TestCancel_Feedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_Feedback__destroy(test_action_interfaces__action__TestCancel_Feedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_Feedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__init(test_action_interfaces__action__TestCancel_Feedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Feedback * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_Feedback *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_Feedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_Feedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_Feedback__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_Feedback__Sequence__fini(test_action_interfaces__action__TestCancel_Feedback__Sequence * array)
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
      test_action_interfaces__action__TestCancel_Feedback__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_Feedback__Sequence *
test_action_interfaces__action__TestCancel_Feedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_Feedback__Sequence * array = (test_action_interfaces__action__TestCancel_Feedback__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_Feedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_Feedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_Feedback__Sequence__destroy(test_action_interfaces__action__TestCancel_Feedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_Feedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Feedback__Sequence * lhs, const test_action_interfaces__action__TestCancel_Feedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Feedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Feedback__Sequence * input,
  test_action_interfaces__action__TestCancel_Feedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_Feedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_Feedback * data =
      (test_action_interfaces__action__TestCancel_Feedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_Feedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_Feedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_Feedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `goal`
// already included above
// #include "test_action_interfaces/action/detail/test_cancel__functions.h"

bool
test_action_interfaces__action__TestCancel_SendGoal_Request__init(test_action_interfaces__action__TestCancel_SendGoal_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    test_action_interfaces__action__TestCancel_SendGoal_Request__fini(msg);
    return false;
  }
  // goal
  if (!test_action_interfaces__action__TestCancel_Goal__init(&msg->goal)) {
    test_action_interfaces__action__TestCancel_SendGoal_Request__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Request__fini(test_action_interfaces__action__TestCancel_SendGoal_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // goal
  test_action_interfaces__action__TestCancel_Goal__fini(&msg->goal);
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Request__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Request * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // goal
  if (!test_action_interfaces__action__TestCancel_Goal__are_equal(
      &(lhs->goal), &(rhs->goal)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Request__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Request * input,
  test_action_interfaces__action__TestCancel_SendGoal_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // goal
  if (!test_action_interfaces__action__TestCancel_Goal__copy(
      &(input->goal), &(output->goal)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_SendGoal_Request *
test_action_interfaces__action__TestCancel_SendGoal_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Request * msg = (test_action_interfaces__action__TestCancel_SendGoal_Request *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_SendGoal_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_SendGoal_Request));
  bool success = test_action_interfaces__action__TestCancel_SendGoal_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Request__destroy(test_action_interfaces__action__TestCancel_SendGoal_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_SendGoal_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__init(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Request * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_SendGoal_Request *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_SendGoal_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_SendGoal_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_SendGoal_Request__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__fini(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array)
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
      test_action_interfaces__action__TestCancel_SendGoal_Request__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence *
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array = (test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__destroy(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_SendGoal_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * input,
  test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_SendGoal_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_SendGoal_Request * data =
      (test_action_interfaces__action__TestCancel_SendGoal_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_SendGoal_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_SendGoal_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_SendGoal_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
test_action_interfaces__action__TestCancel_SendGoal_Response__init(test_action_interfaces__action__TestCancel_SendGoal_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    test_action_interfaces__action__TestCancel_SendGoal_Response__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Response__fini(test_action_interfaces__action__TestCancel_SendGoal_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Response__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Response * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Response__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Response * input,
  test_action_interfaces__action__TestCancel_SendGoal_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_SendGoal_Response *
test_action_interfaces__action__TestCancel_SendGoal_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Response * msg = (test_action_interfaces__action__TestCancel_SendGoal_Response *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_SendGoal_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_SendGoal_Response));
  bool success = test_action_interfaces__action__TestCancel_SendGoal_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Response__destroy(test_action_interfaces__action__TestCancel_SendGoal_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_SendGoal_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__init(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Response * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_SendGoal_Response *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_SendGoal_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_SendGoal_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_SendGoal_Response__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__fini(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array)
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
      test_action_interfaces__action__TestCancel_SendGoal_Response__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence *
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array = (test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__destroy(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_SendGoal_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * input,
  test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_SendGoal_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_SendGoal_Response * data =
      (test_action_interfaces__action__TestCancel_SendGoal_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_SendGoal_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_SendGoal_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_SendGoal_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"

bool
test_action_interfaces__action__TestCancel_GetResult_Request__init(test_action_interfaces__action__TestCancel_GetResult_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    test_action_interfaces__action__TestCancel_GetResult_Request__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_GetResult_Request__fini(test_action_interfaces__action__TestCancel_GetResult_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
}

bool
test_action_interfaces__action__TestCancel_GetResult_Request__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Request * lhs, const test_action_interfaces__action__TestCancel_GetResult_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_GetResult_Request__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Request * input,
  test_action_interfaces__action__TestCancel_GetResult_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_GetResult_Request *
test_action_interfaces__action__TestCancel_GetResult_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Request * msg = (test_action_interfaces__action__TestCancel_GetResult_Request *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_GetResult_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_GetResult_Request));
  bool success = test_action_interfaces__action__TestCancel_GetResult_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_GetResult_Request__destroy(test_action_interfaces__action__TestCancel_GetResult_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_GetResult_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__init(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Request * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_GetResult_Request *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_GetResult_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_GetResult_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_GetResult_Request__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__fini(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array)
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
      test_action_interfaces__action__TestCancel_GetResult_Request__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_GetResult_Request__Sequence *
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array = (test_action_interfaces__action__TestCancel_GetResult_Request__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__destroy(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * lhs, const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_GetResult_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * input,
  test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_GetResult_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_GetResult_Request * data =
      (test_action_interfaces__action__TestCancel_GetResult_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_GetResult_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_GetResult_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_GetResult_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `result`
// already included above
// #include "test_action_interfaces/action/detail/test_cancel__functions.h"

bool
test_action_interfaces__action__TestCancel_GetResult_Response__init(test_action_interfaces__action__TestCancel_GetResult_Response * msg)
{
  if (!msg) {
    return false;
  }
  // status
  // result
  if (!test_action_interfaces__action__TestCancel_Result__init(&msg->result)) {
    test_action_interfaces__action__TestCancel_GetResult_Response__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_GetResult_Response__fini(test_action_interfaces__action__TestCancel_GetResult_Response * msg)
{
  if (!msg) {
    return;
  }
  // status
  // result
  test_action_interfaces__action__TestCancel_Result__fini(&msg->result);
}

bool
test_action_interfaces__action__TestCancel_GetResult_Response__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Response * lhs, const test_action_interfaces__action__TestCancel_GetResult_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // status
  if (lhs->status != rhs->status) {
    return false;
  }
  // result
  if (!test_action_interfaces__action__TestCancel_Result__are_equal(
      &(lhs->result), &(rhs->result)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_GetResult_Response__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Response * input,
  test_action_interfaces__action__TestCancel_GetResult_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // status
  output->status = input->status;
  // result
  if (!test_action_interfaces__action__TestCancel_Result__copy(
      &(input->result), &(output->result)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_GetResult_Response *
test_action_interfaces__action__TestCancel_GetResult_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Response * msg = (test_action_interfaces__action__TestCancel_GetResult_Response *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_GetResult_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_GetResult_Response));
  bool success = test_action_interfaces__action__TestCancel_GetResult_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_GetResult_Response__destroy(test_action_interfaces__action__TestCancel_GetResult_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_GetResult_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__init(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Response * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_GetResult_Response *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_GetResult_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_GetResult_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_GetResult_Response__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__fini(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array)
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
      test_action_interfaces__action__TestCancel_GetResult_Response__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_GetResult_Response__Sequence *
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array = (test_action_interfaces__action__TestCancel_GetResult_Response__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__destroy(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * lhs, const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_GetResult_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * input,
  test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_GetResult_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_GetResult_Response * data =
      (test_action_interfaces__action__TestCancel_GetResult_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_GetResult_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_GetResult_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_GetResult_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `feedback`
// already included above
// #include "test_action_interfaces/action/detail/test_cancel__functions.h"

bool
test_action_interfaces__action__TestCancel_FeedbackMessage__init(test_action_interfaces__action__TestCancel_FeedbackMessage * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    test_action_interfaces__action__TestCancel_FeedbackMessage__fini(msg);
    return false;
  }
  // feedback
  if (!test_action_interfaces__action__TestCancel_Feedback__init(&msg->feedback)) {
    test_action_interfaces__action__TestCancel_FeedbackMessage__fini(msg);
    return false;
  }
  return true;
}

void
test_action_interfaces__action__TestCancel_FeedbackMessage__fini(test_action_interfaces__action__TestCancel_FeedbackMessage * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // feedback
  test_action_interfaces__action__TestCancel_Feedback__fini(&msg->feedback);
}

bool
test_action_interfaces__action__TestCancel_FeedbackMessage__are_equal(const test_action_interfaces__action__TestCancel_FeedbackMessage * lhs, const test_action_interfaces__action__TestCancel_FeedbackMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // feedback
  if (!test_action_interfaces__action__TestCancel_Feedback__are_equal(
      &(lhs->feedback), &(rhs->feedback)))
  {
    return false;
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_FeedbackMessage__copy(
  const test_action_interfaces__action__TestCancel_FeedbackMessage * input,
  test_action_interfaces__action__TestCancel_FeedbackMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // feedback
  if (!test_action_interfaces__action__TestCancel_Feedback__copy(
      &(input->feedback), &(output->feedback)))
  {
    return false;
  }
  return true;
}

test_action_interfaces__action__TestCancel_FeedbackMessage *
test_action_interfaces__action__TestCancel_FeedbackMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_FeedbackMessage * msg = (test_action_interfaces__action__TestCancel_FeedbackMessage *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_FeedbackMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(test_action_interfaces__action__TestCancel_FeedbackMessage));
  bool success = test_action_interfaces__action__TestCancel_FeedbackMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
test_action_interfaces__action__TestCancel_FeedbackMessage__destroy(test_action_interfaces__action__TestCancel_FeedbackMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    test_action_interfaces__action__TestCancel_FeedbackMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__init(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_FeedbackMessage * data = NULL;

  if (size) {
    data = (test_action_interfaces__action__TestCancel_FeedbackMessage *)allocator.zero_allocate(size, sizeof(test_action_interfaces__action__TestCancel_FeedbackMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = test_action_interfaces__action__TestCancel_FeedbackMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        test_action_interfaces__action__TestCancel_FeedbackMessage__fini(&data[i - 1]);
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
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__fini(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array)
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
      test_action_interfaces__action__TestCancel_FeedbackMessage__fini(&array->data[i]);
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

test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence *
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array = (test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence *)allocator.allocate(sizeof(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__destroy(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__are_equal(const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * lhs, const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_FeedbackMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__copy(
  const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * input,
  test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(test_action_interfaces__action__TestCancel_FeedbackMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    test_action_interfaces__action__TestCancel_FeedbackMessage * data =
      (test_action_interfaces__action__TestCancel_FeedbackMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!test_action_interfaces__action__TestCancel_FeedbackMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          test_action_interfaces__action__TestCancel_FeedbackMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!test_action_interfaces__action__TestCancel_FeedbackMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
