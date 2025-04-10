# #! /usr/bin/env python
# Uncomment this line and change the path to the Python version you want to use
# Version <= 3.9 !!

from opentrons import protocol_api
import json

# Metadata
metadata = {
    'apiLevel': '2.14',
    'protocolName': 'Hello World Botilein!',
    'author': 'Franziska Niemeyer',
    'description': 'A simple protocol to demonstrate pipetting with the OT-2.'
                   'It will transfer 10 µl liquid from one Eppendorf tube in well'
                   'A1 to the subsequent wells B1, C1, ... for the number of samples specified.',
}


def get_values(*names):
    _all_values = json.loads("""{"mnt10":"right","num_samps":1}""")
    return [_all_values[n] for n in names]


# Initialize the protocol
def run(protocol: protocol_api.ProtocolContext):
    [mnt10, num_samps] = get_values('mnt10', 'num_samps')

    # Load custom tip rack and pipette, using function 'load_labware_from_definition'
    # to load a custom labware definition in simutation mode only
    #
    # json_definition_file = "/Users/franziskaniemeyer/Downloads/HelloWorld-OT2/labware/tipone_96_diytiprack_10ul.json"
    # with open(json_definition_file) as labware_file:
    #     custom_tiprack_def = json.load(labware_file)
    # custom_tiprack_label = custom_tiprack_def.get('metadata', {}).get('displayName')
    # tips = protocol.load_labware_from_definition(custom_tiprack_def, '8', custom_tiprack_label)

    tips = protocol.load_labware('opentrons_96_tiprack_10ul', '8')
    pipette = protocol.load_instrument('p10_single', mnt10, tip_racks=[tips])

    # Load Eppi rack
    eppi_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')

    # -------------------------------------------------------------------------
    # Start of actual protocol
    # -------------------------------------------------------------------------

    # Define a liquid, only for API version 2.14 or higher
    # coffee = protocol.define_liquid(
    #     name="Coffee",
    #     description="Andrews coffee",
    #     display_color="#0000FF",
    # )

    source = eppi_rack['A1']
    # source.load_liquid(coffee, volume=1000)
    target_eppis = eppi_rack.wells()[1:num_samps+1]

    for dest in target_eppis:
        # Pick up a tip
        pipette.pick_up_tip()

        # Go to the tube and aspirate liquid
        pipette.aspirate(10, source.bottom(10))

        # Move to destination well and pipette up and down
        pipette.dispense(10, dest.bottom())
        pipette.aspirate(5, dest.bottom())
        pipette.dispense(5, dest.bottom())

        # Blow out remaining liquid and touch tip to the side of the well
        pipette.blow_out()
        pipette.touch_tip(dest, v_offset=-2)

        # Drop the tip
        pipette.drop_tip()
