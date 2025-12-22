// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice

#ifndef WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__BUILDER_HPP_
#define WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wbot_msgs/msg/detail/mpc_performance__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wbot_msgs
{

namespace msg
{

namespace builder
{

class Init_MpcPerformance_mpc_frequency
{
public:
  explicit Init_MpcPerformance_mpc_frequency(::wbot_msgs::msg::MpcPerformance & msg)
  : msg_(msg)
  {}
  ::wbot_msgs::msg::MpcPerformance mpc_frequency(::wbot_msgs::msg::MpcPerformance::_mpc_frequency_type arg)
  {
    msg_.mpc_frequency = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

class Init_MpcPerformance_cost
{
public:
  explicit Init_MpcPerformance_cost(::wbot_msgs::msg::MpcPerformance & msg)
  : msg_(msg)
  {}
  Init_MpcPerformance_mpc_frequency cost(::wbot_msgs::msg::MpcPerformance::_cost_type arg)
  {
    msg_.cost = std::move(arg);
    return Init_MpcPerformance_mpc_frequency(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

class Init_MpcPerformance_converged
{
public:
  explicit Init_MpcPerformance_converged(::wbot_msgs::msg::MpcPerformance & msg)
  : msg_(msg)
  {}
  Init_MpcPerformance_cost converged(::wbot_msgs::msg::MpcPerformance::_converged_type arg)
  {
    msg_.converged = std::move(arg);
    return Init_MpcPerformance_cost(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

class Init_MpcPerformance_iterations
{
public:
  explicit Init_MpcPerformance_iterations(::wbot_msgs::msg::MpcPerformance & msg)
  : msg_(msg)
  {}
  Init_MpcPerformance_converged iterations(::wbot_msgs::msg::MpcPerformance::_iterations_type arg)
  {
    msg_.iterations = std::move(arg);
    return Init_MpcPerformance_converged(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

class Init_MpcPerformance_solve_time
{
public:
  explicit Init_MpcPerformance_solve_time(::wbot_msgs::msg::MpcPerformance & msg)
  : msg_(msg)
  {}
  Init_MpcPerformance_iterations solve_time(::wbot_msgs::msg::MpcPerformance::_solve_time_type arg)
  {
    msg_.solve_time = std::move(arg);
    return Init_MpcPerformance_iterations(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

class Init_MpcPerformance_header
{
public:
  Init_MpcPerformance_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MpcPerformance_solve_time header(::wbot_msgs::msg::MpcPerformance::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MpcPerformance_solve_time(msg_);
  }

private:
  ::wbot_msgs::msg::MpcPerformance msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wbot_msgs::msg::MpcPerformance>()
{
  return wbot_msgs::msg::builder::Init_MpcPerformance_header();
}

}  // namespace wbot_msgs

#endif  // WBOT_MSGS__MSG__DETAIL__MPC_PERFORMANCE__BUILDER_HPP_
