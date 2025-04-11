from opentrons import protocol_api

metadata = {"apiLevel": "2.22"}

parameters = {
    'n_slides_box1': 2,
    'n_slides_box2': 4,
    'wash_volume': 100,
    'name_antibody1': 'ERG',
    'description_antibody1': 'ERG antibody 1:300',
    'name_antibody2': 'CK8',
    'description_antibody2': 'Cytokeratin-8 antibody 1:200',
    'name_antibody5': 'P63-PTEN Dual',
    'description_antibody5': 'P63 1:500, PTEN 1:50'
}

num_slides = parameters['n_slides_box1'] + parameters['n_slides_box2']
number_antibodies = 3


# ====== labware ========

staining_jar = {
    "ordering": [
        [
            "A1",
            "B1"
        ],
        [
            "A2",
            "B2"
        ],
        [
            "A3",
            "B3"
        ],
        [
            "A4",
            "B4"
        ]
    ],
    "brand": {
        "brand": "Custom",
        "brandId": [
            "Custom"
        ]
    },
    "metadata": {
        "displayName": "StainChamberTest",
        "displayCategory": "wellPlate",
        "displayVolumeUnits": "µL",
        "tags": []
    },
    "dimensions": {
        "xDimension": 127.76,
        "yDimension": 85.47,
        "zDimension": 110
    },
    "wells": {
        "A1": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 15,
            "y": 64.47,
            "z": 100
        },
        "B1": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 15,
            "y": 19.47,
            "z": 100
        },
        "A2": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 40,
            "y": 64.47,
            "z": 100
        },
        "B2": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 40,
            "y": 19.47,
            "z": 100
        },
        "A3": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 65,
            "y": 64.47,
            "z": 100
        },
        "B3": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 65,
            "y": 19.47,
            "z": 100
        },
        "A4": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 90,
            "y": 64.47,
            "z": 100
        },
        "B4": {
            "depth": 10,
            "totalLiquidVolume": 10000,
            "shape": "rectangular",
            "xDimension": 10,
            "yDimension": 20,
            "x": 90,
            "y": 19.47,
            "z": 100
        }
    },
    "groups": [
        {
            "metadata": {
                "wellBottomShape": "flat"
            },
            "wells": [
                "A1",
                "B1",
                "A2",
                "B2",
                "A3",
                "B3",
                "A4",
                "B4"
            ]
        }
    ],
    "parameters": {
        "format": "irregular",
        "quirks": [],
        "isTiprack": False,
        "isMagneticModuleCompatible": False,
        "loadName": "stainchambertest_8well"
    },
    "namespace": "custom_beta",
    "version": 1,
    "schemaVersion": 2,
    "cornerOffsetFromSlot": {
        "x": 0,
        "y": 0,
        "z": 0
    }
}

# ======= liquids =======

# Define initional volumes for each liquid
h2o2_init = (num_slides * 100) + 100
antibody1_init = 1500
antibody2_init = 1500
antibody5_init = 1500
secondary_init = (num_slides * 100) + 100
tbst_init = (num_slides * 1600) + 100    # assuming a 50ml tube


# ====== functions ======

def calculate_aspirate_height(volume, total_volume, tube_height, min_height=1):
    """
    Calculate the aspiration height based on the remaining volume in the tube.
    """
    if volume <= 0:
        return min_height  # Avoid going too low, minimum height
    height = (volume / total_volume) * tube_height
    return max(min_height, height)


def add_reagent(pipette, source_well, target_wells, n_repetitions, volume, incubation_minutes, protocol, incubation_seconds=0):
    """
    Function for washing steps. Requires pipette, source well, target wells (as a list from wells() function, how many
    slides/wells are used, what volume is to be transferred, and the protocol.

    n_repetitions: how many times this step should be repeated
    volume: how much should be aspirated and dispensed
    incubation_time: how long to incubate in between washes
    """
    source_well[1] -= volume * n_repetitions * len(target_wells)
    if source_well[1] <= 0:
        raise ValueError(f'Not enough liquid in source well {source_well[0].well_name} left.')

    pipette.pick_up_tip()
    for _ in range(n_repetitions):
        aspirate_height = calculate_aspirate_height(source_well[1], source_well[2], source_well[0].depth)
        volume_to_aspirate = volume * len(target_wells) + 10
        if volume_to_aspirate > pipette.max_volume:
            raise ValueError(f'Volume to aspirate ({volume_to_aspirate}) is too high for the pipette.')
            # TODO: Adjust to aspirate as much as possible, later coming back to aspirate and dispense the rest
        pipette.aspirate(volume_to_aspirate, source_well[0].bottom(z=aspirate_height))
        for well in target_wells:
            pipette.dispense(volume, well[0])
        pipette.blow_out(source_well[0].top())
        protocol.delay(minutes=incubation_minutes, seconds=incubation_seconds)
    pipette.drop_tip()
    # TODO: well locations to aspirate from

    return source_well


