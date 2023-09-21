#!/usr/bin/env python3

import can
import struct
import GM_functions
from pprint import pprint


class OperationalSpace:
    def __init__(self,
                 x_axis_min: float, x_axis_max: float,
                 y_axis_min: float, y_axis_max: float,
                 z_axis_min: float, z_axis_max: float) -> None:
        self.x_axis_min = x_axis_min
        self.x_axis_max = x_axis_max
        self.y_axis_min = y_axis_min
        self.y_axis_max = y_axis_max
        self.z_axis_min = z_axis_min
        self.z_axis_max = z_axis_max

    def __str__(self) -> str:
        return f"OperationSpace\n\
        X Axis : from {self.x_axis_min} to {self.x_axis_max}\n\
        Y Axis : from {self.y_axis_min} to {self.y_axis_max}\n\
        Z Axis : from {self.z_axis_min} to {self.z_axis_max}"


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
    DEBUG = False
    GM_PRECISION = 3

    def __init__(self, A_axis_id: int, B_axis_id: int, C_axis_id: int, A_encoder_id: int, B_encoder_id: int, C_encoder_id: int, sniff_traffic: bool = False) -> None:
        self.A_axis_id = A_axis_id
        self.B_axis_id = B_axis_id
        self.C_axis_id = C_axis_id
        self.A_encoder_id = A_encoder_id
        self.B_encoder_id = B_encoder_id
        self.C_encoder_id = C_encoder_id
        self._bus = can.interface.Bus(
            bustype='slcan', channel='/dev/ttyCAP' if sniff_traffic else '/dev/ttyACM0', bitrate=500000)
        self._notifier = can.Notifier(self._bus, [self._parse_data])
        self.callbackUpdate = None
        self._current_angles = [None, None, None]
        self._new_A_received = False
        self._new_B_received = False
        self._new_C_received = False
        self.x = None
        self.y = None
        self.z = None

        # Physical operational space [m]
        RADIUS: float = 0.200    # Radius of the usable range
        MIN_X = -RADIUS/2
        MAX_X = RADIUS/2
        MIN_Y = -RADIUS/2
        MAX_Y = RADIUS/2
        MIN_Z = -0.100
        MAX_Z = -0.150
        self.operational_space = OperationalSpace(
            MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z)

    def __del__(self) -> None:
        self._notifier.stop()
        self._bus.shutdown()

    def _parse_data(self, msg: can.Message) -> None:
        """Parse incoming CAN message and update current angles and call the callback if it exists.

        Args:
            msg (can.Message): CAN message containing a new value for an angle

        Raises:
            can.CanOperationError: if the message arbitration id is not one of the angles.
        """
        try:
            # pprint(msg)
            id = msg.arbitration_id
            angle = struct.unpack('d', msg.data)[0]
            if id == self.A_encoder_id:
                self._current_angles[0] = angle
                self._new_A_received = True
                print("New A received")
            elif id == self.B_encoder_id:
                self._current_angles[1] = angle
                self._new_B_received = True
                print("New B received")
            elif id == self.C_encoder_id:
                self._current_angles[2] = angle
                self._new_C_received = True
                print("New C received")
            else:
                print(
                    f"Arbitration id options are:\n\t{self.A_encoder_id}\n\t{self.B_encoder_id}\n\t{self.C_encoder_id}")
                raise can.CanOperationError(
                    f"Received message with unknown arbitration id: {id}")
        except Exception as e:
            print("Error in _parse_data: {e}")
            raise e

        # and self._new_A_received and self._new_B_received and self._new_C_received:
        if not None in self._current_angles:
            self._new_A_received = False
            self._new_B_received = False
            self._new_C_received = False
            new_position = self.DGM(self._current_angles)

            self.x, self.y, self.z = new_position

            if self.callbackUpdate is not None:
                self.callbackUpdate(new_position)

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
            # print("Message sent on {}".format(self._bus.channel_info))
            return 0
        except can.CanError:
            print("Message NOT sent")
            return 1
        except Exception as e:
            print("Unknown error : " + e)
            raise

    def moveAxisTo(self, axis_id: int, angle: float) -> int:
        """Send a command to the robot to set a given axis to a given angle.

        Args:
            axis_id (int): the CAN id a the motor driver board
            angle (float): the angle in radians to which the motor should go

        Returns:
            int: 1 if the command failed, 0 otherwise
        """
        ba = bytearray(struct.pack("d", angle))  # Using double : 8 bytes
        # print(f"{ba.hex(':')} ({angle})") # Prints as '40:45:35:c2:8f:5c:28:f6 (42.420000)'
        return self._sendMsg(axis_id, ba)

    def moveAllAxesTo(self, angle_A: float, angle_B: float, angle_C: float) -> int:
        """Send a command to the robot to set all axes to a given set of angles.

        Args:
            angle_A (float): the angle in radians to which motor A should go
            angle_B (float): the angle in radians to which motor B should go
            angle_C (float): the angle in radians to which motor C should go

        Returns:
            int: a bit superposition if the command failed (0b0CBA), 0 otherwise
        """
        ret_A = self.moveAxisTo(self.A_axis_id, angle_A)
        ret_B = self.moveAxisTo(self.B_axis_id, angle_B)
        ret_C = self.moveAxisTo(self.C_axis_id, angle_C)

        return ret_A + 2*ret_B + 4*ret_C

    def moveBaseToXYZ(self, xyz_coord: tuple[float, float, float]) -> int:
        """Move the base of the robot to a x,y,z point in the operational space

        Args:
            xyz_coord (tuple[float, float, float]): a vector discribing the x,y,z position to move to

        Returns:
            int: a bit superposition if the sending ov the move command failed (0b0CBA), 0 otherwise
        """
        angle_A, angle_B, angle_C = self.IGM(xyz_coord)
        return self.moveAllAxesTo(angle_A, angle_B, angle_C)

    def IGM(self, X_op: tuple[float, float, float]) -> tuple[float, float, float]:
        Q_art: tuple[float, float, float] = None
        X_op_rounded = tuple([round(x, DeltaRobot.GM_PRECISION) for x in X_op])
        if DeltaRobot.DEBUG:
            (x, y, z) = X_op_rounded
            Q_art = [x/100.0, y/100.0, z/100.0]
        else:
            Q_art, err = GM_functions.Rot_Inv_Geometric_Model(X_op_rounded)
            if err != 0:
                raise ArithmeticError(
                    f"Rot_Inv_Geometric_Model returned error number {err}")
            Q_art = [round(q, DeltaRobot.GM_PRECISION) for q in Q_art]

        return Q_art

    def DGM(self, Q_art: tuple[float, float, float]) -> tuple[float, float, float]:
        X_op: tuple[float, float, float] = None
        Q_art_rounded = tuple(
            [round(q, DeltaRobot.GM_PRECISION) for q in Q_art])
        if DeltaRobot.DEBUG:
            (x, y, z) = Q_art_rounded
            X_op = [x*100.0, y*100.0, z*100.0]
        else:
            X_op, err = GM_functions.Rot_Dir_Geometric_Model(Q_art_rounded)
            if err != 0:
                raise ArithmeticError(
                    f"Rot_Dir_Geometric_Model returned error number {err}")
            X_op = [round(x, DeltaRobot.GM_PRECISION) for x in X_op]

        return X_op
