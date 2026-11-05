# generated from rosidl_generator_py/resource/_idl.py.em
# with input from px4_msgs:msg/RcChannels.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'channels'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_RcChannels(type):
    """Metaclass of message 'RcChannels'."""

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
            module = import_type_support('px4_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'px4_msgs.msg.RcChannels')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__rc_channels
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__rc_channels
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__rc_channels
            cls._TYPE_SUPPORT = module.type_support_msg__msg__rc_channels
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__rc_channels

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class RcChannels(metaclass=Metaclass_RcChannels):
    """Message class 'RcChannels'."""

    __slots__ = [
        '_timestamp',
        '_timestamp_last_valid',
        '_channels',
        '_channel_count',
        '_rssi',
        '_signal_lost',
        '_frame_drop_count',
    ]

    _fields_and_field_types = {
        'timestamp': 'uint64',
        'timestamp_last_valid': 'uint64',
        'channels': 'float[18]',
        'channel_count': 'uint8',
        'rssi': 'uint8',
        'signal_lost': 'boolean',
        'frame_drop_count': 'uint32',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('float'), 18),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.timestamp = kwargs.get('timestamp', int())
        self.timestamp_last_valid = kwargs.get('timestamp_last_valid', int())
        if 'channels' not in kwargs:
            self.channels = numpy.zeros(18, dtype=numpy.float32)
        else:
            self.channels = kwargs.get('channels')
        self.channel_count = kwargs.get('channel_count', int())
        self.rssi = kwargs.get('rssi', int())
        self.signal_lost = kwargs.get('signal_lost', bool())
        self.frame_drop_count = kwargs.get('frame_drop_count', int())

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
        if self.timestamp != other.timestamp:
            return False
        if self.timestamp_last_valid != other.timestamp_last_valid:
            return False
        if any(self.channels != other.channels):
            return False
        if self.channel_count != other.channel_count:
            return False
        if self.rssi != other.rssi:
            return False
        if self.signal_lost != other.signal_lost:
            return False
        if self.frame_drop_count != other.frame_drop_count:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def timestamp(self):
        """Message field 'timestamp'."""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'timestamp' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'timestamp' field must be an unsigned integer in [0, 18446744073709551615]"
        self._timestamp = value

    @builtins.property
    def timestamp_last_valid(self):
        """Message field 'timestamp_last_valid'."""
        return self._timestamp_last_valid

    @timestamp_last_valid.setter
    def timestamp_last_valid(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'timestamp_last_valid' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'timestamp_last_valid' field must be an unsigned integer in [0, 18446744073709551615]"
        self._timestamp_last_valid = value

    @builtins.property
    def channels(self):
        """Message field 'channels'."""
        return self._channels

    @channels.setter
    def channels(self, value):
        if isinstance(value, numpy.ndarray):
            assert value.dtype == numpy.float32, \
                "The 'channels' numpy.ndarray() must have the dtype of 'numpy.float32'"
            assert value.size == 18, \
                "The 'channels' numpy.ndarray() must have a size of 18"
            self._channels = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 18 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'channels' field must be a set or sequence with length 18 and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._channels = numpy.array(value, dtype=numpy.float32)

    @builtins.property
    def channel_count(self):
        """Message field 'channel_count'."""
        return self._channel_count

    @channel_count.setter
    def channel_count(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'channel_count' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'channel_count' field must be an unsigned integer in [0, 255]"
        self._channel_count = value

    @builtins.property
    def rssi(self):
        """Message field 'rssi'."""
        return self._rssi

    @rssi.setter
    def rssi(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rssi' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rssi' field must be an unsigned integer in [0, 255]"
        self._rssi = value

    @builtins.property
    def signal_lost(self):
        """Message field 'signal_lost'."""
        return self._signal_lost

    @signal_lost.setter
    def signal_lost(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'signal_lost' field must be of type 'bool'"
        self._signal_lost = value

    @builtins.property
    def frame_drop_count(self):
        """Message field 'frame_drop_count'."""
        return self._frame_drop_count

    @frame_drop_count.setter
    def frame_drop_count(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'frame_drop_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'frame_drop_count' field must be an unsigned integer in [0, 4294967295]"
        self._frame_drop_count = value
