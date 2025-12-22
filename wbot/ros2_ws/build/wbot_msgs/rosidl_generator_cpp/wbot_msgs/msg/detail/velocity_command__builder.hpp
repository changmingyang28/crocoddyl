// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wbot_msgs:msg/VelocityCommand.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__BUILDER_HPP_
#define WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wbot_msgs/msg/detail/velocity_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wbot_msgs
{

namespace msg
{

namespace builder
{

class Init_VelocityCommand_target_joint_angles
{
public:
  explicit Init_VelocityCommand_target_joint_angles(::wbot_msgs::msg::VelocityCommand & msg)
  : msg_(msg)
  {}
  ::wbot_msgs::msg::VelocityCommand target_joint_angles(::wbot_msgs::msg::VelocityCommand::_target_joint_angles_type arg)
  {
    msg_.target_joint_angles = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wbot_msgs::msg::VelocityCommand msg_;
};

class Init_VelocityCommand_omega_z
{
public:
  explicit Init_VelocityCommand_omega_z(::wbot_msgs::msg::VelocityCommand & msg)
  : msg_(msg)
  {}
  Init_VelocityCommand_target_joint_angles omega_z(::wbot_msgs::msg::VelocityCommand::_omega_z_type arg)
  {
    msg_.omega_z = std::move(arg);
    return Init_VelocityCommand_target_joint_angles(msg_);
  }

private:
  ::wbot_msgs::msg::VelocityCommand msg_;
};

class Init_VelocityCommand_vx
{
public:
  explicit Init_VelocityCommand_vx(::wbot_msgs::msg::VelocityCommand & msg)
  : msg_(msg)
  {}
  Init_VelocityCommand_omega_z vx(::wbot_msgs::msg::VelocityCommand::_vx_type arg)
  {
    msg_.vx = std::move(arg);
    return Init_VelocityCommand_omega_z(msg_);
  }

private:
  ::wbot_msgs::msg::VelocityCommand msg_;
};

class Init_VelocityCommand_header
{
public:
  Init_VelocityCommand_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_VelocityCommand_vx header(::wbot_msgs::msg::VelocityCommand::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_VelocityCommand_vx(msg_);
  }

private:
  ::wbot_msgs::msg::VelocityCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wbot_msgs::msg::VelocityCommand>()
{
  return wbot_msgs::msg::builder::Init_VelocityCommand_header();
}

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__BUILDER_HPP_
