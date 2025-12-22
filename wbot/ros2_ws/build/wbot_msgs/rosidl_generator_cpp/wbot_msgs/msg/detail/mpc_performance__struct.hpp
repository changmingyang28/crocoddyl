// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_HPP_
#define WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_HPP_

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
# define DEPRECATED__wbot_msgs__msg__MpcPerformance __attribute__((deprecated))
#else
# define DEPRECATED__wbot_msgs__msg__MpcPerformance __declspec(deprecated)
#endif

namespace wbot_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MpcPerformance_
{
  using Type = MpcPerformance_<ContainerAllocator>;

  explicit MpcPerformance_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->solve_time = 0.0;
      this->iterations = 0l;
      this->converged = false;
      this->cost = 0.0;
      this->mpc_frequency = 0.0;
    }
  }

  explicit MpcPerformance_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->solve_time = 0.0;
      this->iterations = 0l;
      this->converged = false;
      this->cost = 0.0;
      this->mpc_frequency = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _solve_time_type =
    double;
  _solve_time_type solve_time;
  using _iterations_type =
    int32_t;
  _iterations_type iterations;
  using _converged_type =
    bool;
  _converged_type converged;
  using _cost_type =
    double;
  _cost_type cost;
  using _mpc_frequency_type =
    double;
  _mpc_frequency_type mpc_frequency;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__solve_time(
    const double & _arg)
  {
    this->solve_time = _arg;
    return *this;
  }
  Type & set__iterations(
    const int32_t & _arg)
  {
    this->iterations = _arg;
    return *this;
  }
  Type & set__converged(
    const bool & _arg)
  {
    this->converged = _arg;
    return *this;
  }
  Type & set__cost(
    const double & _arg)
  {
    this->cost = _arg;
    return *this;
  }
  Type & set__mpc_frequency(
    const double & _arg)
  {
    this->mpc_frequency = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wbot_msgs::msg::MpcPerformance_<ContainerAllocator> *;
  using ConstRawPtr =
    const wbot_msgs::msg::MpcPerformance_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::MpcPerformance_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wbot_msgs::msg::MpcPerformance_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wbot_msgs__msg__MpcPerformance
    std::shared_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wbot_msgs__msg__MpcPerformance
    std::shared_ptr<wbot_msgs::msg::MpcPerformance_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MpcPerformance_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->solve_time != other.solve_time) {
      return false;
    }
    if (this->iterations != other.iterations) {
      return false;
    }
    if (this->converged != other.converged) {
      return false;
    }
    if (this->cost != other.cost) {
      return false;
    }
    if (this->mpc_frequency != other.mpc_frequency) {
      return false;
    }
    return true;
  }
  bool operator!=(const MpcPerformance_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MpcPerformance_

// alias to use template instance with default allocator
using MpcPerformance =
  wbot_msgs::msg::MpcPerformance_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__STRUCT_HPP_
