from OT2Driver.opentrons_client import OpentronsClient

client = OpentronsClient("192.168.5.156", 31950)

client.change_lights_status(True)
print("Lights ON")

# client.change_lights_status(False)
# print("Lights OFF")