import argparse

import matplotlib.pyplot as plt

import topside as top


def generate_graph_data(pressures, time_res, nodes):
    """
    Generate the data needed for graphing the pressure.

    Parameters
    ----------

    pressures:
        all pressures logged while running the procedures.

    time_res:
        time interval for the plumbing engine.

    nodes:
        all nodes in the plumbing engine.
    """
    node_pressures = {node: [] for node in nodes}
    t = []
    time = 0

    for p in pressures:
        t.append(time)
        time += top.micros_to_s(time_res)

        for node, pres in p.items():
            node_pressures[node].append(pres)

    return t, node_pressures


arg_parser = argparse.ArgumentParser(
    description="A program that simulates a procedure from given plumbing engine and procedure suite.")
arg_parser.add_argument('proc_path', type=str, help='Path to the procLang file')
arg_parser.add_argument('pdl_path', type=str, help='Path to the pdl file')
arg_parser.add_argument('max_time', type=int, help='max time allowed for the simulation in seconds')

args = arg_parser.parse_args()

plumb_parsed = top.Parser([args.pdl_path])
plumb = plumb_parsed.make_engine()

assert plumb.is_valid()
suite = top.proclang.parse_from_file(args.proc_path)
assert suite is not None
procedures_eng = top.ProceduresEngine(plumb, suite)

all_pressure = []

while len(procedures_eng.current_step.conditions) > 0 and plumb.time < top.s_to_micros(args.max_time):
    if procedures_eng.ready_to_advance():
        procedures_eng.next_step()
    procedures_eng.step_time()
    all_pressure.append(plumb.current_pressures())

tlist, node_plist = generate_graph_data(all_pressure, plumb.time_res,
                                        plumb.nodes(data=False))

for name, pressure in node_plist.items():
    plt.plot(tlist, pressure, label='node ' + str(name))

plt.xlabel('Time (s)')
plt.ylabel('Pressure (psi)')
plt.suptitle('Procedure Simulation')
plt.grid(color='lightgrey')
plt.xlim(0, tlist[-1])

plt.legend()
plt.show()
