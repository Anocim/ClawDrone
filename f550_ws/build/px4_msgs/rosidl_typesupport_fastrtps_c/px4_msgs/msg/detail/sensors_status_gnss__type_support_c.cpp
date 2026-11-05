// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from px4_msgs:msg/SensorsStatusGnss.idl
// generated code does not contain a copyright notice
#include "px4_msgs/msg/detail/sensors_status_gnss__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "px4_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "px4_msgs/msg/detail/sensors_status_gnss__struct.h"
#include "px4_msgs/msg/detail/sensors_status_gnss__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _SensorsStatusGnss__ros_msg_type = px4_msgs__msg__SensorsStatusGnss;

static bool _SensorsStatusGnss__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _SensorsStatusGnss__ros_msg_type * ros_message = static_cast<const _SensorsStatusGnss__ros_msg_type *>(untyped_ros_message);
  // Field name: timestamp
  {
    cdr << ros_message->timestamp;
  }

  // Field name: device_id_selected
  {
    cdr << ros_message->device_id_selected;
  }

  // Field name: device_ids
  {
    size_t size = 4;
    auto array_ptr = ros_message->device_ids;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: order
  {
    size_t size = 4;
    auto array_ptr = ros_message->order;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: healthy
  {
    size_t size = 4;
    auto array_ptr = ros_message->healthy;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: failed_checks
  {
    size_t size = 4;
    auto array_ptr = ros_message->failed_checks;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: strict
  {
    size_t size = 4;
    auto array_ptr = ros_message->strict;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: drift_rate_horizontal
  {
    size_t size = 4;
    auto array_ptr = ros_message->drift_rate_horizontal;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: drift_rate_vertical
  {
    size_t size = 4;
    auto array_ptr = ros_message->drift_rate_vertical;
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: speed_horizontal_filtered
  {
    size_t size = 4;
    auto array_ptr = ros_message->speed_horizontal_filtered;
    cdr.serializeArray(array_ptr, size);
  }

  return true;
}

static bool _SensorsStatusGnss__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _SensorsStatusGnss__ros_msg_type * ros_message = static_cast<_SensorsStatusGnss__ros_msg_type *>(untyped_ros_message);
  // Field name: timestamp
  {
    cdr >> ros_message->timestamp;
  }

  // Field name: device_id_selected
  {
    cdr >> ros_message->device_id_selected;
  }

  // Field name: device_ids
  {
    size_t size = 4;
    auto array_ptr = ros_message->device_ids;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: order
  {
    size_t size = 4;
    auto array_ptr = ros_message->order;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: healthy
  {
    size_t size = 4;
    auto array_ptr = ros_message->healthy;
    for (size_t i = 0; i < size; ++i) {
      uint8_t tmp;
      cdr >> tmp;
      array_ptr[i] = tmp ? true : false;
    }
  }

  // Field name: failed_checks
  {
    size_t size = 4;
    auto array_ptr = ros_message->failed_checks;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: strict
  {
    size_t size = 4;
    auto array_ptr = ros_message->strict;
    for (size_t i = 0; i < size; ++i) {
      uint8_t tmp;
      cdr >> tmp;
      array_ptr[i] = tmp ? true : false;
    }
  }

  // Field name: drift_rate_horizontal
  {
    size_t size = 4;
    auto array_ptr = ros_message->drift_rate_horizontal;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: drift_rate_vertical
  {
    size_t size = 4;
    auto array_ptr = ros_message->drift_rate_vertical;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: speed_horizontal_filtered
  {
    size_t size = 4;
    auto array_ptr = ros_message->speed_horizontal_filtered;
    cdr.deserializeArray(array_ptr, size);
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_px4_msgs
size_t get_serialized_size_px4_msgs__msg__SensorsStatusGnss(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _SensorsStatusGnss__ros_msg_type * ros_message = static_cast<const _SensorsStatusGnss__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name timestamp
  {
    size_t item_size = sizeof(ros_message->timestamp);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name device_id_selected
  {
    size_t item_size = sizeof(ros_message->device_id_selected);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name device_ids
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->device_ids;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name order
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->order;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name healthy
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->healthy;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name failed_checks
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->failed_checks;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name strict
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->strict;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name drift_rate_horizontal
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->drift_rate_horizontal;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name drift_rate_vertical
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->drift_rate_vertical;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name speed_horizontal_filtered
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->speed_horizontal_filtered;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _SensorsStatusGnss__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_px4_msgs__msg__SensorsStatusGnss(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_px4_msgs
size_t max_serialized_size_px4_msgs__msg__SensorsStatusGnss(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: timestamp
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }
  // member: device_id_selected
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: device_ids
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: order
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: healthy
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: failed_checks
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: strict
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: drift_rate_horizontal
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: drift_rate_vertical
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: speed_horizontal_filtered
  {
    size_t array_size = 4;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = px4_msgs__msg__SensorsStatusGnss;
    is_plain =
      (
      offsetof(DataType, speed_horizontal_filtered) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _SensorsStatusGnss__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_px4_msgs__msg__SensorsStatusGnss(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_SensorsStatusGnss = {
  "px4_msgs::msg",
  "SensorsStatusGnss",
  _SensorsStatusGnss__cdr_serialize,
  _SensorsStatusGnss__cdr_deserialize,
  _SensorsStatusGnss__get_serialized_size,
  _SensorsStatusGnss__max_serialized_size
};

static rosidl_message_type_support_t _SensorsStatusGnss__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_SensorsStatusGnss,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, px4_msgs, msg, SensorsStatusGnss)() {
  return &_SensorsStatusGnss__type_support;
}

#if defined(__cplusplus)
}
#endif
