# main.py
from core.cli import DroneHunterCLI

if __name__ == "__main__":
    print("""
       
  _____                       _    _             _            
 |  __ \                     | |  | |           | |           
 | |  | |_ __ ___  _ __   ___| |__| |_   _ _ __ | |_ ___ _ __ 
 | |  | | '__/ _ \| '_ \ / _ \  __  | | | | '_ \| __/ _ \ '__|
 | |__| | | | (_) | | | |  __/ |  | | |_| | | | | ||  __/ |   
 |_____/|_|  \___/|_| |_|\___|_|  |_|\__,_|_| |_|\__\___|_|   
                                                              
                                                              
        
        """)
    print("DroneHunter Framework - Drone Exploitation Toolkit\n")
    cli = DroneHunterCLI()
    cli.start_cli()
