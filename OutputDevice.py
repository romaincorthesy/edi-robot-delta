#!/usr/bin/env python3

import can
import struct 

class DeltaRobot:
    """A class describing a delta robot with three axes (A, B and C) to which move commands can be sent through CAN.

    Attributes:
        A_axis_id (int): the arbitration id of the motor A driver board
        B_axis_id (int): the arbitration id of the motor B driver board
        C_axis_id (int): the arbitration id of the motor C driver board
        sniff_traffic (bool): whether the CAN traffic should be intercepted and shown on /dev/ttyCAP before going to /dev/ttyACM0
    
    Notes:
        With sniff_traffic=True, first start interceptty in a terminal to sniff the communication:
    
        ```Bash
        sudo interceptty /dev/ttyACM0 /dev/ttyCAP -v | interceptty-nicedump
        ```
    """
    def __init__(self, A_axis_id: int, B_axis_id: int, C_axis_id: int, sniff_traffic:bool = False) -> None:
        self.A_axis_id = A_axis_id
        self.B_axis_id = B_axis_id
        self.C_axis_id = C_axis_id
        self._bus = can.interface.Bus(bustype='slcan', channel='/dev/ttyCAP' if sniff_traffic else '/dev/ttyACM0', bitrate=500000)
        self._notifier = can.Notifier(self._bus, [self._parse_data]) 

    def __del__(self) -> None:
        self._notifier.stop()
        self._bus.shutdown()

    def _parse_data(self, can: can) -> None:
        print(can.Message)

    def _sendMsg(self, dest_id: int, data: bytearray) -> int:
        """Send a CAN message to a motor driver board

        Args:
            dest_id (int): the arbitration id of a motor driver board
            data (bytearray): 8 bytes of data

        Returns:
            int: 1 if the message could not be sent, 0 otherwise
        """        
        msg = can.Message(arbitration_id=dest_id,
                    data=data,
                    is_extended_id=True,
                    check=True)

        try:
            self._bus.send(msg)
            print("Message sent on {}".format(self._bus.channel_info))
            return 0
        except can.CanError:
            print("Message NOT sent")
            return 1
        except Exception as e:
            print("Unknown error : "  + e)
            raise

    def moveAxisTo(self, axis_id: int, angle: float) -> int:
        """Send a command to the robot to set a given axis to a given angle.

        Args:
            axis_id (int): the CAN id a the motor driver board
            angle (float): the angle to which the motor should go

        Returns:
            int: 1 if the command failed, 0 otherwise
        """
        ba = bytearray(struct.pack("d", angle)) # Using double : 8 bytes
        print(f"{ba.hex(':')} ({angle})") # Prints as '40:45:35:c2:8f:5c:28:f6 (42.420000)'
        return self._sendMsg(axis_id, ba)
    
    def moveAllAxesTo(self, angle_A: float, angle_B: float, angle_C: float) -> int:
        """Send a command to the robot to set all axes to a given set of angles.

        Args:
            angle_A (float): the angle to which motor A should go
            angle_B (float): the angle to which motor B should go
            angle_C (float): the angle to which motor C should go

        Returns:
            int: a bit superposition if the command failed (0b0CBA), 0 otherwise
        """
        ret_A = self.moveAxisTo(self.A_axis_id, angle_A)
        ret_B = self.moveAxisTo(self.B_axis_id, angle_B)
        ret_C = self.moveAxisTo(self.C_axis_id, angle_C)

        return ret_A + 2*ret_B + 4*ret_C

