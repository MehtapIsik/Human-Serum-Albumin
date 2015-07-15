#! /usr/bin/env python
"""
Script for generation of input files for Aspirin and Naproxen binding to HSA by ITC.
"""

from itctools.itctools import ureg, Quantity
from itctools.procedures import ITCProtocol, ITCExperimentSet, ITCExperiment, ITCHeuristicExperiment
from itctools.materials import Solvent, Compound, SimpleSolution
from itctools.labware import Labware, PipettingLocation
import pprint


## Is this volume correct? I can try adding units.

# The sample cell volume in microliters
cell_volume = 202.8

# Define solvents.
water = Solvent('water', density=0.9970479 * ureg.gram / ureg.milliliter)
buffer = Solvent('buffer', density=1.014 * ureg.gram / ureg.milliliter) # TODO is our density the same as the HOST-GUEST buffer?

# Define compounds.
hsa = Compound('HumanSerumAlbumin', molecular_weight=65000 * (ureg.gram / ureg.mole), purity=.95)
naproxen_sodium = Compound('Naproxen Sodium', molecular_weight=252.24 * (ureg.gram / ureg.mole), purity=1.)


## Aspirin can be insoluble? Are we using its salt?

# These are insoluble in water without added DMSO
aspirin = Compound('AcetylsalicylicAcid', molecular_weight=180.15742 * (ureg.gram / ureg.mole), purity=.99)
# naproxen = Compound('Naproxen', molecular_weight=230.3 * (ureg.gram / ureg.mole), purity=.98)

#Ka (association constants) TODO Add this to the compound properties? (maybe a dict with protein as key)
aspirin_ka = 547198.10 / ureg.molar  # http://omicsonline.org/2157-7544/2157-7544-2-107.pdf first site estimate
naproxen_ka = 1.7 / (10 * ureg.micromolar)  # http://pubs.acs.org/doi/pdf/10.1021/jp062734p

# Define troughs on the instrument
water_trough = Labware(RackLabel='Water', RackType='Trough 100ml')
buffer_trough = Labware(RackLabel='Buffer', RackType='Trough 100ml')

# Define source labware.
source_plate = Labware(RackLabel='SourcePlate', RackType='5x3 Vial Holder')

# Define source solutions in the vial holder
# TODO : Define solutions once prepared with the Quantos
# hsa_solution = SimpleSolution(compound=hsa, compound_mass=13.8 * ureg.milligram, solvent=buffer, solvent_mass=0.5 * ureg.gram, location=PipettingLocation(
#     source_plate.RackLabel,
#     source_plate.RackType,
#     1))

## what is compound mass?
## I updated compound mass and solvent mass values based on Bas's Dec 17, 2015 experiment. (hsa_short.py)

hsa_solution = SimpleSolution(compound=hsa, compound_mass=10.05014 * ureg.milligram, solvent=buffer, solvent_mass=3.4245 * ureg.gram, location=PipettingLocation(
    source_plate.RackLabel,
    source_plate.RackType,
    1))


## TODO : Enter compound mass and solvent mass values.
## I put 1's as place holders.

aspirin_solution = SimpleSolution(compound=aspirin, compound_mass= 1 * ureg.milligram, solvent=buffer, solvent_mass= 1 * ureg.gram, location=PipettingLocation(
    source_plate.RackLabel,
    source_plate.RackType,
    2
))

naproxen_sodium_solution = SimpleSolution(compound=naproxen_sodium, compound_mass=25.245 * ureg.milligram, solvent=buffer, solvent_mass=10.0728 * ureg.gram, location=PipettingLocation(
    source_plate.RackLabel,
    source_plate.RackType,
    3))


drugs = [aspirin, naproxen_sodium]
drug_solutions = [aspirin_solution, naproxen_sodium_solution]
drug_kas = [aspirin_ka, naproxen_ka]



# Define ITC protocol.

# Protocol for 'control' titrations (water-water, buffer-buffer,
# titrations into buffer, etc.)

