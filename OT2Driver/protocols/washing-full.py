from opentrons import protocol_api
import json

# opentrons_simulate -L CUSTOM_LABWARE_DIR IHC-protocol.py

metadata = {"apiLevel": "2.22"}

parameters = {
    'n_slides_box1': 2,
    'n_slides_box2': 0,
    'wash_volume': 100
}

num_slides = parameters['n_slides_box1'] + parameters['n_slides_box2']

# ======= liquids =======

# Define initional volumes for each liquid
milliq_init = (num_slides * 2 * parameters['wash_volume']) + parameters['wash_volume']
eth70_init = (num_slides * 4 * parameters['wash_volume']) + parameters['wash_volume']
eth96_init = (num_slides * 8 * parameters['wash_volume']) + parameters['wash_volume']
tbst_init = (num_slides * 6 * parameters['wash_volume']) + 100    # assuming a 50ml tube


# ======= functions =======
def add_reagent(pipette, source_well, target_wells, n_repetitions, volume, incubation_minutes, protocol, incubation_seconds=0):
    """
    Function for washing steps. Requires pipette, source well, target wells (as a list from wells() function, how many
    slides/wells are used, how much should be pipetted, and the protocol.

    n_repetitions: how many times this step should be repeated
    volume: how much should be pipetted
    incubation_time: how long to incubate in between washes
    """
    source_well[1] -= n_repetitions * volume * (1 if type(target_wells) == protocol_api.labware.Well else len(target_wells))

    pipette.pick_up_tip()
    for _ in range(n_repetitions):
        pipette.distribute(volume, source_well[0], target_wells,
                           new_tip="never",
                           blow_out=True,
                           blowout_location="source well",
                           disposal_vol=0,
                           airgap=10)
        protocol.delay(minutes=incubation_minutes, seconds=incubation_seconds)
    pipette.drop_tip()

    return source_well


def run(protocol: protocol_api.ProtocolContext):

    # load labware
    tips = protocol.load_labware('opentrons_96_tiprack_1000ul', 8)
    slide_rack1 = protocol.load_labware('stainchambertest_8well', 1, '8 well stain chamber')
    slide_rack2 = protocol.load_labware('stainchambertest_8well', 4, '8 well stain chamber')
    slide_rack3 = protocol.load_labware('stainchambertest_8well', 7, '8 well stain chamber')
    eppie = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 2)
    falcon = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 3)

    # load instruments
    pipette = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips])

    # define liquids used
    milliq_liquid = protocol.define_liquid(name='MilliQ Water',
                                           description='MilliQ water',
                                           display_color='#00000F')
    eth96_liquid = protocol.define_liquid(name='96% Ethanol',
                                          description='Ethanol 96%',
                                          display_color='#0304FF')
    eth70_liquid = protocol.define_liquid(name='70% Ethanol',
                                          description='Ethanol 70%',
                                          display_color='#0305FF')
    tbst_liquid = protocol.define_liquid(name='TBST',
                                         description='Wash buffer',
                                         display_color='#720455')

    milliq = [eppie['A2'], milliq_init]
    eth96 = [eppie['A5'], eth96_init]
    eth70 = [eppie['A6'], eth70_init]

    # load liquids
    milliq[0].load_liquid(liquid=milliq_liquid, volume=milliq[1])
    eth96[0].load_liquid(liquid=eth96_liquid, volume=eth96[1])
    eth70[0].load_liquid(liquid=eth70_liquid, volume=eth70[1])

    dest_wells_box1 = slide_rack1.wells()[:parameters['n_slides_box1']]
    dest_wells_box2 = slide_rack2.wells()[:parameters['n_slides_box2']]
    dest_wells_box3 = slide_rack3.wells()[:parameters['n_slides_box3']]

    # ====== proceed to protocol =======

    # Wash
    eth70 = add_reagent(pipette,
                       source_well=eth70,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=1,
                       volume=parameters['wash_volume'],
                       incubation_minutes=2,
                       protocol=protocol)
    eth96 = add_reagent(pipette,
                       source_well=eth96,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=1,
                       volume=parameters['wash_volume'],
                       incubation_minutes=1,
                       protocol=protocol)
    eth70 = add_reagent(pipette,
                       source_well=eth70,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=1,
                       volume=parameters['wash_volume'],
                       incubation_minutes=2,
                       protocol=protocol)

    print('Volumes left in tubes:\n')
    print(f'MilliQ\n'
          f'Initially: {milliq_init}\n'
          f'Remaining: {milliq[1]}\n')
    print(f'Eth96\n'
          f'Initially: {eth96_init}\n'
          f'Remaining: {eth96[1]}\n')
    print(f'Eth70\n'
          f'Initially: {eth70_init}\n'
          f'Remaining: {eth70[1]}\n')

