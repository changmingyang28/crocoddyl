// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wbot_msgs:msg/WbotState.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_STATE__TRAITS_HPP_
#define WBOT_MSGS__MSG__DETAIL__WBOT_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wbot_msgs/msg/detail/wbot_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace wbot_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const WbotState & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: time
  {
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << ", ";
  }

  // member: state
  {
    if (msg.state.size() == 0) {
      out << "state: []";
    } else {
      out << "state: [";
      size_t pending_items = msg.state.size();
      for (auto item : msg.state) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const WbotState & msg,
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

  // member: time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time: ";
    rosidl_generator_traits::value_to_yaml(msg.time, out);
    out << "\n";
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.state.size() == 0) {
      out << "state: []\n";
    } else {
      out << "state:\n";
      for (auto item : msg.state) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const WbotState & msg, bool use_flow_style = false)
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
  const wbot_msgs::msg::WbotState & msg,
  std::ostream & out, size_t indentation = 0)
{
  wbot_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wbot_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const wbot_msgs::msg::WbotState & msg)
{
  return wbot_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wbot_msgs::msg::WbotState>()
{
  return "wbot_msgs::msg::WbotState";
}

template<>
inline const char * name<wbot_msgs::msg::WbotState>()
{
  return "wbot_msgs/msg/WbotState";
}

template<>
struct has_fixed_size<wbot_msgs::msg::WbotState>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<wbot_msgs::msg::WbotState>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<wbot_msgs::msg::WbotState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_STATE__TRAITS_HPP_
