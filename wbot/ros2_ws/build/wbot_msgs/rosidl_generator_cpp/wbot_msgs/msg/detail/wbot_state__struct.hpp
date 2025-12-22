// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wbot_msgs:msg/WbotState.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_HPP_
#define WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__wbot_msgs__msg__WbotState __attribute__((deprecated))
#else
# define DEPRECATED__wbot_msgs__msg__WbotState __declspec(deprecated)
#endif

namespace wbot_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct WbotState_
{
  using Type = WbotState_<ContainerAllocator>;

  explicit WbotState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->time = 0.0;
      this->mode = 0;
    }
  }

  explicit WbotState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->time = 0.0;
      this->mode = 0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _time_type =
    double;
  _time_type time;
  using _state_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _state_type state;
  using _mode_type =
    int8_t;
  _mode_type mode;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__time(
    const double & _arg)
  {
    this->time = _arg;
    return *this;
  }
  Type & set__state(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->state = _arg;
    return *this;
  }
  Type & set__mode(
    const int8_t & _arg)
  {
    this->mode = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wbot_msgs::msg::WbotState_<ContainerAllocator> *;
  using ConstRawPtr =
    const wbot_msgs::msg::WbotState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::WbotState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::WbotState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wbot_msgs__msg__WbotState
    std::shared_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wbot_msgs__msg__WbotState
    std::shared_ptr<wbot_msgs::msg::WbotState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const WbotState_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->time != other.time) {
      return false;
    }
    if (this->state != other.state) {
      return false;
    }
    if (this->mode != other.mode) {
      return false;
    }
    return true;
  }
  bool operator!=(const WbotState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct WbotState_

// alias to use template instance with default allocator
using WbotState =
  wbot_msgs::msg::WbotState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_STATE__STRUCT_HPP_
