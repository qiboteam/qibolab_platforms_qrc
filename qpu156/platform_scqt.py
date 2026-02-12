"""
Initialization script for TII QPOU156.

This initialization script is used to:

- Configure logging;
- Run basic common imports, such as numpy, matplotlib, and some SCQT modules;
- Specifying the hardware configuration;
- Connecting to instruments;
- Loading previous settings (if applicable);
- Setting up the quantum device
"""

# Configure logging
import logging

logger = logging.getLogger(__name__)
scqt_logger = logging.getLogger("superconducting_qubit_tools")
scqt_logger.setLevel(logging.INFO)

############################################
# 1. Basic imports
############################################


# 1.1 Generic python imports

import time

# for benchmarking purposes

import os
from pathlib import Path
from importlib import reload
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from IPython.display import display, SVG

# 1.2 SCQT and Quantify imports

from quantify.utilities.experiment_helpers import load_settings_onto_instrument
from quantify.data.handling import get_datadir, set_datadir

from superconducting_qubit_tools import measurement_functions as meas
from superconducting_qubit_tools import calibration_functions as cal

# 1.3 Instrument imports

from orangeqs.juice_ext.device_and_instruments.measurement_control.measurement_control import MeasurementControl
# import quantify.visualization.pyqt_plotmon as pqm
# from quantify.visualization.instrument_monitor import InstrumentMonitor
from quantify_scheduler.instrument_coordinator.instrument_coordinator import (
    InstrumentCoordinator,
)

from qcodes.instrument.base import Instrument
from quantify_scheduler.instrument_coordinator.components.generic import (
    GenericInstrumentCoordinatorComponent,
)

from superconducting_qubit_tools.device_under_test.quantum_device import QuantumDevice
from superconducting_qubit_tools.device_under_test.transmon_element import (
    BasicTransmonElement
)
from superconducting_qubit_tools.device_under_test.tunable_coupler_transmon_element import (
    TunableCouplerTransmonElement
)
from superconducting_qubit_tools.device_under_test.feedline_element import (
    FeedlineElement,
)
from superconducting_qubit_tools.device_under_test.sudden_nz_edge import SuddenNetZeroEdge
from superconducting_qubit_tools.automation.graph_generation import generate_calibration_graph

from orangeqs.juice_ext.device_and_instruments import new_run_id
from orangeqs.juice_ext.protocol_and_automation.graph import register_calibration_graph


#############################
# 2 configure basic settings
#############################

# set_datadir(os.path.join(Path.home(), "quantify-data"))
set_datadir(Path.home() / "shared" / "data" / "quantify")
# set_datadir_quantify(os.path.join(Path.home(), "quantify-data"))

#set_datadir(Path.home() / "quantify-data" / platform)
logger.info("Data directory set to: {}".format(get_datadir()))

HARDWARE_CFG_TII = {
    "config_type": "quantify_scheduler.backends.qblox_backend.QbloxHardwareCompilationConfig",
    "hardware_description": {
        "cluster0": {
            "instrument_type": "Cluster",
            "ref": "internal",
            "modules": {
                "7": {"instrument_type": "QCM_RF"},
                "8": {"instrument_type": "QCM_RF"},
                "9": {"instrument_type": "QCM_RF"},
                "16": {"instrument_type": "QCM"},
                "20": {"instrument_type": "QRM_RF"}
            },
        },
    },
    "hardware_options": {
        "modulation_frequencies": 
        {'q0:res-q0.ro': {'lo_freq': 6.45e9}, 
        'q1:res-q1.ro': {'lo_freq': 6.45e9},
        'q2:res-q2.ro': {'lo_freq': 6.45e9},
        'q3:res-q3.ro': {'lo_freq': 6.45e9},
        'q4:res-q4.ro': {'lo_freq': 6.45e9},
        'q0:mw-q0.01': {'lo_freq': 3.66e9},
        'q0:mw-q0.12': {'lo_freq': 3.66e9},
        'q1:mw-q1.01': {'lo_freq': 4.31e9},
        'q1:mw-q1.12': {'lo_freq': 4.31e9},
        'q2:mw-q0.01': {'lo_freq': 3.92e9},
        'q2:mw-q0.12': {'lo_freq': 3.92e9},
        'q3:mw-q0.01': {'lo_freq': 4.18e9},
        'q3:mw-q0.12': {'lo_freq': 4.18e9},
        'q4:mw-q0.01': {'lo_freq': 3.91e9},
        'q4:mw-q0.12': {'lo_freq': 3.91e9},
        },
    },
    "connectivity": {
        "graph": [
        ["cluster0.module9.complex_output_0", "q0:mw"],
        ["cluster0.module9.complex_output_1", "q1:mw"],
        ["cluster0.module8.complex_output_0", "q2:mw"],
        ["cluster0.module8.complex_output_1", "q3:mw"],
        ["cluster0.module7.complex_output_0", "q4:mw"],
        ["cluster0.module20.complex_output_0", "q0:res"],
        ["cluster0.module20.complex_output_0", "q1:res"],
        ["cluster0.module20.complex_output_0", "q2:res"],
        ["cluster0.module20.complex_output_0", "q3:res"],
        ["cluster0.module20.complex_output_0", "q4:res"],
        ["cluster0.module20.complex_output_0", "f0:in"],
        ["cluster0.module16.real_output_0", "c01:fl"],
        ["cluster0.module16.real_output_1", "c12:fl"], 
        ["cluster0.module16.real_output_2", "c23:fl"],
        ["cluster0.module16.real_output_3", "c34:fl"],
        ]
    },
}



