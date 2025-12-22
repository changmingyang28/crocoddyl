// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wbot_msgs:msg/VelocityCommand.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__TRAITS_HPP_
#define WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wbot_msgs/msg/detail/velocity_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace wbot_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const VelocityCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: vx
  {
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << ", ";
  }

  // member: omega_z
  {
    out << "omega_z: ";
    rosidl_generator_traits::value_to_yaml(msg.omega_z, out);
    out << ", ";
  }

  // member: target_joint_angles
  {
    if (msg.target_joint_angles.size() == 0) {
      out << "target_joint_angles: []";
    } else {
      out << "target_joint_angles: [";
      size_t pending_items = msg.target_joint_angles.size();
      for (auto item : msg.target_joint_angles) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const VelocityCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: vx
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << "\n";
  }

  // member: omega_z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "omega_z: ";
    rosidl_generator_traits::value_to_yaml(msg.omega_z, out);
    out << "\n";
  }

  // member: target_joint_angles
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.target_joint_angles.size() == 0) {
      out << "target_joint_angles: []\n";
    } else {
      out << "target_joint_angles:\n";
      for (auto item : msg.target_joint_angles) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const VelocityCommand & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace wbot_msgs

namespace rosidl_generator_traits
{

[[deprecated("use wbot_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const wbot_msgs::msg::VelocityCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  wbot_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wbot_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const wbot_msgs::msg::VelocityCommand & msg)
{
  return wbot_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wbot_msgs::msg::VelocityCommand>()
{
  return "wbot_msgs::msg::VelocityCommand";
}

template<>
inline const char * name<wbot_msgs::msg::VelocityCommand>()
{
  return "wbot_msgs/msg/VelocityCommand";
}

template<>
struct has_fixed_size<wbot_msgs::msg::VelocityCommand>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<wbot_msgs::msg::VelocityCommand>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<wbot_msgs::msg::VelocityCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__TRAITS_HPP_
