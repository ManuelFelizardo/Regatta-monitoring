import construct
from construct import *


class Message:
    MSP_MSG_IDENT = 100
    MSP_MSG_STATUS = 101
    MSP_MSG_RAW_IMU = 102
    MSP_MSG_SERVO = 103
    MSP_MSG_MOTOR = 104
    MSP_MSG_RC = 105
    MSP_MSG_RAW_GPS = 106
    MSP_MSG_COMP_GPS = 107
    MSP_MSG_ATTITUDE = 108
    MSP_MSG_ALTITUDE = 109
    MSP_MSG_ANALOG = 110
    MSP_MSG_RC_TUNING = 111
    MSP_MSG_PID = 112
    MSP_MSG_BOX = 113
    MSP_MSG_MISC = 114
    MSP_MSG_MOTOR_PINS = 115
    MSP_MSG_BOXNAMES = 116
    MSP_MSG_PIDNAMES = 117
    MSP_MSG_WP = 118
    MSP_MSG_BOXIDS = 119
    MSP_MSG_SERVO_CONF = 120
    MSP_MSG_SET_RAW_RC = 200
    MSP_MSG_SET_RAW_GPS = 201
    MSP_MSG_SET_PID = 202
    MSP_MSG_SET_BOX = 203
    MSP_MSG_SET_RC_TUNING = 204
    MSP_MSG_ACC_CALIBRATION = 205
    MSP_MSG_MAG_CALIBRATION = 206
    MSP_MSG_SET_MISC = 207
    MSP_MSG_RESET_CONF = 208
    MSP_MSG_SET_WP = 209
    MSP_MSG_SELECT_SETTING = 210
    MSP_MSG_SET_HEAD = 211
    MSP_MSG_SET_SERVO_CONF = 212
    MSP_MSG_SET_MOTOR = 214
    MSP_MSG_BIND = 240
    MSP_MSG_EEPROM_WRITE = 250

    struct = construct.Struct("0" / construct.Const(b"$"),
                                "1" / construct.Const(b"X"),
                                "direction" / construct.Const(b"<"),
                                "flag" / construct.Const(b"\0"),
                                "function" / construct.ByteSwapped(construct.BytesInteger(2)),
                                "payloadSize" / construct.ByteSwapped(construct.BytesInteger(2)),
                                "payload" / construct.Array(this.payloadSize, Int8ub),
                                "checksum" / Int8ub
                                )
    structRecv = construct.Struct("0" / construct.Const(b"$"),
                                "1" / construct.Const(b"X"),
                                "direction" / construct.Const(b">"),
                                "flag" / construct.Const(b"\0"),
                                "function" / construct.ByteSwapped(construct.BytesInteger(2)),
                                "payloadSize" / construct.ByteSwapped(construct.BytesInteger(2)),
                                "payload" / construct.Array(this.payloadSize, Int8ub),
                                "checksum" / Int8ub
                                )

    checksumFormat = construct.Struct(
                              "function" / construct.ByteSwapped(construct.BytesInteger(2)),
                              "payloadSize" / construct.ByteSwapped(construct.BytesInteger(2)),
                              "payload" / construct.Array(this.payloadSize, Int8ub),
                              )

    msp_servo = construct.Struct(
        "servo" / construct.Array(8, construct.ByteSwapped(construct.BytesInteger(2)))
    )

    msp_motor = construct.Struct(
        "motor" / construct.Array(8,construct.ByteSwapped(construct.BytesInteger(2)))
    )

    msp_set_motor = construct.Struct(
        "motor" / construct.Array(8,construct.ByteSwapped(construct.BytesInteger(2)))
    )

    msp_rc = construct.Struct(
        "rc_data" / construct.Array(8,construct.ByteSwapped(construct.BytesInteger(2)))
    )

    msp_set_raw_rc = construct.Struct(
        "rc_data" / construct.Array(8,construct.ByteSwapped(construct.BytesInteger(2)))
    )

    msp_raw_gps = construct.Struct(
        "fix" / construct.ByteSwapped(construct.BytesInteger(1)),
        "num_sat" / construct.ByteSwapped(construct.BytesInteger(1)),
        "coord_lat" / construct.ByteSwapped(Int32sb),
        "coord_lon" / construct.ByteSwapped(Int32sb),
        "altitude" / construct.ByteSwapped(Int16sb),
        "speed" / construct.ByteSwapped(construct.BytesInteger(2)),
        "ground_course" / construct.ByteSwapped(construct.BytesInteger(2)),

    )

    msp_set_raw_gps = construct.Struct(
        "fix" / construct.ByteSwapped(construct.BytesInteger(1)),
        "num_sat" / construct.ByteSwapped(construct.BytesInteger(1)),
        "coord_lat" / construct.ByteSwapped(construct.BytesInteger(4)),
        "coord_lon" / construct.ByteSwapped(construct.BytesInteger(4)),
        "altitude" / construct.ByteSwapped(construct.BytesInteger(2)),
        "speed" / construct.ByteSwapped(construct.BytesInteger(2))
    )

    msp_comp_gps = construct.Struct(
        "distance_to_home" / construct.ByteSwapped(construct.BytesInteger(2)),
        "direction_to_home" / construct.ByteSwapped(construct.BytesInteger(2)),
        "update" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_attitude = construct.Struct(
        "angx" / construct.ByteSwapped(Int16sb),
        "angy" / construct.ByteSwapped(Int16sb),
        "heading" / construct.ByteSwapped(construct.BytesInteger(2)),
    )

    msp_altitude = construct.Struct(
        "alt" / construct.ByteSwapped(Int32sb),
        "vario" / construct.ByteSwapped(construct.BytesInteger(2))

    )

    msp_analog = construct.Struct(
        "vbat" / construct.ByteSwapped(construct.BytesInteger(1)),
        "power_meter_sum" / construct.ByteSwapped(construct.BytesInteger(2)),
        "rssi" / construct.ByteSwapped(construct.BytesInteger(2)),
        "amperage" / construct.ByteSwapped(construct.BytesInteger(2))
    )

    msp_rc_tuning = construct.Struct(
        "rc_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "rc_expo" / construct.ByteSwapped(construct.BytesInteger(1)),
        "roll_pitch_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "yaw_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "dyn_thr_pid" / construct.ByteSwapped(construct.BytesInteger(1)),
        "throttle_mid" / construct.ByteSwapped(construct.BytesInteger(1)),
        "throttle_expo" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_set_rc_tuning = construct.Struct(
        "rc_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "rc_expo" / construct.ByteSwapped(construct.BytesInteger(1)),
        "roll_pitch_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "yaw_rate" / construct.ByteSwapped(construct.BytesInteger(1)),
        "dyn_thr_pid" / construct.ByteSwapped(construct.BytesInteger(1)),
        "throttle_mid" / construct.ByteSwapped(construct.BytesInteger(1)),
        "throttle_expo" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    _msp_pid_item = construct.Struct(
        "p" / construct.ByteSwapped(construct.BytesInteger(1)),
        "i" / construct.ByteSwapped(construct.BytesInteger(1)),
        "d" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_pid = construct.Struct(
        "roll" / _msp_pid_item,
        "pitch" / _msp_pid_item,
        "yaw" / _msp_pid_item,
        "alt" / _msp_pid_item,
        "pos" / _msp_pid_item,
        "posr" / _msp_pid_item,
        "navr" / _msp_pid_item,
        "level" / _msp_pid_item,
        "mag" / _msp_pid_item,
        "vel" / _msp_pid_item,
    )

    msp_set_pid = construct.Struct(
        "roll" / _msp_pid_item,
        "pitch" / _msp_pid_item,
        "yaw" / _msp_pid_item,
        "alt" / _msp_pid_item,
        "pos" / _msp_pid_item,
        "posr" / _msp_pid_item,
        "navr" / _msp_pid_item,
        "level" / _msp_pid_item,
        "mag" / _msp_pid_item,
        "vel" / _msp_pid_item
    )

    msp_box = construct.Struct(
        "boxitems[1]" / construct.ByteSwapped(construct.BytesInteger(2))
    )

    msp_set_box = construct.Struct(
        "boxitems[1]" / construct.ByteSwapped(construct.BytesInteger(2))
    )

    msp_misc = construct.Struct(
        "power_trigger" / construct.ByteSwapped(construct.BytesInteger(2)),
        "min_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "max_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "min_command" / construct.ByteSwapped(construct.BytesInteger(2)),
        "failsafe_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "arm_count" / construct.ByteSwapped(construct.BytesInteger(2)),
        "lifetime" / construct.ByteSwapped(construct.BytesInteger(4)),
        "mag_declination" / construct.ByteSwapped(construct.BytesInteger(2)),
        "vbat_scale" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_warn1" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_warn2" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_crit" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_set_misc = construct.Struct(
        "power_trigger" / construct.ByteSwapped(construct.BytesInteger(2)),
        "min_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "max_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "min_command" / construct.ByteSwapped(construct.BytesInteger(2)),
        "failsafe_throttle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "arm_count" / construct.ByteSwapped(construct.BytesInteger(2)),
        "lifetime" / construct.ByteSwapped(construct.BytesInteger(4)),
        "mag_declination" / construct.ByteSwapped(construct.BytesInteger(2)),
        "vbat_scale" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_warn1" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_warn2" / construct.ByteSwapped(construct.BytesInteger(1)),
        "vbat_crit" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_motor_pins = construct.Struct(
        "pwm_pin" / construct.Array(8,construct.ByteSwapped(construct.BytesInteger(1)))
    )

    msp_wp = construct.Struct(
        "wp_no" / construct.ByteSwapped(construct.BytesInteger(1)),
        "action" / construct.ByteSwapped(construct.BytesInteger(1)),
        "lat" / construct.ByteSwapped(construct.BytesInteger(4)),
        "lon" / construct.ByteSwapped(construct.BytesInteger(4)),
        "alt_hold" / construct.ByteSwapped(construct.BytesInteger(4)),
        "p1" / construct.ByteSwapped(construct.BytesInteger(2)),
        "p2" / construct.ByteSwapped(construct.BytesInteger(2)),
        "p3" / construct.ByteSwapped(construct.BytesInteger(2)),
        "nav_flag" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_set_wp = construct.Struct(
        "wp_no" / construct.ByteSwapped(construct.BytesInteger(1)),
        "action" / construct.ByteSwapped(construct.BytesInteger(1)),
        "lat" / construct.ByteSwapped(Int32sb),
        "lon" / construct.ByteSwapped(Int32sb),
        "alt_hold" / construct.ByteSwapped(construct.BytesInteger(4)),
        "heading" / construct.ByteSwapped(construct.BytesInteger(2)),
        "p2" / construct.ByteSwapped(construct.BytesInteger(2)),
        "p3" / construct.ByteSwapped(construct.BytesInteger(2)),
        "nav_flag" / construct.ByteSwapped(construct.BytesInteger(1)),
    )

    msp_boxids = construct.Struct(
        "checkbox_items[0]" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    _msp_servo_conf_item = construct.Struct(
        "min" / construct.ByteSwapped(construct.BytesInteger(2)),
        "max" / construct.ByteSwapped(construct.BytesInteger(2)),
        "middle" / construct.ByteSwapped(construct.BytesInteger(2)),
        "rate" / construct.ByteSwapped(construct.BytesInteger(1)),
    )

    msp_select_setting = construct.Struct(
        "current_set" / construct.ByteSwapped(construct.BytesInteger(1))
    )

    msp_set_head = construct.Struct(
        "mag_hold" / construct.ByteSwapped(construct.BytesInteger(2))
    )


def getCheckSum(bytes):
    for i in bytes:
        checksum = checkSum(checksum, i)
    return checksum


def checkSum(crc, a):
    crc ^= a
    for i in range(0, 8):

        if crc & 0x80:
            crc = ((crc & 127) << 1) ^ 0xD5
        else:
            crc = (crc & 127) << 1
    return crc