control_protocol = ITCProtocol(
    'control_protocol',
    sample_prep_method='Plates Quick.setup',
    itc_method='ChoderaWaterWater.inj',
    analysis_method='Control',
    experimental_conditions=dict(target_temperature=25, equilibration_time=60, stir_rate=1000, reference_power=5),
    injections=[
        dict(volume_inj=0.2, duration_inj=0.4, spacing=60, filter_period=0.5)] +
        20 * [dict(volume_inj=1.5, duration_inj=6, spacing=120, filter_period=0.5)],
    )

# Protocol for 1:1 binding analysis
blank_protocol = ITCProtocol(
    '1:1 binding protocol',
    sample_prep_method='Chodera Load Cell Without Cleaning Cell After.setup',
    itc_method='ChoderaHSA20.inj',
    analysis_method='Onesite',
    experimental_conditions=dict(target_temperature=25, equilibration_time=300, stir_rate=1000, reference_power=5),
    injections=[
        dict(volume_inj=0.2, duration_inj=0.4, spacing=60, filter_period=0.5)] +
        20 * [dict(volume_inj=1.5, duration_inj=6, spacing=120, filter_period=0.5)],
    )


binding_protocol = ITCProtocol(
    '1:1 binding protocol',
    sample_prep_method='Plates Standart.setup',
    itc_method='ChoderaHSA20.inj',
    analysis_method='Onesite',
    experimental_conditions=dict(target_temperature=25, equilibration_time=300, stir_rate=1000, reference_power=5),
    injections=[
        dict(volume_inj=0.2, duration_inj=0.4, spacing=60, filter_period=0.5)] +
        20 * [dict(volume_inj=1.5, duration_inj=6, spacing=120, filter_period=0.5)],
    )
# Protocol for cleaning protocol
cleaning_protocol = ITCProtocol(
    'cleaning protocol',
    sample_prep_method='Plates Clean.setup',
    itc_method='ChoderaLHSA20.inj',
    analysis_method='Onesite',
    experimental_conditions=dict(target_temperature=25, equilibration_time=60, stir_rate=1000, reference_power=5),
    injections=5 * [
        dict(volume_inj=7.5, duration_inj=15, spacing=150, filter_period=5)],
    )

# Define ITC Experiment.

# use specified protocol by default
itc_experiment_set = ITCExperimentSet(name='Human Serum Albumin experiments')
# Add available plates for experiments.
itc_experiment_set.addDestinationPlate(
    Labware(
        RackLabel='DestinationPlate',
        RackType='ITC Plate'))
itc_experiment_set.addDestinationPlate(
    Labware(
        RackLabel='DestinationPlate2',
        RackType='ITC Plate'))

nreplicates = 1  # number of replicates of each experiment

## Cleaning experiment, buffer control titration and buffer into hsa was missing in Bas's experiment. Do we want to keep it?

# # Add cleaning experiment.
# name = 'initial cleaning water titration'
# itc_experiment_set.addExperiment(
#     ITCExperiment(
#         name=name,
#         syringe_source=water_trough,
#         cell_source=water_trough,
#         protocol=cleaning_protocol,
#         cell_volume=cell_volume))

# Add water control titrations.
for replicate in range(1):
    name = 'water into water %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=water_trough,
            cell_source=water_trough,
            protocol=control_protocol,
            cell_volume=cell_volume))

# # Add buffer control titrations.
# for replicate in range(1):
#     name = 'buffer into buffer %d' % (replicate + 1)
#     itc_experiment_set.addExperiment(
#         ITCExperiment(
#             name=name,
#             syringe_source=buffer_trough,
#             cell_source=buffer_trough,
#             protocol=control_protocol,
#             cell_volume=cell_volume))
#
# # buffer into hsa
# for replicate in range(1):
#     name = 'buffer into HSA %d' % (replicate + 1)
#     itc_experiment_set.addExperiment(
#         ITCExperiment(
#             name=name,
#             syringe_source=buffer_trough,
#             cell_source=hsa_solution,
#             protocol=control_protocol,
#             cell_concentration=0.045 * ureg.millimolar,
#             buffer_source=buffer_trough,
#             cell_volume=cell_volume))

