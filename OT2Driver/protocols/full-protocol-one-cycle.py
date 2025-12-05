from opentrons import protocol_api

# Simulate the protocol by running
# opentrons_simulate -L CUSTOM_LABWARE_DIR IHC-protocol.py

metadata = {
            'protocolName': 'One cycle - full protocol',
            'description': 'OT-2 protocol for immunohistochemistry staining using an 8-well slide chamber. '
                           'This protocol does not include an antigen retrieval step, but it performs'
                           'deparaffinization of the slides.',
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
milliq_init = (num_slides * 2 * parameters['wash_volume']) + parameters['wash_volume']
xylene_init = (num_slides * 3 * parameters['wash_volume']) + parameters['wash_volume']
eth100_init = (num_slides * 3 * parameters['wash_volume']) + parameters['wash_volume']
eth96_init = (num_slides * 2 * parameters['wash_volume']) + parameters['wash_volume']
eth70_init = (num_slides * 1 * parameters['wash_volume']) + parameters['wash_volume']
h2o2_init = (num_slides * 1 * parameters['wash_volume']) + parameters['wash_volume']
ngs_init = (num_slides * 1 * parameters['wash_volume']) + parameters['wash_volume'] if num_neg_controls == 0\
    else (num_slides * parameters['wash_volume']) + (num_neg_controls * parameters['wash_volume']) + parameters['wash_volume']
antibody1_init = (num_slides * parameters['wash_volume']) + parameters['wash_volume'] if num_neg_controls == 0\
    else (num_slides * parameters['wash_volume']) + parameters['wash_volume'] - (parameters['wash_volume'] * num_neg_controls)
secondary_init = (num_slides * parameters['wash_volume']) + parameters['wash_volume']
tbst_init = (num_slides * 16 * parameters['wash_volume']) + parameters['wash_volume']    # assuming a 50ml tube
# trypsin_1_1_init = 300  # for dilution 1:1
# trypsin_1_3_init = 300  # for dilution 1:3

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
    milliq_liquid = protocol.define_liquid(name='MilliQ Water',
                                           description='MilliQ water',
                                           display_color='#00000F')
    xylene_liquid = protocol.define_liquid(name='Xylene',
                                           description='Xylene for deparaffinization',
                                           display_color='#0300FF')
    eth100_liquid = protocol.define_liquid(name='100% Ethanol',
                                           description='Ethanol 100%',
                                           display_color='#0303FF')
    eth96_liquid = protocol.define_liquid(name='96% Ethanol',
                                          description='Ethanol 96%',
                                          display_color='#0304FF')
    eth70_liquid = protocol.define_liquid(name='70% Ethanol',
                                          description='Ethanol 70%',
                                          display_color='#0305FF')
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
    milliq = [eppie['A2'], milliq_init]
    xylene = [eppie['A3'], xylene_init]
    eth100 = [eppie['A4'], eth100_init]
    eth96 = [eppie['A5'], eth96_init]
    eth70 = [eppie['A6'], eth70_init]
    h2o2 = [falcon['A2'], h2o2_init]
    ngs = [falcon['B1'], ngs_init]

    tbst = [falcon['A3'], tbst_init]

    # load liquids
    xylene[0].load_liquid(liquid=h2o2_liquid, volume=h2o2[1])
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

    # Deparaffinization
    xylene = add_reagent(pipette,
                       source_well=xylene,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=3,
                       volume=parameters['wash_volume'],
                       incubation_minutes=5,
                       protocol=protocol)
    eth100 = add_reagent(pipette,
                       source_well=eth100,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=3,
                       volume=parameters['wash_volume'],
                       incubation_minutes=1,
                       protocol=protocol)
    eth96 = add_reagent(pipette,
                       source_well=eth96,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=2,
                       volume=parameters['wash_volume'],
                       incubation_minutes=1,
                       protocol=protocol)
    eth70 = add_reagent(pipette,
                       source_well=eth70,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=1,
                       volume=parameters['wash_volume'],
                       incubation_minutes=1,
                       protocol=protocol)
    milliq = add_reagent(pipette,
                       source_well=milliq,
                       target_wells=[dest_wells_box1, dest_wells_box2, dest_wells_box3],
                       n_repetitions=2,
                       volume=parameters['wash_volume'],
                       incubation_minutes=1,
                       protocol=protocol)


    # Antigen retrieval?

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

    print('Volumes left in tubes:\n')
    print(f'Antibody 1\n'
          f'Initially: {antibody1_init}\n'
          f'Remaining: {antibody1[1]}\n')
    # print(f'Antibody 2: {antibody2[1]}')
    print(f'Secondary\n'
          f'Initially: {secondary_init}\n'
          f'Remaining: {secondary[1]}\n')
    print(f'MilliQ\n'
          f'Initially: {milliq_init}\n'
          f'Remaining: {milliq[1]}\n')
    print(f'Xylene\n'
          f'Initially: {xylene_init}\n'
          f'Remaining: {xylene[1]}\n')
    print(f'Eth100\n'
          f'Initially: {eth100_init}\n'
          f'Remaining: {eth100[1]}\n')
    print(f'Eth96\n'
          f'Initially: {eth96_init}\n'
          f'Remaining: {eth96[1]}\n')
    print(f'Eth70\n'
          f'Initially: {eth70_init}\n'
          f'Remaining: {eth70[1]}\n')
    print(f'H2O2\n'
          f'Initially: {h2o2_init}\n'
          f'Remaining: {h2o2[1]}\n')
    print(f'TBST\n'
          f'Initially: {tbst_init}\n'
          f'Remaining: {tbst[1]}\n')
    # print(f'Trypsin 1:1: {trypsin_1_1[1]}')
    # print(f'Trypsin 1:3: {trypsin_1_3[1]}')
    print(f'NGS\n'
          f'Initially: {ngs_init}\n'
          f'Remaining: {ngs[1]}\n')
