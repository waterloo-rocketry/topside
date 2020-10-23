import topside as top

import matplotlib.pyplot as plt
import topside.plumbing.plumbing_utils as utils


def make_plumbing_engine(components, mapping, initial_pressures, initial_states):
    """
    makes a new plumbing engine.
    """
    plumb = top.PlumbingEngine()
    plumb.load_graph(components, mapping, initial_pressures, initial_states)
    return plumb

def make_procedures_engine(plumbing_eng, suite):
    """
    makes a new procedures enging.
    """
    procedures_eng = top.ProceduresEngine(plumbing_eng, suite)
    return procedures_eng

def make_plot(pressures, time_res, nodes):
    """
    makes a graph based on the logged time and pressure of each node.
    """
    node_pressures = {node: [] for node in nodes}

    t = []
    time = 0

    for p in pressures:
        t.append(time)
        time += utils.micros_to_s(time_res)

        for node, pres in p.items():
            node_pressures[node].append(pres)

    return t, node_pressures


components = None
mapping = None
pressure = None
states = None

plumb = make_plumbing_engine(components, mapping, pressure, states)

suite = None

procedures_eng = make_procedures_engine(plumb, suite)

all_pressure = []

while procedures_eng.ready_to_advance():
    procedures_eng.next_step()
    procedures_eng.step_time()
    all_pressure.append(procedures_eng._plumb.current_pressures())

tlist, node_plist = make_plot(all_pressure, procedures_eng._plumb.time_res, procedures_eng._plumb.nodes(data=False))

for name, pressure in node_plist.items():
    plt.plot(tlist, pressure, label='node ' + str(name))

plt.xlabel('Time (s)')
plt.ylabel('Pressure (Pa)')
plt.suptitle('Pressure Simulation')
plt.grid(color='lightgrey')
plt.xlim(0, tlist[-1])
plt.ylim(-1, 101)

plt.legend()
plt.show()