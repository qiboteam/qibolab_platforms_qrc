from qibolab import initialize_parameters

from qibolab_platforms_qrc.qpu163.platform import create

hardware = create()
parameters = initialize_parameters(hardware, natives = {'RX', 'RX90', 'RX12', 'MZ'})

str_parameters = parameters.model_dump_json(indent = 4)

with open("parameters.json", "w") as f:
    f.write(str_parameters)
