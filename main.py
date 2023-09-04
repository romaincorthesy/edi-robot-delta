#!/usr/bin/python3
# -*- coding: utf-8

import can


def send_one():
    bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
    # is_extended_id=True : arbitration_id is 29 bits in length (extended addressing, CAN 2.0B)
    msg = can.Message(arbitration_id=0xc0ffee, data=[0, 25, 0, 1, 3, 1, 4, 1], is_extended_id=True)

    try:
        bus.send(msg)
        print("Message sent on {}".format(bus.channel_info))
    except can.CanError:
        print("Message NOT sent")


if __name__ == '__main__':
    send_one()
