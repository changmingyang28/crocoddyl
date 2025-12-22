// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wbot_msgs:msg/VelocityCommand.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_HPP_
#define WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_HPP_

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
# define DEPRECATED__wbot_msgs__msg__VelocityCommand __attribute__((deprecated))
#else
# define DEPRECATED__wbot_msgs__msg__VelocityCommand __declspec(deprecated)
#endif

namespace wbot_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct VelocityCommand_
{
  using Type = VelocityCommand_<ContainerAllocator>;

  explicit VelocityCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->omega_z = 0.0;
    }
  }

  explicit VelocityCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->omega_z = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _vx_type =
    double;
  _vx_type vx;
  using _omega_z_type =
    double;
  _omega_z_type omega_z;
  using _target_joint_angles_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _target_joint_angles_type target_joint_angles;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__vx(
    const double & _arg)
  {
    this->vx = _arg;
    return *this;
  }
  Type & set__omega_z(
    const double & _arg)
  {
    this->omega_z = _arg;
    return *this;
  }
  Type & set__target_joint_angles(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->target_joint_angles = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wbot_msgs::msg::VelocityCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const wbot_msgs::msg::VelocityCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::VelocityCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::VelocityCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wbot_msgs__msg__VelocityCommand
    std::shared_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wbot_msgs__msg__VelocityCommand
    std::shared_ptr<wbot_msgs::msg::VelocityCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const VelocityCommand_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->vx != other.vx) {
      return false;
    }
    if (this->omega_z != other.omega_z) {
      return false;
    }
    if (this->target_joint_angles != other.target_joint_angles) {
      return false;
    }
    return true;
  }
  bool operator!=(const VelocityCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct VelocityCommand_

// alias to use template instance with default allocator
using VelocityCommand =
  wbot_msgs::msg::VelocityCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__VELOCITY_COMMAND__STRUCT_HPP_
