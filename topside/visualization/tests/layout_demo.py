import matplotlib.pyplot as plt

import topside as top


def make_engine():
    states = {
        'static': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        },
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    mapping = {'c1': {1: 'atm', 2: 1},
               'c2': {1: 1, 2: 2},
               'c3': {1: 1, 2: 2},
               'c4': {1: 2, 2: 3},
               'c5': {1: 3, 2: 'atm'},
               'c6': {1: 3, 2: 4},
               'c7': {1: 4, 2: 5},
               'c8': {1: 4, 2: 5},
               'c9': {1: 5, 2: 6},
               'c10': {1: 6, 2: 'atm'},
               'c11': {1: 6, 2: 'atm'},
               'c12': {1: 6, 2: 'atm'},}
    
    pressures = {}
    for k1, v1 in mapping.items():
        for k2, v2 in v1.items():
            pressures[v2] = 0

    component_dict = {k: top.PlumbingComponent(k, states, edges) for k in mapping.keys()}
    initial_states = {k: 'static' for k in mapping.keys()}

    return top.PlumbingEngine(component_dict, mapping, pressures, initial_states)


fig, ax = top.layout_and_plot_plumbing_engine(make_engine())
plt.show()
