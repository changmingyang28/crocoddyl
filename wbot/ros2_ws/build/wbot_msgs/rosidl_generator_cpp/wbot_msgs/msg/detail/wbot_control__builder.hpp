// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wbot_msgs:msg/WbotControl.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__BUILDER_HPP_
#define WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wbot_msgs/msg/detail/wbot_control__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wbot_msgs
{

namespace msg
{

namespace builder
{

class Init_WbotControl_valid
{
public:
  explicit Init_WbotControl_valid(::wbot_msgs::msg::WbotControl & msg)
  : msg_(msg)
  {}
  ::wbot_msgs::msg::WbotControl valid(::wbot_msgs::msg::WbotControl::_valid_type arg)
  {
    msg_.valid = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wbot_msgs::msg::WbotControl msg_;
};

class Init_WbotControl_control
{
public:
  explicit Init_WbotControl_control(::wbot_msgs::msg::WbotControl & msg)
  : msg_(msg)
  {}
  Init_WbotControl_valid control(::wbot_msgs::msg::WbotControl::_control_type arg)
  {
    msg_.control = std::move(arg);
    return Init_WbotControl_valid(msg_);
  }

private:
  ::wbot_msgs::msg::WbotControl msg_;
};

class Init_WbotControl_time
{
public:
  explicit Init_WbotControl_time(::wbot_msgs::msg::WbotControl & msg)
  : msg_(msg)
  {}
  Init_WbotControl_control time(::wbot_msgs::msg::WbotControl::_time_type arg)
  {
    msg_.time = std::move(arg);
    return Init_WbotControl_control(msg_);
  }

private:
  ::wbot_msgs::msg::WbotControl msg_;
};

class Init_WbotControl_header
{
public:
  Init_WbotControl_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_WbotControl_time header(::wbot_msgs::msg::WbotControl::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_WbotControl_time(msg_);
  }

private:
  ::wbot_msgs::msg::WbotControl msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wbot_msgs::msg::WbotControl>()
{
  return wbot_msgs::msg::builder::Init_WbotControl_header();
}

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__BUILDER_HPP_
