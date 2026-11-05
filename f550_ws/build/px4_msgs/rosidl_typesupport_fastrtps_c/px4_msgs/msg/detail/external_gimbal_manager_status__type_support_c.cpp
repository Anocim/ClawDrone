// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from px4_msgs:msg/ExternalGimbalManagerStatus.idl
// generated code does not contain a copyright notice
#include "px4_msgs/msg/detail/external_gimbal_manager_status__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "px4_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "px4_msgs/msg/detail/external_gimbal_manager_status__struct.h"
#include "px4_msgs/msg/detail/external_gimbal_manager_status__functions.h"
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


using _ExternalGimbalManagerStatus__ros_msg_type = px4_msgs__msg__ExternalGimbalManagerStatus;

static bool _ExternalGimbalManagerStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _ExternalGimbalManagerStatus__ros_msg_type * ros_message = static_cast<const _ExternalGimbalManagerStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: timestamp
  {
    cdr << ros_message->timestamp;
  }

  // Field name: manager_sysid
  {
    cdr << ros_message->manager_sysid;
  }

  // Field name: manager_compid
  {
    cdr << ros_message->manager_compid;
  }

  // Field name: flags
  {
    cdr << ros_message->flags;
  }

  // Field name: gimbal_device_id
  {
    cdr << ros_message->gimbal_device_id;
  }

  // Field name: primary_control_sysid
  {
    cdr << ros_message->primary_control_sysid;
  }

  // Field name: primary_control_compid
  {
    cdr << ros_message->primary_control_compid;
  }

  // Field name: secondary_control_sysid
  {
    cdr << ros_message->secondary_control_sysid;
  }

  // Field name: secondary_control_compid
  {
    cdr << ros_message->secondary_control_compid;
  }

  return true;
}

static bool _ExternalGimbalManagerStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _ExternalGimbalManagerStatus__ros_msg_type * ros_message = static_cast<_ExternalGimbalManagerStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: timestamp
  {
    cdr >> ros_message->timestamp;
  }

  // Field name: manager_sysid
  {
    cdr >> ros_message->manager_sysid;
  }

  // Field name: manager_compid
  {
    cdr >> ros_message->manager_compid;
  }

  // Field name: flags
  {
    cdr >> ros_message->flags;
  }

  // Field name: gimbal_device_id
  {
    cdr >> ros_message->gimbal_device_id;
  }

  // Field name: primary_control_sysid
  {
    cdr >> ros_message->primary_control_sysid;
  }

  // Field name: primary_control_compid
  {
    cdr >> ros_message->primary_control_compid;
  }

  // Field name: secondary_control_sysid
  {
    cdr >> ros_message->secondary_control_sysid;
  }

  // Field name: secondary_control_compid
  {
    cdr >> ros_message->secondary_control_compid;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_px4_msgs
size_t get_serialized_size_px4_msgs__msg__ExternalGimbalManagerStatus(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _ExternalGimbalManagerStatus__ros_msg_type * ros_message = static_cast<const _ExternalGimbalManagerStatus__ros_msg_type *>(untyped_ros_message);
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
  // field.name manager_sysid
  {
    size_t item_size = sizeof(ros_message->manager_sysid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name manager_compid
  {
    size_t item_size = sizeof(ros_message->manager_compid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name flags
  {
    size_t item_size = sizeof(ros_message->flags);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name gimbal_device_id
  {
    size_t item_size = sizeof(ros_message->gimbal_device_id);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name primary_control_sysid
  {
    size_t item_size = sizeof(ros_message->primary_control_sysid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name primary_control_compid
  {
    size_t item_size = sizeof(ros_message->primary_control_compid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name secondary_control_sysid
  {
    size_t item_size = sizeof(ros_message->secondary_control_sysid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name secondary_control_compid
  {
    size_t item_size = sizeof(ros_message->secondary_control_compid);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _ExternalGimbalManagerStatus__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_px4_msgs__msg__ExternalGimbalManagerStatus(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_px4_msgs
size_t max_serialized_size_px4_msgs__msg__ExternalGimbalManagerStatus(
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
  // member: manager_sysid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: manager_compid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: flags
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: gimbal_device_id
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: primary_control_sysid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: primary_control_compid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: secondary_control_sysid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: secondary_control_compid
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = px4_msgs__msg__ExternalGimbalManagerStatus;
    is_plain =
      (
      offsetof(DataType, secondary_control_compid) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _ExternalGimbalManagerStatus__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_px4_msgs__msg__ExternalGimbalManagerStatus(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_ExternalGimbalManagerStatus = {
  "px4_msgs::msg",
  "ExternalGimbalManagerStatus",
  _ExternalGimbalManagerStatus__cdr_serialize,
  _ExternalGimbalManagerStatus__cdr_deserialize,
  _ExternalGimbalManagerStatus__get_serialized_size,
  _ExternalGimbalManagerStatus__max_serialized_size
};

static rosidl_message_type_support_t _ExternalGimbalManagerStatus__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_ExternalGimbalManagerStatus,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, px4_msgs, msg, ExternalGimbalManagerStatus)() {
  return &_ExternalGimbalManagerStatus__type_support;
}

#if defined(__cplusplus)
}
#endif
