from opentrons import protocol_api

# Simulate the protocol by running
# opentrons_simulate -L CUSTOM_LABWARE_DIR IHC-protocol.py

metadata = {
            'protocolName': 'IHC example protocol',
            'description': 'OT-2 protocol for immunohistochemistry staining using two 8-well slide chambers and'
                           'different antibodies.',
            'author': 'Franziska Niemeyer'}
requirements = {"robotType": "OT-2", 'apiLevel': '2.18'}

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Number of slides loaded into each physical box (0 = box not used)
BOX_SIZES = {
    'box1': 8,
    'box2': 0,
}

# Wash volume in µl used for all TBST steps
WASH_VOLUME = 100

# Negative control slides (0-indexed, counting across box1 then box2)
# These receive NGS instead of a primary antibody.
NEG_CONTROL_SLIDES = [0, 1]

# Primary antibody definitions.
# Each entry maps an antibody name to:
#   - 'description': label shown in the Opentrons app
#   - 'slides': 0-indexed slide numbers that receive this antibody
#   - 'color': hex display color for the liquid tracker
#   - 'eppie_well': position in the Eppendorf tube rack (eppie)
ANTIBODIES = [
    {
        'name':        'NKX3-1',
        'description': 'NKX3-1 antibody 1:250',
        'slides':      [2, 3],
        'color':       '#1475BF',
        'eppie_well':  'A3',
    },
    {
        'name':        'P63',
        'description': 'P63 antibody 1:500',
        'slides':      [4, 5],
        'color':       '#2D7290',
        'eppie_well':  'B3',
    },
    {
        'name':        'ERG',
        'description': 'ERG antibody 1:200',
        'slides':      [6, 7],
        'color':       '#214270',
        'eppie_well':  'A4',
    },
]

# Reagent locations
REAGENT_WELLS = {
    'ngs':       'A1',   # Eppendorf rack
    'h2o2':      'B1',   # Eppendorf rack
    'secondary': 'A2',   # Eppendorf rack
    'tbst':      'A3',   # Falcon rack (50 ml tube)
}

# ==============================================================================
# END OF CONFIGURATION
# ==============================================================================


def add_reagent(pipette, source_well, target_wells, n_repetitions, volume, incubation_minutes, protocol, incubation_seconds=0):
    """
    Function for washing steps. Requires pipette, source well, target wells (as a list from wells() function, how many
    slides/wells are used, how much should be pipetted, and the protocol.

    n_repetitions: how many times this step should be repeated
    volume: how much should be pipetted
    incubation_time: how long to incubate in between washes
    """
    if isinstance(target_wells, protocol_api.labware.Well):
        target_wells = [target_wells]
    source_well[1] -= n_repetitions * volume * len(target_wells)

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
    if isinstance(target_wells, protocol_api.labware.Well):
        target_wells = [target_wells]
    source_well[1] -= volume * len(target_wells)

    pipette.distribute(volume, source_well[0], target_wells,
                       new_tip="once",
                       blow_out=True,
                       blowout_location="source well",
                       disposal_vol=0,
                       airgap=10)

    return source_well


