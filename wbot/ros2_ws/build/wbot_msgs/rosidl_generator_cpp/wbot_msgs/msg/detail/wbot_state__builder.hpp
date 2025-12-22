// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wbot_msgs:msg/WbotState.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_STATE__BUILDER_HPP_
#define WBOT_MSGS__MSG__DETAIL__WBOT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wbot_msgs/msg/detail/wbot_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wbot_msgs
{

namespace msg
{

namespace builder
{

class Init_WbotState_mode
{
public:
  explicit Init_WbotState_mode(::wbot_msgs::msg::WbotState & msg)
  : msg_(msg)
  {}
  ::wbot_msgs::msg::WbotState mode(::wbot_msgs::msg::WbotState::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wbot_msgs::msg::WbotState msg_;
};

class Init_WbotState_state
{
public:
  explicit Init_WbotState_state(::wbot_msgs::msg::WbotState & msg)
  : msg_(msg)
  {}
  Init_WbotState_mode state(::wbot_msgs::msg::WbotState::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_WbotState_mode(msg_);
  }

private:
  ::wbot_msgs::msg::WbotState msg_;
};

class Init_WbotState_time
{
public:
  explicit Init_WbotState_time(::wbot_msgs::msg::WbotState & msg)
  : msg_(msg)
  {}
  Init_WbotState_state time(::wbot_msgs::msg::WbotState::_time_type arg)
  {
    msg_.time = std::move(arg);
    return Init_WbotState_state(msg_);
  }

private:
  ::wbot_msgs::msg::WbotState msg_;
};

class Init_WbotState_header
{
public:
  Init_WbotState_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_WbotState_time header(::wbot_msgs::msg::WbotState::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_WbotState_time(msg_);
  }

private:
  ::wbot_msgs::msg::WbotState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wbot_msgs::msg::WbotState>()
{
  return wbot_msgs::msg::builder::Init_WbotState_header();
}

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_STATE__BUILDER_HPP_
