// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from test_action_interfaces:action/TestCancel.idl
// generated code does not contain a copyright notice

#ifndef TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__BUILDER_HPP_
#define TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "test_action_interfaces/action/detail/test_cancel__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_Goal_duration
{
public:
  Init_TestCancel_Goal_duration()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::test_action_interfaces::action::TestCancel_Goal duration(::test_action_interfaces::action::TestCancel_Goal::_duration_type arg)
  {
    msg_.duration = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_Goal>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_Goal_duration();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_Result_message
{
public:
  Init_TestCancel_Result_message()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::test_action_interfaces::action::TestCancel_Result message(::test_action_interfaces::action::TestCancel_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_Result>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_Result_message();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_Feedback_progress
{
public:
  Init_TestCancel_Feedback_progress()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::test_action_interfaces::action::TestCancel_Feedback progress(::test_action_interfaces::action::TestCancel_Feedback::_progress_type arg)
  {
    msg_.progress = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_Feedback>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_Feedback_progress();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_SendGoal_Request_goal
{
public:
  explicit Init_TestCancel_SendGoal_Request_goal(::test_action_interfaces::action::TestCancel_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::test_action_interfaces::action::TestCancel_SendGoal_Request goal(::test_action_interfaces::action::TestCancel_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_SendGoal_Request msg_;
};

class Init_TestCancel_SendGoal_Request_goal_id
{
public:
  Init_TestCancel_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TestCancel_SendGoal_Request_goal goal_id(::test_action_interfaces::action::TestCancel_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_TestCancel_SendGoal_Request_goal(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_SendGoal_Request>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_SendGoal_Request_goal_id();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_SendGoal_Response_stamp
{
public:
  explicit Init_TestCancel_SendGoal_Response_stamp(::test_action_interfaces::action::TestCancel_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::test_action_interfaces::action::TestCancel_SendGoal_Response stamp(::test_action_interfaces::action::TestCancel_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_SendGoal_Response msg_;
};

class Init_TestCancel_SendGoal_Response_accepted
{
public:
  Init_TestCancel_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TestCancel_SendGoal_Response_stamp accepted(::test_action_interfaces::action::TestCancel_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_TestCancel_SendGoal_Response_stamp(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_SendGoal_Response>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_SendGoal_Response_accepted();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_GetResult_Request_goal_id
{
public:
  Init_TestCancel_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::test_action_interfaces::action::TestCancel_GetResult_Request goal_id(::test_action_interfaces::action::TestCancel_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_GetResult_Request>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_GetResult_Request_goal_id();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_GetResult_Response_result
{
public:
  explicit Init_TestCancel_GetResult_Response_result(::test_action_interfaces::action::TestCancel_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::test_action_interfaces::action::TestCancel_GetResult_Response result(::test_action_interfaces::action::TestCancel_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_GetResult_Response msg_;
};

class Init_TestCancel_GetResult_Response_status
{
public:
  Init_TestCancel_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TestCancel_GetResult_Response_result status(::test_action_interfaces::action::TestCancel_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_TestCancel_GetResult_Response_result(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_GetResult_Response>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_GetResult_Response_status();
}

}  // namespace test_action_interfaces


namespace test_action_interfaces
{

namespace action
{

namespace builder
{

class Init_TestCancel_FeedbackMessage_feedback
{
public:
  explicit Init_TestCancel_FeedbackMessage_feedback(::test_action_interfaces::action::TestCancel_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::test_action_interfaces::action::TestCancel_FeedbackMessage feedback(::test_action_interfaces::action::TestCancel_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_FeedbackMessage msg_;
};

class Init_TestCancel_FeedbackMessage_goal_id
{
public:
  Init_TestCancel_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TestCancel_FeedbackMessage_feedback goal_id(::test_action_interfaces::action::TestCancel_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_TestCancel_FeedbackMessage_feedback(msg_);
  }

private:
  ::test_action_interfaces::action::TestCancel_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_action_interfaces::action::TestCancel_FeedbackMessage>()
{
  return test_action_interfaces::action::builder::Init_TestCancel_FeedbackMessage_goal_id();
}

}  // namespace test_action_interfaces

#endif  // TEST_ACTION_INTERFACES__ACTION__DETAIL__TEST_CANCEL__BUILDER_HPP_
