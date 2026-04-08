// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from test_action_interfaces:action/TestCancel.idl
// generated code does not contain a copyright notice

#ifndef TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__FUNCTIONS_H_
#define TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "test_action_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "test_action_interfaces/action/detail/test_cancel__struct.h"

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_Goal
 * )) before or use
 * test_action_interfaces__action__TestCancel_Goal__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__init(test_action_interfaces__action__TestCancel_Goal * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Goal__fini(test_action_interfaces__action__TestCancel_Goal * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_Goal__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Goal *
test_action_interfaces__action__TestCancel_Goal__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Goal__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Goal__destroy(test_action_interfaces__action__TestCancel_Goal * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__are_equal(const test_action_interfaces__action__TestCancel_Goal * lhs, const test_action_interfaces__action__TestCancel_Goal * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__copy(
  const test_action_interfaces__action__TestCancel_Goal * input,
  test_action_interfaces__action__TestCancel_Goal * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_Goal__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__Sequence__init(test_action_interfaces__action__TestCancel_Goal__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Goal__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Goal__Sequence__fini(test_action_interfaces__action__TestCancel_Goal__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_Goal__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Goal__Sequence *
test_action_interfaces__action__TestCancel_Goal__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Goal__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Goal__Sequence__destroy(test_action_interfaces__action__TestCancel_Goal__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Goal__Sequence * lhs, const test_action_interfaces__action__TestCancel_Goal__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Goal__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Goal__Sequence * input,
  test_action_interfaces__action__TestCancel_Goal__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_Result
 * )) before or use
 * test_action_interfaces__action__TestCancel_Result__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__init(test_action_interfaces__action__TestCancel_Result * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Result__fini(test_action_interfaces__action__TestCancel_Result * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_Result__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Result *
test_action_interfaces__action__TestCancel_Result__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Result__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Result__destroy(test_action_interfaces__action__TestCancel_Result * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__are_equal(const test_action_interfaces__action__TestCancel_Result * lhs, const test_action_interfaces__action__TestCancel_Result * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__copy(
  const test_action_interfaces__action__TestCancel_Result * input,
  test_action_interfaces__action__TestCancel_Result * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_Result__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__Sequence__init(test_action_interfaces__action__TestCancel_Result__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Result__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Result__Sequence__fini(test_action_interfaces__action__TestCancel_Result__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_Result__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Result__Sequence *
test_action_interfaces__action__TestCancel_Result__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Result__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Result__Sequence__destroy(test_action_interfaces__action__TestCancel_Result__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Result__Sequence * lhs, const test_action_interfaces__action__TestCancel_Result__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Result__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Result__Sequence * input,
  test_action_interfaces__action__TestCancel_Result__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_Feedback
 * )) before or use
 * test_action_interfaces__action__TestCancel_Feedback__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__init(test_action_interfaces__action__TestCancel_Feedback * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Feedback__fini(test_action_interfaces__action__TestCancel_Feedback * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_Feedback__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Feedback *
test_action_interfaces__action__TestCancel_Feedback__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Feedback__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Feedback__destroy(test_action_interfaces__action__TestCancel_Feedback * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__are_equal(const test_action_interfaces__action__TestCancel_Feedback * lhs, const test_action_interfaces__action__TestCancel_Feedback * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__copy(
  const test_action_interfaces__action__TestCancel_Feedback * input,
  test_action_interfaces__action__TestCancel_Feedback * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_Feedback__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__init(test_action_interfaces__action__TestCancel_Feedback__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Feedback__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Feedback__Sequence__fini(test_action_interfaces__action__TestCancel_Feedback__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_Feedback__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_Feedback__Sequence *
test_action_interfaces__action__TestCancel_Feedback__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_Feedback__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_Feedback__Sequence__destroy(test_action_interfaces__action__TestCancel_Feedback__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__are_equal(const test_action_interfaces__action__TestCancel_Feedback__Sequence * lhs, const test_action_interfaces__action__TestCancel_Feedback__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_Feedback__Sequence__copy(
  const test_action_interfaces__action__TestCancel_Feedback__Sequence * input,
  test_action_interfaces__action__TestCancel_Feedback__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_SendGoal_Request
 * )) before or use
 * test_action_interfaces__action__TestCancel_SendGoal_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__init(test_action_interfaces__action__TestCancel_SendGoal_Request * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Request__fini(test_action_interfaces__action__TestCancel_SendGoal_Request * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_SendGoal_Request *
test_action_interfaces__action__TestCancel_SendGoal_Request__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Request__destroy(test_action_interfaces__action__TestCancel_SendGoal_Request * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Request * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Request * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Request * input,
  test_action_interfaces__action__TestCancel_SendGoal_Request * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__init(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__fini(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence *
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__destroy(test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * input,
  test_action_interfaces__action__TestCancel_SendGoal_Request__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_SendGoal_Response
 * )) before or use
 * test_action_interfaces__action__TestCancel_SendGoal_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__init(test_action_interfaces__action__TestCancel_SendGoal_Response * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Response__fini(test_action_interfaces__action__TestCancel_SendGoal_Response * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_SendGoal_Response *
test_action_interfaces__action__TestCancel_SendGoal_Response__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Response__destroy(test_action_interfaces__action__TestCancel_SendGoal_Response * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Response * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Response * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Response * input,
  test_action_interfaces__action__TestCancel_SendGoal_Response * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__init(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__fini(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence *
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__destroy(test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__are_equal(const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * lhs, const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence__copy(
  const test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * input,
  test_action_interfaces__action__TestCancel_SendGoal_Response__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_GetResult_Request
 * )) before or use
 * test_action_interfaces__action__TestCancel_GetResult_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__init(test_action_interfaces__action__TestCancel_GetResult_Request * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Request__fini(test_action_interfaces__action__TestCancel_GetResult_Request * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_GetResult_Request *
test_action_interfaces__action__TestCancel_GetResult_Request__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Request__destroy(test_action_interfaces__action__TestCancel_GetResult_Request * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Request * lhs, const test_action_interfaces__action__TestCancel_GetResult_Request * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Request * input,
  test_action_interfaces__action__TestCancel_GetResult_Request * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__init(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__fini(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence *
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__destroy(test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * lhs, const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Request__Sequence__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * input,
  test_action_interfaces__action__TestCancel_GetResult_Request__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_GetResult_Response
 * )) before or use
 * test_action_interfaces__action__TestCancel_GetResult_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__init(test_action_interfaces__action__TestCancel_GetResult_Response * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Response__fini(test_action_interfaces__action__TestCancel_GetResult_Response * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_GetResult_Response *
test_action_interfaces__action__TestCancel_GetResult_Response__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Response__destroy(test_action_interfaces__action__TestCancel_GetResult_Response * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Response * lhs, const test_action_interfaces__action__TestCancel_GetResult_Response * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Response * input,
  test_action_interfaces__action__TestCancel_GetResult_Response * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__init(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__fini(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence *
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__destroy(test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__are_equal(const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * lhs, const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_GetResult_Response__Sequence__copy(
  const test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * input,
  test_action_interfaces__action__TestCancel_GetResult_Response__Sequence * output);

/// Initialize action/TestCancel message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_action_interfaces__action__TestCancel_FeedbackMessage
 * )) before or use
 * test_action_interfaces__action__TestCancel_FeedbackMessage__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__init(test_action_interfaces__action__TestCancel_FeedbackMessage * msg);

/// Finalize action/TestCancel message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_FeedbackMessage__fini(test_action_interfaces__action__TestCancel_FeedbackMessage * msg);

/// Create action/TestCancel message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_FeedbackMessage *
test_action_interfaces__action__TestCancel_FeedbackMessage__create();

/// Destroy action/TestCancel message.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_FeedbackMessage__destroy(test_action_interfaces__action__TestCancel_FeedbackMessage * msg);

/// Check for action/TestCancel message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__are_equal(const test_action_interfaces__action__TestCancel_FeedbackMessage * lhs, const test_action_interfaces__action__TestCancel_FeedbackMessage * rhs);

/// Copy a action/TestCancel message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__copy(
  const test_action_interfaces__action__TestCancel_FeedbackMessage * input,
  test_action_interfaces__action__TestCancel_FeedbackMessage * output);

/// Initialize array of action/TestCancel messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__init(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array, size_t size);

/// Finalize array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__fini(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array);

/// Create array of action/TestCancel messages.
/**
 * It allocates the memory for the array and calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence *
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__create(size_t size);

/// Destroy array of action/TestCancel messages.
/**
 * It calls
 * test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
void
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__destroy(test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * array);

/// Check for action/TestCancel message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__are_equal(const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * lhs, const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * rhs);

/// Copy an array of action/TestCancel messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_action_interfaces
bool
test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence__copy(
  const test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * input,
  test_action_interfaces__action__TestCancel_FeedbackMessage__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__FUNCTIONS_H_
