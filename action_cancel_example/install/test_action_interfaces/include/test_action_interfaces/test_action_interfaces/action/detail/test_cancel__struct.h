// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from test_action_interfaces:action/TestCancel.idl
// generated code does not contain a copyright notice

#ifndef TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__STRUCT_H_
#define TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_Goal
{
  int32_t duration;
} test_action_interfaces__action__TestCancel_Goal;

// Struct for a sequence of test_action_interfaces__action__TestCancel_Goal.
typedef struct test_action_interfaces__action__TestCancel_Goal__Sequence
{
  test_action_interfaces__action__TestCancel_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_Result
{
  rosidl_runtime_c__String message;
} test_action_interfaces__action__TestCancel_Result;

// Struct for a sequence of test_action_interfaces__action__TestCancel_Result.
typedef struct test_action_interfaces__action__TestCancel_Result__Sequence
{
  test_action_interfaces__action__TestCancel_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'progress'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_Feedback
{
  rosidl_runtime_c__String progress;
} test_action_interfaces__action__TestCancel_Feedback;

// Struct for a sequence of test_action_interfaces__action__TestCancel_Feedback.
typedef struct test_action_interfaces__action__TestCancel_Feedback__Sequence
{
  test_action_interfaces__action__TestCancel_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "test_action_interfaces/action/detail/test_cancel__struct.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  test_action_interfaces__action__TestCancel_Goal goal;
} test_action_interfaces__action__TestCancel_SendGoal_Request;

// Struct for a sequence of test_action_interfaces__action__TestCancel_SendGoal_Request.
typedef struct test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence
{
  test_action_interfaces__action__TestCancel_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} test_action_interfaces__action__TestCancel_SendGoal_Response;

// Struct for a sequence of test_action_interfaces__action__TestCancel_SendGoal_Response.
typedef struct test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence
{
  test_action_interfaces__action__TestCancel_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} test_action_interfaces__action__TestCancel_GetResult_Request;

// Struct for a sequence of test_action_interfaces__action__TestCancel_GetResult_Request.
typedef struct test_action_interfaces__action__TestCancel_GetResult_Request__Sequence
{
  test_action_interfaces__action__TestCancel_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "test_action_interfaces/action/detail/test_cancel__struct.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_GetResult_Response
{
  int8_t status;
  test_action_interfaces__action__TestCancel_Result result;
} test_action_interfaces__action__TestCancel_GetResult_Response;

// Struct for a sequence of test_action_interfaces__action__TestCancel_GetResult_Response.
typedef struct test_action_interfaces__action__TestCancel_GetResult_Response__Sequence
{
  test_action_interfaces__action__TestCancel_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "test_action_interfaces/action/detail/test_cancel__struct.h"

/// Struct defined in action/TestCancel in the package test_action_interfaces.
typedef struct test_action_interfaces__action__TestCancel_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  test_action_interfaces__action__TestCancel_Feedback feedback;
} test_action_interfaces__action__TestCancel_FeedbackMessage;

// Struct for a sequence of test_action_interfaces__action__TestCancel_FeedbackMessage.
typedef struct test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence
{
  test_action_interfaces__action__TestCancel_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__STRUCT_H_
