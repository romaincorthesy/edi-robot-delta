#!/usr/bin/bash /usr/bin/python3

# This code is intended to be run on WSL with a MKS CANable V2.0 Pro module connected to Windows
# The CAN module should be shared to WSL with usbipd-win

import can
import struct
from time import sleep

def sendMsg(dest_id: int, data: bytearray) -> int:
	"""Send a CAN message to the raspberry pi

	Args:
		dest_id (int): the arbitration id of an encoder
		data (bytearray): 8 bytes of data

	Returns:
		int: 1 if the message could not be sent, 0 otherwise
	"""        
	msg = can.Message(arbitration_id=dest_id,
				data=data,
				is_extended_id=True,
				check=True)

	try:
		bus.send(msg)
		print("Message sent on {}".format(bus.channel_info))
		return 0
	except can.CanError:
		print("Message NOT sent")
		return 1
	except Exception as e:
		print("Unknown error : "  + e)
		raise

def sendAngle(axis_id: int, angle: float) -> int:
	"""Send a command to the raspberry pi to give the current motor angle.

	Args:
		axis_id (int): the CAN id of an encoder
		angle (float): the angle in radians of the motor

	Returns:
		int: 1 if the command failed, 0 otherwise
	"""
	ba = bytearray(struct.pack("d", angle)) # Using double : 8 bytes
	print(f"{ba.hex(':')} ({angle})") # Prints as '40:45:35:c2:8f:5c:28:f6 (42.420000)'
	return sendMsg(axis_id, ba)
		
		
with can.interface.Bus(bustype='slcan', channel='/dev/ttyACM0', bitrate=500000) as bus:

	def _parse_data(msg: can.Message) -> None:
		angle = struct.unpack('d', msg.data)[0]
		print(f"{msg.arbitration_id} : {msg.data} = {angle}")

	notifier = can.Notifier(bus, [_parse_data])
	
	while(True):
		# Say to the raspberry pi that the encoder toggles between 0.78 an d1.2 rad
		sleep(2)
		sendAngle(0x1, 0.78)
		sendAngle(0x2, 0.78)
		sendAngle(0x3, 0.78)
		sleep(2)
		sendAngle(0x1, 1.2)
		sendAngle(0x2, 1.2)
		sendAngle(0x3, 1.2)
