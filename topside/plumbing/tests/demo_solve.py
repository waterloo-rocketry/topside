import matplotlib.pyplot as plt

import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def make_plumb():
    """
    The engine that's been set up looks like this:
    +-----+           +-----+           +-----+           +-----+
    |     |  --C-->   |     |  --40->   |     |  --5-->   |     |
    |  1  |           |  2  |           |  3  |           | atm |
    |     |  <-10--   |     |  <-45--   |     |  <-5---   |     |
    +-----+           +-----+           +-----+           +-----+
    100               100                100                 0

    Result annotation:
    - node 1 stays at 100 the entire duration because 1->2 is closed, so no pressure can flow out
        of node 1.

    - node 3's pressure drops much more quickly than node 2's because its teq to atm (5) is much
        lower than the teq in the 2->3 connection (50). Pressure from 3 flows into atm much faster
        than it's replenished by pressure from 2.

    - pressure at atm stays at 0, because pressure at atm is always 0.

    """

    ret = test.two_valve_setup(1, 1, utils.CLOSED, 10, 40, 45, 1, 1)
    comp = test.create_component(5, 5, utils.CLOSED, utils.CLOSED, 'vent', 'A')
    mapping = {
        1: 3,
        2: utils.ATM,
    }
    ret.add_component(comp, mapping, 'open')
    ret.set_pressure(1, 100)
    ret.set_pressure(2, 100)
    return ret


def make_plot(states, time_res, nodes):
    node_pressures = {node: [] for node in nodes}

    t = []
    time = 0

    for state in states:
        t.append(time)
        time += utils.micros_to_s(time_res)

        for node, pres in state.items():
            node_pressures[node].append(pres)

    return t, node_pressures


plumb = make_plumb()

solve_states = plumb.solve(max_time=60, return_resolution=plumb.time_res)

tlist, node_p = make_plot(solve_states, plumb.time_res, plumb.nodes(data=False))

for name, pressures in node_p.items():
    plt.plot(tlist, pressures, label='node ' + str(name))

plt.xlabel('Time (s)')
plt.ylabel('Pressure (Pa)')
plt.suptitle('Pressure Simulation')
plt.grid(color='lightgrey')
plt.xlim(0, tlist[-1])
plt.ylim(-1, 101)

plt.legend()
plt.show()
