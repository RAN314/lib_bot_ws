// generated from rosidl_generator_cpp/resource/rosidl_generator_cpp__visibility_control.hpp.in
// generated code does not contain a copyright notice

#ifndef TEST_ACTION_CANCEL__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_
#define TEST_ACTION_CANCEL__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_

#ifdef __cplusplus
extern "C"
{
#endif

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define ROSIDL_GENERATOR_CPP_EXPORT_test_action_cancel __attribute__ ((dllexport))
    #define ROSIDL_GENERATOR_CPP_IMPORT_test_action_cancel __attribute__ ((dllimport))
  #else
    #define ROSIDL_GENERATOR_CPP_EXPORT_test_action_cancel __declspec(dllexport)
    #define ROSIDL_GENERATOR_CPP_IMPORT_test_action_cancel __declspec(dllimport)
  #endif
  #ifdef ROSIDL_GENERATOR_CPP_BUILDING_DLL_test_action_cancel
    #define ROSIDL_GENERATOR_CPP_PUBLIC_test_action_cancel ROSIDL_GENERATOR_CPP_EXPORT_test_action_cancel
  #else
    #define ROSIDL_GENERATOR_CPP_PUBLIC_test_action_cancel ROSIDL_GENERATOR_CPP_IMPORT_test_action_cancel
  #endif
#else
  #define ROSIDL_GENERATOR_CPP_EXPORT_test_action_cancel __attribute__ ((visibility("default")))
  #define ROSIDL_GENERATOR_CPP_IMPORT_test_action_cancel
  #if __GNUC__ >= 4
    #define ROSIDL_GENERATOR_CPP_PUBLIC_test_action_cancel __attribute__ ((visibility("default")))
  #else
    #define ROSIDL_GENERATOR_CPP_PUBLIC_test_action_cancel
  #endif
#endif

#ifdef __cplusplus
}
#endif

#endif  // TEST_ACTION_CANCEL__MSG__ROSIDL_GENERATOR_CPP__VISIBILITY_CONTROL_HPP_
