import argparse

import topside as top

import matplotlib.pyplot as plt
import topside.plumbing.plumbing_utils as plumbing_utils


# def make_plumbing_engine(components, mapping, initial_pressures, initial_states):
#     plumb = top.PlumbingEngine()
#     plumb.load_graph(components, mapping, initial_pressures, initial_states)
#     return plumb


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
        time += plumbing_utils.micros_to_s(time_res)

        for node, pres in p.items():
            node_pressures[node].append(pres)

    return t, node_pressures


# read file paths from argument input
# first file path: Proclang file path
# second file path: Pdl file path
arg_parser = argparse.ArgumentParser(
    description="A program that simulates a procedure from given plumbing engine and procedure suite.")
arg_parser.add_argument('procPath', type=str)
arg_parser.add_argument('pdlPath', type=str)

args = arg_parser.parse_args()

# parsing file paths and make plumbing engine
plumb_parsed = top.Parser([args.pdlPath])
plumb = plumb_parsed.make_engine()

assert plumb.is_valid()

suite = top.proclang.parse_from_file(args.procPath)

assert suite != None

# construct procedures engine from given plumbing engine
procedures_eng = make_procedures_engine(plumb, suite)

all_pressure = []

# 1. the loop runs until the end of procedure
# 2. check to see if the procedures engine is ready to advance to the next step (ready_to_advance)
# 3. if so, advance one step (next_step)
# 4. step forward in time by a small amount (step_time)
# 5. record the current pressures of the system
# 6. repeat steps 2-5 until we are at the end of the procedure

while len(procedures_eng.current_step.conditions) > 0:
    if procedures_eng.ready_to_advance():
        procedures_eng.next_step()
    procedures_eng.step_time()
    all_pressure.append(procedures_eng._plumb.current_pressures())

tlist, node_plist = make_plot(all_pressure, procedures_eng._plumb.time_res,
                              procedures_eng._plumb.nodes(data=False))

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