# drugs/HSA
# scale cell concentration to fix necessary syringe concentrations

cell_scaling = 1.
for drug, drug_solution, drug_ka in zip(drugs, drug_solutions, drug_kas):

    # We need to store the experiments before adding them to the set
    drug_protein_experiments = list()
    drug_buffer_experiments = list()

    # Scaling factors per replicate
    factors = list()

    # Define drug to protein experiments.
    for replicate in range(1):
        name = '%s into HSA %d' % (drug.name, replicate + 1 )
        experiment = ITCHeuristicExperiment(
            name=name,
            syringe_source=drug_solution,
            cell_source=hsa_solution,
            protocol=binding_protocol,
            cell_concentration=0.040 *
            ureg.millimolar *
            cell_scaling,
            buffer_source=buffer_trough,
            cell_volume=cell_volume)
        # optimize the syringe_concentration using heuristic equations and known binding constants
        # TODO extract m, v and V0 from protocol somehow?

        # Warning, you're possibly not getting the setup you want. Consider not using the Heuristic Experiment
        experiment.heuristic_syringe(drug_ka, 10, strict=False)
        # rescale if syringe > stock. Store factor.
        factors.append(experiment.rescale())
        drug_protein_experiments.append(experiment)

    # Define drug into buffer
    for replicate in range(1):
        name = '%s into buffer  %d' % (drug.name, replicate + 1)
        experiment = ITCHeuristicExperiment(
            name=name,
            syringe_source=drug_solution,
            cell_source=buffer_trough,
            protocol=blank_protocol,
            buffer_source=buffer_trough,
            cell_volume=cell_volume)
        # rescale to match drug to protein experiment concentrations.
        experiment.rescale(tfactor=factors[replicate])
        drug_buffer_experiments.append(experiment)

    # TODO, since we are changing drugs, we'd have to wash the syringe.
    # Add drug to protein experiment(s) to set
    for drug_protein_experiment in drug_protein_experiments:
        itc_experiment_set.addExperiment(drug_protein_experiment)
        # pprint.pprint(drug_protein_experiment.__dict__)

    # Add drug_to_buffer experiment(s) to set
    for drug_buffer_experiment in drug_buffer_experiments:
        itc_experiment_set.addExperiment(drug_buffer_experiment)
        # pprint.pprint(drug_buffer_experiment.__dict__)


# Add cleaning experiment.
name = 'final cleaning water titration'
itc_experiment_set.addExperiment( ITCExperiment(name=name, syringe_source=water_trough, cell_source=water_trough, protocol=cleaning_protocol, cell_volume=cell_volume) )


## Do we want this final water into water experiment? Bas didn't have this?

# Water control titrations.
nfinal = 2
for replicate in range(nfinal):
    name = 'final water into water test %d' % (replicate + 1)
    itc_experiment_set.addExperiment(
        ITCExperiment(
            name=name,
            syringe_source=water_trough,
            cell_source=water_trough,
            protocol=control_protocol,
            cell_volume=cell_volume))

# Check that the experiment can be carried out using available solutions
# and plates.

itc_experiment_set.validate(print_volumes=True, omit_zeroes=True)

# For convenience, concentrations
for drug_solution in drug_solutions:
    print("%s %.4f mM" % (drug_solution.name, drug_solution.concentration / ureg.millimolar ))
    print("HSA", hsa_solution.concentration.to(ureg.millimolar))


# Write Tecan EVO pipetting operations.
worklist_filename = 'hsa_20150714_MI.gwl'
itc_experiment_set.writeTecanWorklist(worklist_filename)

# Write Auto iTC-200 experiment spreadsheet.
excel_filename = 'hsa_20150714_MI.xlsx'
itc_experiment_set.writeAutoITCExcel(excel_filename)