#############################
# 3 Instantiate Instruments
#############################

# physical instruments
#############################
from qblox_instruments import Cluster

# Connect to the cluster
logger.info("Connecting to qblox-cluster-MM.")
cluster0 = Cluster("cluster0", "192.168.0.3")
print("\n!! cluster connected !!")
logger.info(f"CMM system status is {cluster0.get_system_status()}")
logger.info("Correctly connected to qblox-cluster-MM.")
# Reset and set propragation delay compensations
# cluster0.reset()
for module in cluster0.modules:
    for sequencer in module.sequencers:
        sequencer.nco_prop_delay_comp_en(True)


# hardware abstraction layer
#############################
from quantify_scheduler.instrument_coordinator.components.qblox import ClusterComponent

instrument_coordinator = InstrumentCoordinator("instrument_coordinator")
instrument_coordinator.add_component(ic_cluster0 := ClusterComponent(cluster0))

# utility instruments
#############################

meas_ctrl = instrument_coordinator("meas_ctrl")
nested_meas_ctrl = MeasurementControl("nested_meas_ctrl")
# Create the live plotting intrument which handles the graphical interface
# Two windows will be created, the main will feature 1D plots and any 2D plots will go
# to the secondary
# plotmon = pqm.PlotMonitor_pyqt("plotmon")
# nested_plotmon = pqm.PlotMonitor_pyqt("nested_plotmon")
# Connect the live plotting monitor to the measurement control
# meas_ctrl.instr_plotmon(plotmon.name)
# nested_meas_ctrl.instr_plotmon(nested_plotmon.name)
meas_ctrl.attach_plotmon()

# The instrument monitor will give an overview of all parameters of all instruments
# We are not using this, since this is not compatible with the DC biasing with the QCM
# insmon = InstrumentMonitor("insmon")
# By connecting to the MC the parameters will be updated in real-time during an
# experiment.
# meas_ctrl.instrument_monitor(insmon.name)

# Config management instruments
###############################
quantum_device = QuantumDevice(name="quantum_device")
quantum_device.hardware_config(HARDWARE_CFG_TII)
quantum_device.instr_measurement_control(meas_ctrl.name)
quantum_device.instr_nested_measurement_control(nested_meas_ctrl.name)
quantum_device.instr_instrument_coordinator(instrument_coordinator.name)

# Add all the qubit elements to the quantum device
from superconducting_qubit_tools.device_under_test.transmon_element import TransmonElementPurcell
quantum_device.add_element(q0 := BasicTransmonElement("q0"))
quantum_device.add_element(q1 := BasicTransmonElement("q1"))
quantum_device.add_element(q2 := BasicTransmonElement("q2"))
quantum_device.add_element(q3 := BasicTransmonElement("q3"))
quantum_device.add_element(q4 := BasicTransmonElement("q4"))


qubits = [q0, q1, q2, q3, q4]

