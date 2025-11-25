from opentrons import protocol_api

# Simulate the protocol by running
# opentrons_simulate -L CUSTOM_LABWARE_DIR IHC-protocol.py

metadata = {
            'protocolName': 'One cycle - full protocol',
            'description': 'OT-2 protocol for immunohistochemistry staining using one 6-well slide chamber',
            'author': 'Franziska Niemeyer'}
requirements = {"robotType": "OT-2", 'apiLevel': '2.18'}

parameters = {
    'n_slides_box1': 2,
    'n_slides_box2': 0,
    'n_slides_box3': 0,
    'wash_volume': 100,
    'name_antibody1': 'CK8',
    'description_antibody1': 'Cytokeratin-8 antibody 1:200'
}

num_slides = parameters['n_slides_box1'] + parameters['n_slides_box2'] + parameters['n_slides_box3']
number_antibodies = 1
num_neg_controls = 1    # slides without primary antibody, only NGS

# Define initial volumes for each liquid
h2o2_init = (num_slides * 100) + 100
ngs_init = (num_slides * 100) + 100
# trypsin_1_1_init = 300  # for dilution 1:1
# trypsin_1_3_init = 300  # for dilution 1:3
antibody1_init = (num_slides * 100) + 100 if num_neg_controls == 0 else (num_slides * 100) + 100 - (100 * num_neg_controls)
secondary_init = (num_slides * 100) + 100
tbst_init = (num_slides * 1600) + 100    # assuming a 50ml tube

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


def add_single_antibody(pipette, source_well, target_wells, volume):
    """
    Attention: Requires adding the incubation time after!!
    Adding antibody to the slides. Requires pipette, source wells, how many slides to treat, the volume to be
    pipetted, how long to incubate.
    """
    source_well[1] -= volume * (1 if type(target_wells) == protocol_api.labware.Well else len(target_wells))

    pipette.distribute(volume, source_well[0], target_wells,
                       new_tip="once",
                       blow_out=True,
                       blowout_location="source well",
                       disposal_vol=0,
                       airgap=10)

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
    h2o2_liquid = protocol.define_liquid(name='H2O2',
                                         description='Hydrogen peroxide for blocking',
                                         display_color='#0000FF')
    ngs_liquid = protocol.define_liquid(name='NGS',
                                        description='Normal Goat Serum for blocking',
                                        display_color='#00FF55')
    # trypsin_1_1_liquid = protocol.define_liquid(name='Trypsin 1:1',
    #                                      description='Trypsin for enzymatic antigen retrieval',
    #                                      display_color='#FFA500')
    # trypsin_1_3_liquid = protocol.define_liquid(name='Trypsin 1:3',
    #                                      description='Trypsin for enzymatic antigen retrieval',
    #                                      display_color='#00A560')
    antibody1_liquid = protocol.define_liquid(name=parameters['name_antibody1'],
                                             description=parameters['description_antibody1'],
                                             display_color='#00FF00')
    # antibody2_liquid = protocol.define_liquid(name=parameters['name_antibody2'],
    #                                          description=parameters['description_antibody2'],
    #                                          display_color='#FFFF00')
    tbst_liquid = protocol.define_liquid(name='TBST',
                                         description='Wash buffer',
                                         display_color='#720455')
    secondary_liquid = protocol.define_liquid(name='Secondary antibody',
                                              description='Rabbit HRP',
                                              display_color='#9DBC98')

    antibody1 = [eppie['A1'], antibody1_init]
    # antibody2 = [eppie['A2'], antibody2_init]

    secondary = [falcon['A1'], secondary_init]
    h2o2 = [falcon['A2'], h2o2_init]
    ngs = [falcon['B1'], ngs_init]

    tbst = [falcon['A3'], tbst_init]

    # load liquids
    h2o2[0].load_liquid(liquid=h2o2_liquid, volume=h2o2[1])
    ngs[0].load_liquid(liquid=ngs_liquid, volume=ngs[1])
    antibody1[0].load_liquid(liquid=antibody1_liquid, volume=antibody1[1])
    # antibody2[0].load_liquid(liquid=antibody2_liquid, volume=antibody2[1])
    secondary[0].load_liquid(liquid=secondary_liquid, volume=secondary[1])
    tbst[0].load_liquid(liquid=tbst_liquid, volume=tbst[1])

    dest_wells_box1 = slide_rack1.wells()[:parameters['n_slides_box1']]
    dest_wells_box2 = slide_rack2.wells()[:parameters['n_slides_box2']]
    dest_wells_box3 = slide_rack3.wells()[:parameters['n_slides_box3']]

    # Define which wells are used for what
    control_slides_box_1 = slide_rack1.wells('A1')
    ck8_ab_slides_box_1 = slide_rack1.wells('B1')
    # p63_ab_slides_box_1 = slide_rack1.wells('B3', 'A4', 'B4')

    # control_slides_box_2 = slide_rack2.wells('A1', 'A2', 'B4')
    # p63_ab_slides_box_2 = slide_rack2.wells('B1', 'B2', 'B3', 'A3', 'A4')

    # nkx_ab_slides_box_3 = slide_rack3.wells('A1', 'B1', 'A2', 'B2')

    # ====== proceed to protocol =======

    # wash step with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=4,
                       volume=parameters['wash_volume'],
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    # peroxidase block 100 ul, 15 minutes
    h2o2 = add_reagent(pipette,
                       source_well=h2o2,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=1,
                       volume=100,
                       incubation_minutes=15,
                       protocol=protocol)

    # wash step with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=4,
                       volume=parameters['wash_volume'],
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    # NGS block
    ngs = add_reagent(pipette,
                      source_well=ngs,
                      target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                      n_repetitions=1,
                      volume=100,
                      incubation_minutes=15,
                      incubation_seconds=0,
                      protocol=protocol)

    # primary antibody 100 ul, 60 minutes
    antibody1 = add_single_antibody(pipette,
                                    source_well=antibody1,
                                    target_wells=[ck8_ab_slides_box_1],
                                    volume=100)
    # antibody2 = add_single_antibody(pipette,
    #                                 source_well=antibody2,
    #                                 target_wells=[p63_ab_slides_box_1, p63_ab_slides_box_2],
    #                                 volume=100)

    # NGS as negative control
    ngs = add_single_antibody(pipette,
                              source_well=ngs,
                              target_wells=[control_slides_box_1],
                              volume=100)
    protocol.delay(minutes=60)

    # wash step with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=4,
                       incubation_minutes=0,
                       incubation_seconds=15,
                       volume=parameters['wash_volume'],
                       protocol=protocol)

    # secondary antibody 100 ul, 30 min
    secondary = add_reagent(pipette,
                            source_well=secondary,
                            target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                            n_repetitions=1,
                            volume=100,
                            incubation_minutes=30,
                            protocol=protocol)

    # wash step TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=4,
                       volume=parameters['wash_volume'],
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    print('Volumes left in tubes:')
    print(f'Antibody 1: {antibody1[1]}')
    # print(f'Antibody 2: {antibody2[1]}')
    print(f'Secondary: {secondary[1]}')
    print(f'H2O2: {h2o2[1]}')
    print(f'TBST: {tbst[1]}')
    # print(f'Trypsin 1:1: {trypsin_1_1[1]}')
    # print(f'Trypsin 1:3: {trypsin_1_3[1]}')
    print(f'NGS: {ngs[1]}')
