// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wbot_msgs:msg/WbotControl.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_HPP_
#define WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_HPP_

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
# define DEPRECATED__wbot_msgs__msg__WbotControl __attribute__((deprecated))
#else
# define DEPRECATED__wbot_msgs__msg__WbotControl __declspec(deprecated)
#endif

namespace wbot_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct WbotControl_
{
  using Type = WbotControl_<ContainerAllocator>;

  explicit WbotControl_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->time = 0.0;
      this->valid = false;
    }
  }

  explicit WbotControl_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->time = 0.0;
      this->valid = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _time_type =
    double;
  _time_type time;
  using _control_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _control_type control;
  using _valid_type =
    bool;
  _valid_type valid;

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
  Type & set__control(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->control = _arg;
    return *this;
  }
  Type & set__valid(
    const bool & _arg)
  {
    this->valid = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wbot_msgs::msg::WbotControl_<ContainerAllocator> *;
  using ConstRawPtr =
    const wbot_msgs::msg::WbotControl_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::WbotControl_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::WbotControl_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wbot_msgs__msg__WbotControl
    std::shared_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wbot_msgs__msg__WbotControl
    std::shared_ptr<wbot_msgs::msg::WbotControl_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const WbotControl_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->time != other.time) {
      return false;
    }
    if (this->control != other.control) {
      return false;
    }
    if (this->valid != other.valid) {
      return false;
    }
    return true;
  }
  bool operator!=(const WbotControl_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct WbotControl_

// alias to use template instance with default allocator
using WbotControl =
  wbot_msgs::msg::WbotControl_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__WBOT_CONTROL__STRUCT_HPP_