# Add a feedline element to the quantum device and connect it to the qubits
quantum_device.add_element(feedline := FeedlineElement("f0"))
quantum_device.add_connection(feedline, [qubit.ports.readout() for qubit in qubits])

c01 = TunableCouplerTransmonElement(
    name="c01", 
    parent_element_name="q0", 
    child_element_name="q1"
)
c12 = TunableCouplerTransmonElement(
    name="c12", 
    parent_element_name="q1", 
    child_element_name="q2"
)
c23 = TunableCouplerTransmonElement(
    name="c23", 
    parent_element_name="q2", 
    child_element_name="q3"
)
c34 = TunableCouplerTransmonElement(
    name="c34", 
    parent_element_name="q3", 
    child_element_name="q4"
)



# for qubit in [q0,q1,q2,q3,q4]:
#     quantum_device.add_element(qubit)

print("\n#---------------------------------------------------")
print("# Setting up Qubit Edges....")
print("#---------------------------------------------------")

quantum_device.add_edge(c01)
quantum_device.add_edge(c12)
quantum_device.add_edge(c23)
quantum_device.add_edge(c34)

#coupler params
# c34.default_measure("measure_qubit_rabi")
# c34.readout_element(q4.name)
# print("Coupler readout port:", c34.ports.readout())

# c23.default_measure("measure_qubit_rabi")
# c23.readout_element(q2.name)
# print("Coupler readout port:", c23.ports.readout())

# c12.default_measure("measure_qubit_rabi")
# c12.readout_element(q1.name)
# print("Coupler readout port:", c12.ports.readout())

# c01.default_measure("measure_qubit_rabi")
# c01.readout_element(q0.name)
# print("Coupler readout port:", c01.ports.readout())



# print(f"Qubits Edges are : {c01.name}, {c12.name}")
# Setup DC flux offsets with the QCM

# c34.hardware_options.flux_bias_line.parameter("cluster0.module16.out3_offset")
# c01.hardware_options.flux_bias_line.parameter("cluster0.module16.out0_offset")
# c23.hardware_options.flux_bias_line.parameter("cluster0.module16.out2_offset")
# c12.hardware_options.flux_bias_line.parameter("cluster0.module16.out1_offset")

# c34.hardware_options.flux_bias_line.current(0)
# c01.hardware_options.flux_bias_line.current(0)
# c23.hardware_options.flux_bias_line.current(0)
# c12.hardware_options.flux_bias_line.current(0)

# Ensure ramping is enabled on these parameters for safety
from contextlib import suppress
from quantify_scheduler.instrument_coordinator.utility import search_settable_param

for element in quantum_device.elements():
    with suppress(AttributeError):
        parameter_name = element.hardware_options.flux_bias_line.parameter()
        instrument_name, parameter_path = parameter_name.split(".", maxsplit=1)
        instrument = Instrument.find_instrument(instrument_name)
        parameter = search_settable_param(instrument, parameter_path)
        parameter.inter_delay = 0.05  # [s]
        parameter.step = 0.05  # [V]

print("\n#---------------------------------------------------")
print("# Hardware Configuration completed.")
print("#---------------------------------------------------")
#-------------------------------------------------------------------------------------------------


# Set initial estimates of parameters (palceholder)
q0.clock_freqs.f01(3.7560e9)
q1.clock_freqs.f01(4.2377e9)
q2.clock_freqs.f01(3.8526e9)
q3.clock_freqs.f01(4.1140e9) 
q4.clock_freqs.f01(3.8355e9)

q0.clock_freqs.readout(6.3030e9)
q1.clock_freqs.readout(6.5530e9)
q2.clock_freqs.readout(6.3480e9)
q3.clock_freqs.readout(6.6340e9)
q4.clock_freqs.readout(6.3940e9)


# Calibration Graph
print("\n#---------------------------------------------------")
print("# Generating calibration graph.")
print("#---------------------------------------------------")

graph = generate_calibration_graph(quantum_device)
graph.set_all_node_states("needs calibration")
new_run_id()
register_calibration_graph(graph)

from orangeqs.juice_ext.device_and_instruments.instrument_monitor import InstrumentMonitorPublisher
publisher = InstrumentMonitorPublisher()
publisher.start()

## Initial auto-calibration settings
for qubit in [q0, q1, q2, q3, q4]:
    qubit.spec_mw.reference_magnitude.dBm(-30)