import os
from OT2Driver.opentrons_client import OpentronsClient

try:
    from dotenv import load_dotenv
    load_dotenv()
    ot_ip = os.getenv("OT2_IP", "169.254.254.239")
except ImportError:
    print("python-dotenv not found, using default OT2 IP address")
    ot_ip = "169.254.254.239"

client = OpentronsClient(ot_ip, 31950)

client.change_lights_status(True)
print("Lights ON")

# client.change_lights_status(False)
# print("Lights OFF")