def run(protocol: protocol_api.ProtocolContext):

    # Derived slide counts
    n_slides_box1 = BOX_SIZES['box1']
    n_slides_box2 = BOX_SIZES['box2']
    num_slides = n_slides_box1 + n_slides_box2
    num_neg_controls = len(NEG_CONTROL_SLIDES)

    # Load labware
    tips = protocol.load_labware('opentrons_96_tiprack_1000ul', 8)
    slide_rack1 = protocol.load_labware('stainchambertest_8well', 1, '8 well stain chamber')
    if n_slides_box2 > 0:
        slide_rack2 = protocol.load_labware('stainchambertest_8well', 4, '8 well stain chamber')
    eppie = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 2)
    falcon = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 3)

    # Load instruments
    pipette = protocol.load_instrument('p1000_single_gen2', 'right', tip_racks=[tips])

    # Build a flat, ordered list of all destination wells
    all_wells = slide_rack1.wells()[:n_slides_box1]
    if n_slides_box2 > 0:
        all_wells += slide_rack2.wells()[:n_slides_box2]

    dest_wells_all = all_wells
    slides_neg_control = [all_wells[i] for i in NEG_CONTROL_SLIDES]

    # Resolve antibody wells from the ANTIBODIES config
    for ab in ANTIBODIES:
        ab['_wells'] = [all_wells[i] for i in ab['slides']]

    # Print slide layout summary
    print()
    print(f"Negative control slides (indices {NEG_CONTROL_SLIDES}): {slides_neg_control}")
    for ab in ANTIBODIES:
        print(f"Antibody '{ab['name']}' slides (indices {ab['slides']}): {ab['_wells']}")
    print()

    # Define liquids
    h2o2_liquid      = protocol.define_liquid(name='H2O2',
                                              description='Hydrogen peroxide for blocking',
                                              display_color='#2CB4CF')
    ngs_liquid       = protocol.define_liquid(name='NGS',
                                              description='Normal Goat Serum for blocking',
                                              display_color='#00FF55')
    secondary_liquid = protocol.define_liquid(name='Secondary antibody',
                                              description='Rabbit HRP',
                                              display_color='#9DBC98')
    tbst_liquid      = protocol.define_liquid(name='TBST',
                                              description='Wash buffer',
                                              display_color='#720455')

    for ab in ANTIBODIES:
        ab['_liquid'] = protocol.define_liquid(name=ab['name'],
                                               description=ab['description'],
                                               display_color=ab['color'])

    # Compute initial volumes
    h2o2_init      = (num_slides * 100) + 100
    ngs_init       = (num_slides * 100) + (num_neg_controls * 100) + 100
    secondary_init = (num_slides * 100) + 100
    tbst_init      = (num_slides * 1600) + 100    # assuming a 50 ml tube

    for ab in ANTIBODIES:
        ab['_init_vol'] = (len(ab['slides']) * 100) + 100

    print('Initial volumes:')
    print(f'  H2O2:         {h2o2_init} µl')
    print(f'  NGS:          {ngs_init} µl')
    print(f'  Secondary:    {secondary_init} µl')
    print(f'  TBST:         {tbst_init} µl')
    for ab in ANTIBODIES:
        print(f"  {ab['name']}: {ab['_init_vol']} µl")
    print()

    # Assign reagent source wells
    h2o2      = [eppie[REAGENT_WELLS['h2o2']],      h2o2_init]
    ngs       = [eppie[REAGENT_WELLS['ngs']],       ngs_init]
    secondary = [eppie[REAGENT_WELLS['secondary']], secondary_init]
    tbst      = [falcon[REAGENT_WELLS['tbst']],     tbst_init]

    for ab in ANTIBODIES:
        ab['_source'] = [eppie[ab['eppie_well']], ab['_init_vol']]

    # Load liquids into wells
    h2o2[0].load_liquid(liquid=h2o2_liquid,           volume=h2o2[1])
    ngs[0].load_liquid(liquid=ngs_liquid,             volume=ngs[1])
    secondary[0].load_liquid(liquid=secondary_liquid, volume=secondary[1])
    tbst[0].load_liquid(liquid=tbst_liquid,           volume=tbst[1])

    for ab in ANTIBODIES:
        ab['_source'][0].load_liquid(liquid=ab['_liquid'], volume=ab['_source'][1])

    # ==========================================================================
    # PROTOCOL
    # (Deparaffinization and rehydration are done manually beforehand.)
    # ==========================================================================

    # Wash with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=dest_wells_all,
                       n_repetitions=4,
                       volume=WASH_VOLUME,
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    # Peroxidase block — 100 µl, 15 min
    h2o2 = add_reagent(pipette,
                       source_well=h2o2,
                       target_wells=dest_wells_all,
                       n_repetitions=1,
                       volume=100,
                       incubation_minutes=15,
                       protocol=protocol)

    # Wash with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=dest_wells_all,
                       n_repetitions=4,
                       volume=WASH_VOLUME,
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    # NGS block — 100 µl, 15 min
    ngs = add_reagent(pipette,
                      source_well=ngs,
                      target_wells=dest_wells_all,
                      n_repetitions=1,
                      volume=100,
                      incubation_minutes=15,
                      incubation_seconds=0,
                      protocol=protocol)

    # Primary antibodies — 100 µl each, then 60 min incubation
    for ab in ANTIBODIES:
        ab['_source'] = add_single_antibody(pipette,
                                            source_well=ab['_source'],
                                            target_wells=ab['_wells'],
                                            volume=100)
    # NGS as negative control
    ngs = add_single_antibody(pipette,
                              source_well=ngs,
                              target_wells=slides_neg_control,
                              volume=100)
    protocol.delay(minutes=60)

    # Wash with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=dest_wells_all,
                       n_repetitions=4,
                       incubation_minutes=0,
                       incubation_seconds=15,
                       volume=WASH_VOLUME,
                       protocol=protocol)

    # Secondary antibody — 100 µl, 30 min
    secondary = add_reagent(pipette,
                            source_well=secondary,
                            target_wells=dest_wells_all,
                            n_repetitions=1,
                            volume=100,
                            incubation_minutes=30,
                            protocol=protocol)

    # Wash with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=dest_wells_all,
                       n_repetitions=4,
                       volume=WASH_VOLUME,
                       incubation_minutes=0,
                       incubation_seconds=15,
                       protocol=protocol)

    # Final volumes
    print('Volumes left in tubes:')
    for ab in ANTIBODIES:
        print(f"  {ab['name']}: {ab['_source'][1]} µl")
    print(f'  Secondary:    {secondary[1]} µl')
    print(f'  H2O2:         {h2o2[1]} µl')
    print(f'  TBST:         {tbst[1]} µl')
    print(f'  NGS:          {ngs[1]} µl')
    print()
