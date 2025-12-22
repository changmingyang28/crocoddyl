// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from wbot_msgs:msg/MpcPerformance.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "wbot_msgs/msg/detail/mpc_performance__struct.h"
#include "wbot_msgs/msg/detail/mpc_performance__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool wbot_msgs__msg__mpc_performance__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[46];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("wbot_msgs.msg._mpc_performance.MpcPerformance", full_classname_dest, 45) == 0);
  }
  wbot_msgs__msg__MpcPerformance * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // solve_time
    PyObject * field = PyObject_GetAttrString(_pymsg, "solve_time");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->solve_time = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // iterations
    PyObject * field = PyObject_GetAttrString(_pymsg, "iterations");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->iterations = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // converged
    PyObject * field = PyObject_GetAttrString(_pymsg, "converged");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->converged = (Py_True == field);
    Py_DECREF(field);
  }
  {  // cost
    PyObject * field = PyObject_GetAttrString(_pymsg, "cost");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->cost = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mpc_frequency
    PyObject * field = PyObject_GetAttrString(_pymsg, "mpc_frequency");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mpc_frequency = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * wbot_msgs__msg__mpc_performance__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of MpcPerformance */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("wbot_msgs.msg._mpc_performance");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "MpcPerformance");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  wbot_msgs__msg__MpcPerformance * ros_message = (wbot_msgs__msg__MpcPerformance *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // solve_time
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->solve_time);
    {
      int rc = PyObject_SetAttrString(_pymessage, "solve_time", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // iterations
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->iterations);
    {
      int rc = PyObject_SetAttrString(_pymessage, "iterations", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // converged
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->converged ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "converged", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // cost
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->cost);
    {
      int rc = PyObject_SetAttrString(_pymessage, "cost", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mpc_frequency
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mpc_frequency);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mpc_frequency", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
