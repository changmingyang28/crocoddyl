# generated from rosidl_generator_py/resource/_idl.py.em
# with input from wbot_msgs:msg/MpcPerformance.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MpcPerformance(type):
    """Metaclass of message 'MpcPerformance'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('wbot_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'wbot_msgs.msg.MpcPerformance')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__mpc_performance
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__mpc_performance
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__mpc_performance
            cls._TYPE_SUPPORT = module.type_support_msg__msg__mpc_performance
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__mpc_performance

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MpcPerformance(metaclass=Metaclass_MpcPerformance):
    """Message class 'MpcPerformance'."""

    __slots__ = [
        '_header',
        '_solve_time',
        '_iterations',
        '_converged',
        '_cost',
        '_mpc_frequency',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'solve_time': 'double',
        'iterations': 'int32',
        'converged': 'boolean',
        'cost': 'double',
        'mpc_frequency': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.solve_time = kwargs.get('solve_time', float())
        self.iterations = kwargs.get('iterations', int())
        self.converged = kwargs.get('converged', bool())
        self.cost = kwargs.get('cost', float())
        self.mpc_frequency = kwargs.get('mpc_frequency', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.solve_time != other.solve_time:
            return False
        if self.iterations != other.iterations:
            return False
        if self.converged != other.converged:
            return False
        if self.cost != other.cost:
            return False
        if self.mpc_frequency != other.mpc_frequency:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def solve_time(self):
        """Message field 'solve_time'."""
        return self._solve_time

    @solve_time.setter
    def solve_time(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'solve_time' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'solve_time' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._solve_time = value

    @builtins.property
    def iterations(self):
        """Message field 'iterations'."""
        return self._iterations

    @iterations.setter
    def iterations(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'iterations' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'iterations' field must be an integer in [-2147483648, 2147483647]"
        self._iterations = value

    @builtins.property
    def converged(self):
        """Message field 'converged'."""
        return self._converged

    @converged.setter
    def converged(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'converged' field must be of type 'bool'"
        self._converged = value

    @builtins.property
    def cost(self):
        """Message field 'cost'."""
        return self._cost

    @cost.setter
    def cost(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'cost' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'cost' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._cost = value

    @builtins.property
    def mpc_frequency(self):
        """Message field 'mpc_frequency'."""
        return self._mpc_frequency

    @mpc_frequency.setter
    def mpc_frequency(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'mpc_frequency' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'mpc_frequency' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._mpc_frequency = value
