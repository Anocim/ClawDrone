// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from px4_msgs:msg/RcChannels.idl
// generated code does not contain a copyright notice

#ifndef PX4_MSGS__MSG__DETAIL__RC_CHANNELS__STRUCT_H_
#define PX4_MSGS__MSG__DETAIL__RC_CHANNELS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/RcChannels in the package px4_msgs.
typedef struct px4_msgs__msg__RcChannels
{
  /// time since system start (microseconds)
  uint64_t timestamp;
  /// Timestamp of last valid RC signal
  uint64_t timestamp_last_valid;
  /// Scaled to -1..1 (throttle: 0..1)
  float channels[18];
  /// Number of valid channels
  uint8_t channel_count;
  /// Receive signal strength index
  uint8_t rssi;
  /// Control signal lost, should be checked together with topic timeout
  bool signal_lost;
  /// Number of dropped frames
  uint32_t frame_drop_count;
} px4_msgs__msg__RcChannels;

// Struct for a sequence of px4_msgs__msg__RcChannels.
typedef struct px4_msgs__msg__RcChannels__Sequence
{
  px4_msgs__msg__RcChannels * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} px4_msgs__msg__RcChannels__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PX4_MSGS__MSG__DETAIL__RC_CHANNELS__STRUCT_H_
