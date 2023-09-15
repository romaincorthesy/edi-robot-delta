#!/usr/bin/env python3

import can

# If using SNIFF_TRAFFIC, first start interceptty in a terminal to sniff the communication:
# sudo interceptty /dev/ttyACM0 /dev/ttyCAP -v
SNIFF_TRAFFIC = True



with can.interface.Bus(bustype='slcan', channel='/dev/ttyCAP' if SNIFF_TRAFFIC else '/dev/ttyACM0', bitrate=500000) as bus:

    msg = can.Message(arbitration_id=0xc0ffee,
                    data=[0, 1, 0, 1, 1, 1, 1, 1],
                    is_extended_id=True,
                    check=True)

    try:
        bus.send(msg)
        print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")
    except Exception as e:
        print("Unknown error : "  + e)
        raise