def add_single_antibody(pipette, source_well, target_wells, volume):
    """
    Attention: Requires adding the incubation time after!!
    Adding antibody to the slides. Requires pipette, source wells, how many slides to treat, the volume to be
    aspirated and dispensed, and how long to incubate.
    """
    source_well[1] -= volume
    if source_well[1] <= 0:
        raise ValueError(f'Not enough liquid in source well {source_well[0].well_name} left.')

    pipette.pick_up_tip()
    volume_to_aspirate = volume * len(target_wells) + 10
    aspirate_height = calculate_aspirate_height(source_well[1], source_well[2], source_well[0].depth)
    pipette.aspirate(volume_to_aspirate, source_well[0].bottom(z=aspirate_height))
    for well in target_wells:
        pipette.dispense(volume, well)
    pipette.blow_out(source_well[0].top())
    pipette.drop_tip()

    return source_well


def run(protocol: protocol_api.ProtocolContext):

    # load labware
    tips = protocol.load_labware('opentrons_96_tiprack_1000ul', 8)
    slide_rack1 = protocol.load_labware_from_definition(staining_jar, 1, '8 well stain chamber')
    slide_rack2 = protocol.load_labware_from_definition(staining_jar, 4, '8 well stain chamber')
    eppie = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', 2)
    falcon = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 3)

    # load instruments
    pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tips])

    # define liquids used
    h2o2_liquid = protocol.define_liquid(name='H2O2',
                                         description='Hydrogen peroxide for blocking',
                                         display_color='#0000FF')
    antibody1_liquid = protocol.define_liquid(name=parameters['name_antibody1'],
                                              description=parameters['description_antibody1'],
                                              display_color='#00FF00')
    antibody2_liquid = protocol.define_liquid(name=parameters['name_antibody2'],
                                              description=parameters['description_antibody2'],
                                              display_color='#00FF40')
    antibody5_liquid = protocol.define_liquid(name=parameters['name_antibody5'],
                                              description=parameters['description_antibody5'],
                                              display_color='#00FF89')
    tbst_liquid = protocol.define_liquid(name='TBST',
                                         description='Wash buffer',
                                         display_color='#720455')
    secondary_liquid = protocol.define_liquid(name='Secondary antibody',
                                              description='Rabbit HRP',
                                              display_color='#9DBC98')

    # [tube, current volume, initial volume]
    h2o2 = [eppie['A5'], h2o2_init, h2o2_init]
    antibody1 = [eppie['A1'], antibody1_init, antibody1_init]
    antibody2 = [eppie['B1'], antibody2_init, antibody2_init]
    antibody5 = [eppie['C1'], antibody5_init, antibody5_init]
    secondary = [eppie['A3'], secondary_init, secondary_init]
    tbst = [falcon['A3'], tbst_init, tbst_init]

    # load liquids
    h2o2[0].load_liquid(liquid=h2o2_liquid, volume=h2o2[2])
    antibody1[0].load_liquid(liquid=antibody1_liquid, volume=antibody1[2])
    antibody2[0].load_liquid(liquid=antibody2_liquid, volume=antibody2[2])
    antibody5[0].load_liquid(liquid=antibody5_liquid, volume=antibody5[2])
    secondary[0].load_liquid(liquid=secondary_liquid, volume=secondary[2])
    tbst[0].load_liquid(liquid=tbst_liquid, volume=tbst[2])

    dest_wells_box1 = slide_rack1.wells()[:parameters['n_slides_box1']]
    dest_wells_box2 = slide_rack2.wells()[:parameters['n_slides_box2']]

    # ====== proceed to protocol =======

    # wash step with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2],
                       n_repetitions=4,
                       volume=parameters['wash_volume'],
                       incubation_minutes=0,
                       incubation_seconds=30,
                       protocol=protocol)

    # peroxidase block 100 ul, 15 minutes
    h2o2 = add_reagent(pipette,
                       source_well=h2o2,
                       target_wells=[dest_wells_box1, dest_wells_box2],
                       n_repetitions=1,
                       volume=100,
                       incubation_minutes=15,
                       protocol=protocol)

    # wash step with TBST
    tbst = add_reagent(pipette,
                       source_well=tbst,
                       target_wells=[dest_wells_box1, dest_wells_box2],
                       n_repetitions=4,
                       volume=parameters['wash_volume'],
                       incubation_minutes=0,
                       incubation_seconds=30,
                       protocol=protocol)

    # primary antibody 100 ul, 60 minutes
    antibody1 = add_single_antibody(pipette,
                                    source_well=antibody1,
                                    target_wells=[dest_wells_box1[1]],
                                    volume=100)
    antibody2 = add_single_antibody(pipette,
                                    source_well=antibody2,
                                    target_wells=[dest_wells_box1[0]],
                                    volume=100)
    antibody5 = add_single_antibody(pipette,
                                    source_well=antibody5,
                                    target_wells=dest_wells_box2,
                                    volume=100)
