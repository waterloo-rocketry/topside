import topside as top


def create_component(s1v1, s1v2, s2v1, s2v2, name, key):
    pc_states = {
        'open': {
            (1, 2, key + '1'): s1v1,
            (2, 1, key + '2'): s1v2
        },
        'closed': {
            (1, 2, key + '1'): s2v1,
            (2, 1, key + '2'): s2v2
        }
    }
    pc_edges = [(1, 2, key + '1'), (2, 1, key + '2')]
    pc = top.PlumbingComponent(name, pc_states, pc_edges)
    return pc


def two_valve_setup(vAs1_1, vAs1_2, vAs2_1, vAs2_2, vBs1_1, vBs1_2, vBs2_1, vBs2_2):
    pc1 = create_component(vAs1_1, vAs1_2, vAs2_1, vAs2_2, 'valve1', 'A')
    pc2 = create_component(vBs1_1, vBs1_2, vBs2_1, vBs2_2, 'valve2', 'B')

    component_mapping = {
        'valve1': {
            1: 1,
            2: 2
        },
        'valve2': {
            1: 2,
            2: 3
        }
    }

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    return plumb
