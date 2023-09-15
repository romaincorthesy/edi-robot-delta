#!/usr/bin/env python3

import can

class RobotDelta:
    # If using sniff_traffic, first start interceptty in a terminal to sniff the communication:
    # sudo interceptty /dev/ttyACM0 /dev/ttyCAP -v | interceptty-nicedump
    def __init__(self, sniff_traffic = False) -> None:
        self.bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyCAP' if sniff_traffic else '/dev/ttyACM0', bitrate=500000)
        self.notifier = can.Notifier(self.bus, [self.parse_data]) 

    def __del__(self) -> None:
        self.notifier.stop()
        self.bus.shutdown()

    def parse_data(self, can: can) -> None:
        print(can.Message)

    def sendMsg(self, dest_id: int, data: bytearray) -> int:
        msg = can.Message(arbitration_id=dest_id,
                    data=data,
                    is_extended_id=True,
                    check=True)

        try:
            self.bus.send(msg)
            print("Message sent on {}".format(self.bus.channel_info))
            return 0
        except can.CanError:
            print("Message NOT sent")
            return 1
        except Exception as e:
            print("Unknown error : "  + e)
            raise

